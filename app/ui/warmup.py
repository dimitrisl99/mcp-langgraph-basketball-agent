import time
import ollama

from app.graph.mcp_client import get_mcp_client, call_mcp_tool


OLLAMA_MODEL = "qwen3:8b"


def warmup_system() -> dict:
    timings = {}

    start = time.perf_counter()
    get_mcp_client().start()
    timings["mcp_client_start"] = round(time.perf_counter() - start, 3)

    start = time.perf_counter()
    call_mcp_tool(
        tool_name="search_basketball_playbooks",
        arguments={
            "query": "Spain Pick and Roll",
            "top_k": 1,
        },
    )
    timings["mcp_retriever_warmup"] = round(time.perf_counter() - start, 3)

    start = time.perf_counter()
    ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Reply with only: ready",
            }
        ],
    )
    timings["ollama_warmup"] = round(time.perf_counter() - start, 3)

    return timings