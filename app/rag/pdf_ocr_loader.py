from pathlib import Path

import fitz  # PyMuPDF
import easyocr # OCR engine
import numpy as np # Το EasyOCR θέλει numpy arrays
import json # για την αποθήκευση
from PIL import Image # Για να μετατρέψουμε PDF pages σε PIL images

#πάρε μια pdf σελίδα και κάνε την εικόνα
def render_page_to_image(page, zoom: float = 3.0) -> Image.Image:
    """
    Converts a PDF page into a PIL image.
    OCR works on images, not directly on PDF pages.
    So first we render each PDF page as an image.
    """
    #Το zoom είναι η ανάλυση zoom=1 χαμηλή ανάλυση, 2 καλύτερη ποιότητα, 3 ακόμα καλύτερη)
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix) #εδώ γίνεται το render PDF page --> Image

    #μετατρέπουμε το pixmap σε PIL Image
    image = Image.frombytes(
        "RGB",
        [pixmap.width, pixmap.height],
        pixmap.samples
    )

    return image

#παίρνει reader(EasyOCR model) + image
def ocr_image(reader: easyocr.Reader, image: Image.Image) -> str:
    """
    Runs OCR on a PIL image and returns extracted text.
    """

    image_array = np.array(image) #μετατρέπει το PIL image --> Numpy Array

    # SOS γραμμή --> εδώ γινεται το OCR
    results = reader.readtext(
        image_array,
        detail=0, #σημαίνει δεν θέλω coordinates, bounding boxes, αλλά μόνο κείμενο)
        paragraph=True #ζητάμε να ενώσει γραμμές σε παραγράφους
    )

    text = "\n".join(results)

    return text.strip()


#Ανοίγει όλοκληρο το pdf
def load_pdf_with_ocr(pdf_path: Path, reader: easyocr.Reader) -> list[dict]:
    """
    Loads one PDF and extracts text from every page using OCR.

    Returns a list of dictionaries.
    Each dictionary represents one PDF page.
    """

    documents = []

    pdf_document = fitz.open(pdf_path) #άνοιγμα pdf

    for page_index in range(len(pdf_document)): #για κάθε σελίδα, την κάνουμε εικόνα και μετά κείμενο
        page = pdf_document[page_index]

        image = render_page_to_image(page)
        text = ocr_image(reader, image)

        #εδώ αποθηκεύουμε το αποτέλεσμα
        documents.append(
            {
                "text": text,
                "source": pdf_path.name,
                "page": page_index + 1,
                "extraction_method": "ocr",
            }
        )

        print(f"OCR done: {pdf_path.name} | page {page_index + 1}")

    pdf_document.close()

    return documents


def load_playbooks_with_ocr(playbooks_dir: Path) -> list[dict]:
    """
    Loads all PDFs from the playbooks folder using OCR.
    Skips PDFs that already exist in data/processed/ocr_documents.json.
    """

    project_root = Path(__file__).parents[2]
    processed_dir = project_root / "data" / "processed"
    output_path = processed_dir / "ocr_documents.json"

    existing_documents = []

    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_documents = json.load(f)

    already_processed_sources = {
        document["source"]
        for document in existing_documents
    }

    reader = easyocr.Reader(["en"], gpu=True)

    all_documents = existing_documents.copy()

    pdf_files = sorted(playbooks_dir.glob("*.pdf"))

    for pdf_path in pdf_files:

        if pdf_path.name in already_processed_sources:
            print(f"Skipping already processed PDF: {pdf_path.name}")
            continue

        print(f"\nProcessing new PDF: {pdf_path.name}")

        pdf_documents = load_pdf_with_ocr(pdf_path, reader)
        all_documents.extend(pdf_documents)

    return all_documents


if __name__ == "__main__":
    project_root = Path(__file__).parents[2]
    playbooks_dir = project_root / "data" / "playbooks"

    documents = load_playbooks_with_ocr(playbooks_dir)

    #αποθήκευση
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_path = processed_dir / "ocr_documents.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"\nSaved OCR documents to: {output_path}")

    print("\nTotal pages extracted:", len(documents))

    if documents:
        print("\nSample document:")
        print("\n========== SAMPLE PAGES ==========\n")

        for i in [0, 5, 10, 20]:
            if i < len(documents):
                print(f"\n--- DOCUMENT {i} ---")
                print(f"Source: {documents[i]['source']}")
                print(f"Page: {documents[i]['page']}")
                print(documents[i]['text'][:1000])