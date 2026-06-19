from rank_bm25 import BM25Okapi

import chromadb
from pathlib import Path

COLLECTION_NAME = "basketball_playbooks"
_chroma_collection = None


def get_project_root() -> Path:
    return Path(__file__).parents[2]


def get_chroma_collection():
    global _chroma_collection

    if _chroma_collection is None:
        project_root = get_project_root()
        chroma_path = project_root / "data" / "chroma"

        client = chromadb.PersistentClient(path=str(chroma_path))

        _chroma_collection = client.get_collection(
            name=COLLECTION_NAME
        )

    return _chroma_collection


_bm25_index = None
_bm25_documents = None
_bm25_metadatas = None


def simple_tokenize(text: str) -> list[str]:
    """
    Simple BM25 tokenizer.
    """

    return text.lower().split()


def load_bm25_index():
    """
    Builds the BM25 index only once per Python process.
    """

    global _bm25_index
    global _bm25_documents
    global _bm25_metadatas

    if _bm25_index is not None:
        return (
            _bm25_index,
            _bm25_documents,
            _bm25_metadatas,
        )

    collection = get_chroma_collection()

    data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    documents = data["documents"]
    metadatas = data["metadatas"]

    tokenized_documents = [
        simple_tokenize(document)
        for document in documents
    ]

    _bm25_index = BM25Okapi(
        tokenized_documents
    )

    _bm25_documents = documents
    _bm25_metadatas = metadatas

    return (
        _bm25_index,
        _bm25_documents,
        _bm25_metadatas,
    )


def search_bm25(
    query: str,
    top_k: int = 20,
) -> list[dict]:
    """
    Searches documents using BM25 keyword retrieval.
    """

    bm25_index, documents, metadatas = load_bm25_index()

    tokenized_query = simple_tokenize(query)

    scores = bm25_index.get_scores(
        tokenized_query
    )

    top_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )[:top_k]

    results = []

    for index in top_indices:

        metadata = metadatas[index]

        results.append(
            {
                "text": documents[index],
                "source": metadata["source"],
                "page": metadata["page"],
                "chunk_index": metadata["chunk_index"],
                "distance": None,
                "bm25_score": float(scores[index]),
            }
        )

    return results