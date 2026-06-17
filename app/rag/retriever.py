from pathlib import Path

import chromadb
import time
import sys

from app.rag.reranker import rerank_results
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "basketball_playbooks"

#global μεταβλητές cache
_embedding_model = None
_chroma_collection = None

def get_project_root() -> Path:
    return Path(__file__).parents[2]


def load_embedding_model() -> SentenceTransformer:
    """
    Loads the embedding model only once per Python process.
    """
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _embedding_model



def get_chroma_collection():
    """
    Loads the Chroma collection only once per Python process.
    """
    global _chroma_collection

    if _chroma_collection is None:

        project_root = get_project_root()
        chroma_path = project_root / "data" / "chroma"

        client = chromadb.PersistentClient(path=str(chroma_path))

        _chroma_collection = client.get_collection(
            name=COLLECTION_NAME
        )

    return _chroma_collection


def format_results(results: dict) -> list[dict]:
    """
    Converts raw Chroma results into a cleaner list of dictionaries.
    """
    formatted = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        formatted.append(
            {
                "text": document,
                "source": metadata["source"],
                "page": metadata["page"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return formatted


def search_playbooks(query: str, top_k: int = 5) -> list[dict]:
    """
    Searches basketball playbook chunks using semantic similarity.
    """

    t0 = time.perf_counter()

    model = load_embedding_model()

    print(
        f"[TIMING] load_embedding_model: "
        f"{time.perf_counter() - t0:.3f}s",
        file=sys.stderr,
    )

    t1 = time.perf_counter()

    collection = get_chroma_collection()

    print(
        f"[TIMING] get_chroma_collection: "
        f"{time.perf_counter() - t1:.3f}s",
        file=sys.stderr,
    )

    t2 = time.perf_counter()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    print(
        f"[TIMING] embedding_query: "
        f"{time.perf_counter() - t2:.3f}s",
        file=sys.stderr,
    )

    t3 = time.perf_counter()

    candidate_k = max(top_k * 4, 20)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=candidate_k,
    )

    print(
        f"[TIMING] chroma_query: "
        f"{time.perf_counter() - t3:.3f}s",
        file=sys.stderr,
    )

    formatted_results = format_results(results)

    t4 = time.perf_counter()

    reranked_results = rerank_results(
        query=query,
        results=formatted_results,
        top_k=top_k,
    )

    print(
        f"[TIMING] rerank_results: "
        f"{time.perf_counter() - t4:.3f}s",
        file=sys.stderr,
    )

    return reranked_results



if __name__ == "__main__":
    queries = [
        "How does Spain Pick and Roll work?",
        "What are the advantages of Spain Pick and Roll?",
    ]

    for query in queries:
        results = search_playbooks(query, top_k=5)

        print(f"\nQuery: {query}")
        print("\nTop results:")

        for index, result in enumerate(results, start=1):
            print(f"\n--- RESULT {index} ---")
            print(f"Source: {result['source']}")
            print(f"Page: {result['page']}")
            print(f"Chunk: {result['chunk_index']}")
            print(f"Distance: {result['distance']}")
            print(result["text"][:800])

"""
Η τελευταία αλλαγή ουσιαστικά είναι οτι απο εκεί που το σύστημα πριν λειτουργούσε έτσι: 
search_playbooks() --> load model --> load Chroma --> search 

Τώρα ουσιαστικά γίνεται: 
first search_playbooks() --> load model once --> load Chroma once --> search 
second search_playbooks() --> reuse same model --> reuse same Chroma collection --> search 

H ουσιαστική αλλαγή είναι οτι τώρα φορτώνει το model και την chroma μόνο μία φορά 
"""


