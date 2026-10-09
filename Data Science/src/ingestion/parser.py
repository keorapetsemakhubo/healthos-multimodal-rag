import os
from typing import List, Dict, Any
import fitz  # PyMuPDF (No Poppler required)
import pdfplumber

class PDFMultimodalIngestor:
    """Extracts text, structured tables, and page snapshot images from PDF files using PyMuPDF."""

    def __init__(self, output_dir: str = "data/processed_pages"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

        chunks = []
        doc_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        # 1. Open PDF with PyMuPDF to render page snapshot images
        fitz_doc = fitz.open(pdf_path)

        # 2. Open PDF with pdfplumber to extract text & structured tables
        with pdfplumber.open(pdf_path) as plumber_pdf:
            for i, page in enumerate(plumber_pdf.pages):
                page_num = i + 1

                # Extract text
                text_content = page.extract_text() or ""

                # Extract structured tables
                tables = page.extract_tables() or []

                # Render page image snapshot natively without Poppler
                fitz_page = fitz_doc[i]
                pix = fitz_page.get_pixmap(dpi=150)
                image_filename = f"{doc_filename}_page_{page_num}.png"
                image_path = os.path.join(self.output_dir, image_filename)
                pix.save(image_path)

                chunks.append({
                    "document_id": doc_filename,
                    "page_number": page_num,
                    "text": text_content,
                    "tables": tables,
                    "image_path": image_path
                })

        fitz_doc.close()
        return chunks


if __name__ == "__main__":
    ingestor = PDFMultimodalIngestor()
    print("PDFMultimodalIngestor (PyMuPDF engine) loaded successfully.")