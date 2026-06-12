"""
Έχουμε 3 nodes:
i) Router
ii) Rag
iii) SQL

Ο Router αποφασίζει αν η ερώτηση είναι RAG ή SQL
π.χ. αν η ερώτηση είναι How does Spain Pick and Roll work? --> RAG
ενώ αν είναι Who are the top 5 players by assists? --> SQL
"""

from typing import TypedDict, Literal

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
    question = state["question"]
    chat_history = state["chat_history"]

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

    return state


def route_question(state: AgentState) -> AgentState:
    question = state["standalone_question"]

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

    return state


def rag_node(state: AgentState) -> AgentState:
    question = state["standalone_question"]

    answer = call_mcp_tool(
        tool_name="answer_basketball_question",
        arguments={
            "question": question,
            "top_k": 5,
        },
    )

    state["route"] = "RAG"
    state["answer"] = answer

    return state


def sql_node(state: AgentState) -> AgentState:
    question = state["standalone_question"]

    answer = call_mcp_tool(
        tool_name="answer_nba_stats_question",
        arguments={
            "question": question,
        },
    )

    state["route"] = "SQL"
    state["answer"] = answer

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
    app = build_graph()

    if chat_history is None:
        chat_history = []

    initial_state = {
        "question": question,
        "standalone_question": "",
        "chat_history": chat_history,
        "route": "",
        "answer": "",
    }

    final_state = app.invoke(initial_state)

    return {
        "question": question,
        "standalone_question": final_state["standalone_question"],
        "route": final_state["route"],
        "answer": final_state["answer"],
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