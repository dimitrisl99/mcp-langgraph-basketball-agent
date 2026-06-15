import ollama
import time
from app.rag.retriever import search_playbooks
from pathlib import Path

OLLAMA_MODEL = "qwen3:8b"


def format_context(results: list[dict]) -> str:
    """
    Converts retrieved chunks into a clean context block for the LLM.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"[Source {index}]\n"
            f"File: {result['source']}\n"
            f"Page: {result['page']}\n"
            f"Text:\n{result['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


def generate_basketball_answer(question: str, top_k: int = 5) -> dict:
    """
    Retrieves relevant playbook chunks and asks a local Ollama model
    to generate a grounded basketball coaching answer.
    """

    total_start_time = time.perf_counter()
    rag_timings = {}

    retrieval_start_time = time.perf_counter()

    retrieved_results = search_playbooks(
        query=question,
        top_k=top_k,
    )

    rag_timings["retrieval"] = round(
        time.perf_counter() - retrieval_start_time,
        3
    )

    if not retrieved_results:
        return {
            "answer": "I could not find relevant information in the basketball playbooks.",
            "sources": [],
            "rag_timings": rag_timings,
        }

    context_start_time = time.perf_counter()

    context = format_context(retrieved_results)

    rag_timings["context_building"] = round(
        time.perf_counter() - context_start_time,
        3
    )

    prompt = f"""
You are a basketball coaching assistant.

Answer the user's question using ONLY the provided playbook context.
If the context is not enough, say that the available playbooks do not provide enough evidence.

Write clearly and practically, as if explaining to a coach or player.
Do NOT include source references inside the answer text.
The source list will be displayed separately by the UI.

User question:
{question}

Playbook context:
{context}

Answer:
"""

    generation_start_time = time.perf_counter()

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    rag_timings["ollama_generation"] = round(
        time.perf_counter() - generation_start_time,
        3
    )

    answer = response["message"]["content"]

    sources_start_time = time.perf_counter()

    project_root = Path(__file__).parents[2]
    playbooks_dir = project_root / "data" / "playbooks"

    sources = []

    for index, result in enumerate(retrieved_results, start=1):
        pdf_path = playbooks_dir / result["source"]

        sources.append(
            {
                "label": f"Source {index}",
                "file": result["source"],
                "page": result["page"],
                "chunk_index": result["chunk_index"],
                "text": result["text"],
                "file_path": str(pdf_path),
            }
        )

    rag_timings["sources_building"] = round(
        time.perf_counter() - sources_start_time,
        3
    )

    rag_timings["total_rag_answer"] = round(
        time.perf_counter() - total_start_time,
        3
    )

    return {
        "answer": answer,
        "sources": sources,
        "rag_timings": rag_timings,
    }


if __name__ == "__main__":
    question = "How does Spain Pick and Roll work?"

    answer = generate_basketball_answer(question, top_k=5)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)