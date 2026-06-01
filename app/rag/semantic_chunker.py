import json  # για να διαβάζουμε/γράφουμε JSON αρχεία
import re  # για καθάρισμα κειμένου
from pathlib import Path

from sentence_transformers import SentenceTransformer  # μετατρέπει προτάσεις σε embeddings/διανύσματα
from sklearn.metrics.pairwise import cosine_similarity  # μετράει πόσο κοντά είναι νοηματικά 2 προτάσεις


def clean_text(text: str) -> str:
    """
    Καθαρίζει το OCR text από περιττά κενά και περίεργες αλλαγές γραμμών.
    """
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    """
    Σπάει το κείμενο σε μικρές νοηματικές μονάδες.
    Για OCR playbooks κρατάμε και line-based λογική, γιατί συχνά οι προτάσεις δεν είναι τέλειες.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sentences = []

    for line in lines:
        parts = re.split(r"(?<=[.!?])\s+", line)

        for part in parts:
            part = part.strip()

            if len(part) >= 25:
                sentences.append(part)

    return sentences


def semantic_chunk_document(
    document: dict,
    model: SentenceTransformer,
    similarity_threshold: float = 0.45,
    min_chunk_chars: int = 250,
    max_chunk_chars: int = 1200,
) -> list[dict]:
    """
    Κάνει semantic chunking σε μία σελίδα/document.

    Λογική:
    1. Καθαρίζει το OCR text.
    2. Το σπάει σε προτάσεις/μονάδες.
    3. Φτιάχνει embeddings για κάθε πρόταση.
    4. Συγκρίνει κάθε πρόταση με την προηγούμενη.
    5. Αν μοιάζουν νοηματικά, τις βάζει στο ίδιο chunk.
    6. Αν αλλάζει το νόημα ή μεγαλώνει πολύ το chunk, ξεκινά νέο chunk.
    7. Ενώνει πολύ μικρά chunks με το προηγούμενο.
    """

    text = clean_text(document["text"])
    sentences = split_into_sentences(text)

    if not sentences:
        return []

    embeddings = model.encode(sentences)

    chunks = []
    current_chunk_sentences = [sentences[0]]

    # Σύγκριση κάθε πρότασης με την προηγούμενη
    for i in range(1, len(sentences)):
        previous_embedding = embeddings[i - 1].reshape(1, -1)
        current_embedding = embeddings[i].reshape(1, -1)

        similarity = cosine_similarity(
            previous_embedding,
            current_embedding,
        )[0][0]

        current_chunk_text = " ".join(current_chunk_sentences)

        if (
            similarity >= similarity_threshold
            and len(current_chunk_text) + len(sentences[i]) <= max_chunk_chars
        ):
            current_chunk_sentences.append(sentences[i])
        else:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    # Ενώνουμε πολύ μικρά chunks με το προηγούμενο, για να μη μένουν μόνα τους άχρηστα fragments
    merged_chunks = []

    for chunk in chunks:
        if not merged_chunks:
            merged_chunks.append(chunk)

        elif len(chunk) < min_chunk_chars:
            merged_chunks[-1] = merged_chunks[-1] + " " + chunk

        else:
            merged_chunks.append(chunk)

    chunks = merged_chunks

    chunk_records = []

    for index, chunk_text in enumerate(chunks):
        chunk_records.append(
            {
                "text": chunk_text,
                "source": document["source"],
                "page": document["page"],
                "extraction_method": document["extraction_method"],
                "chunk_index": index,
                "chunking_method": "semantic",
            }
        )

    return chunk_records


def semantic_chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Κάνει semantic chunking σε όλα τα OCR documents.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")

    all_chunks = []

    for document in documents:
        chunks = semantic_chunk_document(document, model)
        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    project_root = Path(__file__).parents[2]

    input_path = project_root / "data" / "processed" / "ocr_documents.json"
    output_path = project_root / "data" / "processed" / "semantic_chunks.json"

    with input_path.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    chunks = semantic_chunk_documents(documents)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Loaded documents: {len(documents)}")
    print(f"Created semantic chunks: {len(chunks)}")
    print(f"Saved to: {output_path}")

    print("\nSample chunks:")

    for i in [0, 10, 50, 100, 200]:
        if i < len(chunks):
            print(f"\n--- CHUNK {i} ---")
            print(f"Source: {chunks[i]['source']}")
            print(f"Page: {chunks[i]['page']}")
            print(chunks[i]["text"][:800])