from sentence_transformers import CrossEncoder


RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker_model = None


def load_reranker_model() -> CrossEncoder:
    """
    Loads the cross-encoder reranker only once per Python process.
    """

    global _reranker_model

    if _reranker_model is None:
        _reranker_model = CrossEncoder(RERANKER_MODEL_NAME)

    return _reranker_model


def rerank_results(
    query: str,
    results: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Reranks retrieved chunks using a cross-encoder.

    The retriever first returns candidate chunks.
    The reranker then scores each query-chunk pair more accurately.
    """

    if not results:
        return []

    reranker = load_reranker_model()

    pairs = [
        [query, result["text"]]
        for result in results
    ]

    scores = reranker.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):
        result_with_score = result.copy()
        result_with_score["rerank_score"] = float(score)
        reranked_results.append(result_with_score)

    reranked_results = sorted(
        reranked_results,
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return reranked_results[:top_k]