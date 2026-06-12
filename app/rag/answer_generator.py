import ollama

from app.rag.retriever import search_playbooks


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


def generate_basketball_answer(question: str, top_k: int = 5) -> str:
    """
    Retrieves relevant playbook chunks and asks a local Ollama model
    to generate a grounded basketball coaching answer.
    """

    retrieved_results = search_playbooks(
        query=question,
        top_k=top_k,
    )

    if not retrieved_results:
        return "I could not find relevant information in the basketball playbooks."

    context = format_context(retrieved_results)

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

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    answer = response["message"]["content"]

    sources = []

    for index, result in enumerate(retrieved_results, start=1):
        sources.append(
            {
                "label": f"Source {index}",
                "file": result["source"],
                "page": result["page"],
                "chunk_index": result["chunk_index"],
                "text": result["text"],
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    question = "How does Spain Pick and Roll work?"

    answer = generate_basketball_answer(question, top_k=5)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)