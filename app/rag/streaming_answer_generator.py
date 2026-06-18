import time
from pathlib import Path
from typing import Iterator

import ollama

from app.rag.retriever import search_playbooks
from app.rag.answer_generator import format_context


OLLAMA_MODEL = "qwen3:8b"


def prepare_streaming_rag_answer(question: str, top_k: int = 5) -> dict:
    total_start_time = time.perf_counter()
    rag_timings = {}

    retrieval_start = time.perf_counter()

    retrieved_results = search_playbooks(
        query=question,
        top_k=top_k,
    )

    rag_timings["retrieval"] = round(
        time.perf_counter() - retrieval_start,
        3,
    )

    context_start = time.perf_counter()

    context = format_context(retrieved_results)

    rag_timings["context_building"] = round(
        time.perf_counter() - context_start,
        3,
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

    rag_timings["total_prepare_rag"] = round(
        time.perf_counter() - total_start_time,
        3,
    )

    return {
        "prompt": prompt,
        "sources": sources,
        "rag_timings": rag_timings,
    }


def stream_ollama_answer(prompt: str) -> Iterator[str]:
    stream = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=True,
    )

    for chunk in stream:
        token = chunk["message"]["content"]

        if token:
            yield token