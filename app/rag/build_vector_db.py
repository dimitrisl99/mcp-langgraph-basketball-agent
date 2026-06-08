import json
import shutil
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "basketball_playbooks"


def load_chunks(chunks_path: Path) -> list[dict]:
    """
    Loads semantic chunks from JSON.
    """
    with chunks_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def prepare_documents(chunks: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    """
    Prepares documents, ids, and metadata for Chroma.
    """
    documents = []
    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        text = chunk["text"].strip()

        if len(text) < 50: #φιλτράρει πολύ μικρά chunks
            continue

        documents.append(text)

        ids.append(
            f"{chunk['source']}_page_{chunk['page']}_chunk_{chunk['chunk_index']}_{index}" #κάθε chunk πρέπει να έχει unique id
        )

        #κρατάει metadata
        metadatas.append(
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "chunking_method": chunk["chunking_method"],
                "extraction_method": chunk["extraction_method"],
            }
        )

    return documents, ids, metadatas


def build_chroma_index(
    documents: list[str],
    ids: list[str],
    metadatas: list[dict],
    chroma_path: Path,
) -> None:
    """
    Builds a persistent Chroma vector database.
    """
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    embeddings = model.encode(
        documents,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    client = chromadb.PersistentClient(path=str(chroma_path))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"embedding_model": EMBEDDING_MODEL_NAME},
    )

    collection.add(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids,
    )

    print(f"Stored documents in Chroma: {collection.count()}")


if __name__ == "__main__":
    project_root = Path(__file__).parents[2]

    chunks_path = project_root / "data" / "processed" / "semantic_chunks.json" #παίρνει τα chunks που φτιάξαμε
    #απο OCR + semantic chunking

    chroma_path = project_root / "data" / "chroma"

    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    chunks = load_chunks(chunks_path)

    documents, ids, metadatas = prepare_documents(chunks)

    print(f"Loaded chunks: {len(chunks)}")
    print(f"Documents to index: {len(documents)}")

    build_chroma_index(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
        chroma_path=chroma_path,
    )

    print(f"Chroma DB saved to: {chroma_path}")