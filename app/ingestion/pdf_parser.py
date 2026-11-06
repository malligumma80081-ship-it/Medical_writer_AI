
import fitz
from pathlib import Path


class PDFParser:

    @staticmethod
    def extract_text(file_path: str) -> dict:
        pages = []
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        with fitz.open(path) as pdf:

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text")

                pages.append({
                    "page_number": page_number,
                    "content": text,
                })

            metadata = pdf.metadata or {}

            return {
                "file_name": path.name,
                "page_count": len(pdf),
                "metadata": {
                    "title": metadata.get("title"),
                    "author": metadata.get("author"),
                    "subject": metadata.get("subject"),
                    "creator": metadata.get("creator"),
                    "producer": metadata.get("producer"),
                    "creation_date": metadata.get("creationDate"),
                },
                "pages": pages,
            }

    @staticmethod
    def find_ocr_required_pages(file_path: str) -> list[int]:
        required_pages = []
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        with fitz.open(path) as pdf:

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()
                images = page.get_images(full=True)

                # Page has very little selectable text
                # and contains embedded images.
                if len(text) < 30 and images:
                    required_pages.append(page_number)

                # Also identify blank-text pages.
                elif len(text) < 30 and not images:
                    required_pages.append(page_number)

        return required_pages
