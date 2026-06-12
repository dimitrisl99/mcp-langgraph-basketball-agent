from pathlib import Path

import chromadb
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

    model = load_embedding_model()
    collection = get_chroma_collection()

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
    )

    return format_results(results)

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


