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

from app.rag.answer_generator import generate_basketball_answer
from app.sql.text_to_sql import answer_sql_question


OLLAMA_MODEL = "qwen3:8b"


class AgentState(TypedDict):
    question: str
    route: str
    answer: str


def route_question(state: AgentState) -> AgentState:
    question = state["question"]

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
        messages=[{"role": "user", "content": prompt}],
    )

    route = response["message"]["content"].strip().upper()

    if "SQL" in route:
        state["route"] = "SQL"
    else:
        state["route"] = "RAG"

    return state


def rag_node(state: AgentState) -> AgentState:
    question = state["question"]

    answer = generate_basketball_answer(
        question=question,
        top_k=5,
    )

    state["answer"] = answer
    return state


def sql_node(state: AgentState) -> AgentState:
    question = state["question"]

    answer = answer_sql_question(question)

    state["answer"] = answer
    return state


def choose_route(state: AgentState) -> Literal["rag", "sql"]:
    if state["route"] == "SQL":
        return "sql"

    return "rag"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", route_question)
    graph.add_node("rag", rag_node)
    graph.add_node("sql", sql_node)

    graph.set_entry_point("router")

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


def run_agent(question: str) -> str:
    app = build_graph()

    initial_state = {
        "question": question,
        "route": "",
        "answer": "",
    }

    final_state = app.invoke(initial_state)

    return final_state["answer"]


if __name__ == "__main__":
    questions = [
        "How does Spain Pick and Roll work?",
        "Who are the top 5 players by assists?",
    ]

    for question in questions:
        print("\n==============================")
        print("Question:", question)
        print("==============================")

        answer = run_agent(question)

        print(answer)