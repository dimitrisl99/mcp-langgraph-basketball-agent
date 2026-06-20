"""
We have 3 nodes:
i) Router
ii) Rag
iii) SQL
Router decides if questions is RAG or SQL
e.g. if the Q is "How does Spain Pick and Roll work?" --> Rag
or if the Q is "Who are the top 5 players by assists?" --> SQL
"""

from typing import TypedDict, Literal
import time
import ollama
from langgraph.graph import StateGraph, END

from app.graph.mcp_client import call_mcp_tool


OLLAMA_MODEL = "qwen3:8b"


class AgentState(TypedDict):
    question: str
    standalone_question: str
    chat_history: list[dict]
    route: str
    answer: str
    sources: list[dict]
    timings: dict

def record_timing(state: AgentState, step_name: str, start_time: float) -> None:
    elapsed = time.perf_counter() - start_time
    state["timings"][step_name] = round(elapsed, 3)

def format_chat_history(chat_history: list[dict]) -> str:
    if not chat_history:
        return "No previous conversation."

    formatted_messages = []

    for message in chat_history:
        role = message["role"]
        content = message["content"]

        formatted_messages.append(
            f"{role.upper()}: {content}"
        )

    return "\n".join(formatted_messages)


def rewrite_question(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    question = state["question"]
    chat_history = state["chat_history"]

    if not chat_history:
        state["standalone_question"] = question
        record_timing(state, "rewrite_question", start_time)
        return state

    history_text = format_chat_history(chat_history)

    prompt = f"""
You are a question rewriting assistant.

Your task is to rewrite the user's latest question into a standalone question.

Use the conversation history only if the latest question depends on previous context.

Rules:
- If the question is already standalone, return it unchanged.
- If the question contains references like "it", "that", "this system", "these players", "his stats", resolve them using the chat history.
- Return only the rewritten standalone question.
- Do not answer the question.

Conversation history:
{history_text}

Latest question:
{question}

Standalone question:
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    standalone_question = response["message"]["content"].strip()

    state["standalone_question"] = standalone_question

    record_timing(state, "rewrite_question", start_time)

    return state


SQL_KEYWORDS = [
    "point", "points", "pts",
    "assist", "assists", "ast",
    "rebound", "rebounds", "reb",
    "steal", "steals", "stl",
    "block", "blocks", "blk",
    "turnover", "turnovers", "tov",
    "field goal", "fg%",
    "three point", "3 point", "3-point", "three-point", "fg3",
    "free throw", "ft%",
    "percentage", "percent",
    "top", "leader", "leaders",
    "average", "averages",
    "stats", "statistics",
    "player", "players",
    "team", "teams",
]

RAG_KEYWORDS = [
    "play", "plays",
    "offense", "offence",
    "defense", "defence",
    "system", "systems",
    "pick and roll", "pnr",
    "spain", "flex",
    "motion", "5-out", "5 out",
    "screen", "screens",
    "cut", "cuts",
    "spacing",
    "set", "sets",
    "scheme", "concept",
    "coach", "coaching",
    "explain", "how does", "what is",
]

def rule_based_route(question: str) -> str | None:
    question_lower = question.lower()

    sql_score = sum(
        1 for keyword in SQL_KEYWORDS
        if keyword in question_lower
    )

    rag_score = sum(
        1 for keyword in RAG_KEYWORDS
        if keyword in question_lower
    )

    if sql_score > 0 and rag_score == 0:
        return "SQL"

    if rag_score > 0 and sql_score == 0:
        return "RAG"

    if sql_score >= 2 and sql_score > rag_score:
        return "SQL"

    if rag_score >= 2 and rag_score > sql_score:
        return "RAG"

    return None

def route_question(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    question = state["standalone_question"]

    rule_route = rule_based_route(question)

    if rule_route:
        state["route"] = rule_route
        record_timing(state, "route_question", start_time)
        state["timings"]["router_method"] = f"rule_based_{rule_route.lower()}"
        return state

    prompt = f"""
You are a routing assistant.

Classify the user's basketball question into exactly one category:

RAG:
Questions about basketball systems, plays, tactics, coaching concepts, offensive schemes, defensive schemes, pick and roll concepts, playbook explanations.

SQL:
Questions about NBA player statistics, points, rebounds, assists, steals, blocks, turnovers, shooting percentages, rankings, leaders, teams, or numeric comparisons.

Return only one word:
RAG or SQL

Question:
{question}
"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    route = response["message"]["content"].strip().upper()

    if "SQL" in route:
        state["route"] = "SQL"
    else:
        state["route"] = "RAG"

    record_timing(state, "route_question", start_time)

    state["timings"]["router_method"] = "llm_fallback"

    return state


def rag_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    question = state["standalone_question"]

    result = call_mcp_tool(
        tool_name="answer_basketball_question",
        arguments={
            "question": question,
            "top_k": 5,
        },
    )

    state["route"] = "RAG"

    if isinstance(result, dict):
        state["answer"] = result["answer"]
        state["sources"] = result.get("sources", [])

        rag_timings = result.get("rag_timings", {})

        for step, value in rag_timings.items():
            state["timings"][f"rag_{step}"] = value
    else:
        state["answer"] = result
        state["sources"] = []

    record_timing(state, "rag_mcp_tool", start_time)

    return state


def sql_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()
    question = state["standalone_question"]
    state["sources"] = []

    answer = call_mcp_tool(
        tool_name="answer_nba_stats_question",
        arguments={
            "question": question,
        },
    )

    state["route"] = "SQL"
    state["answer"] = answer

    record_timing(state, "sql_mcp_tool", start_time)

    return state


def choose_route(state: AgentState) -> Literal["rag", "sql"]:
    if state["route"] == "SQL":
        return "sql"

    return "rag"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("rewrite_question", rewrite_question)
    graph.add_node("router", route_question)
    graph.add_node("rag", rag_node)
    graph.add_node("sql", sql_node)

    graph.set_entry_point("rewrite_question")

    graph.add_edge("rewrite_question", "router")

    graph.add_conditional_edges(
        "router",
        choose_route,
        {
            "rag": "rag",
            "sql": "sql",
        },
    )

    graph.add_edge("rag", END)
    graph.add_edge("sql", END)

    return graph.compile()


def run_agent(
    question: str,
    chat_history: list[dict] | None = None,
) -> dict:
    total_start_time = time.perf_counter()
    app = build_graph()

    if chat_history is None:
        chat_history = []

    initial_state = {
        "question": question,
        "standalone_question": "",
        "chat_history": chat_history,
        "route": "",
        "answer": "",
        "sources": [],
        "timings": {},
    }

    final_state = app.invoke(initial_state)

    final_state["timings"]["total_agent_time"] = round(
        time.perf_counter() - total_start_time,
        3
    )

    return {
        "question": question,
        "standalone_question": final_state["standalone_question"],
        "route": final_state["route"],
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "timings": final_state["timings"],
    }

def prepare_agent_request(
    question: str,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    Runs only rewrite + router.
    Used by the UI before streaming the final answer.
    """

    if chat_history is None:
        chat_history = []

    state = {
        "question": question,
        "standalone_question": "",
        "chat_history": chat_history,
        "route": "",
        "answer": "",
        "sources": [],
        "timings": {},
    }

    state = rewrite_question(state)
    state = route_question(state)

    return {
        "question": question,
        "standalone_question": state["standalone_question"],
        "route": state["route"],
        "timings": state["timings"],
    }

if __name__ == "__main__":
    chat_history = []

    questions = [
        "How does Spain Pick and Roll work?",
        "What are its advantages?",
        "Who are the top 5 players by assists?",
        "What about points?",
    ]

    for question in questions:
        print("\n========================================================")
        print("Question:", question)
        print("==========================================================")

        result = run_agent(
            question=question,
            chat_history=chat_history,
        )


        print("Standalone question:", result["standalone_question"])
        print("Route:", result["route"])
        print("\nAnswer:")
        print(result["answer"])

        chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        chat_history.append(
            {
                "role": "assistant",
                "content": result["answer"],
            }
        )