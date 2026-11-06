from pathlib import Path
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.docx_parser import DOCXParser
from app.ingestion.text_parser import TXTParser

from app.ingestion.cleaner import TextCleaner
from app.ingestion.metadata import MetadataExtractor


class DocumentIngestionService:

    def __init__(self):

        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.txt_parser = TXTParser()

        self.cleaner = TextCleaner()

    def process(self, file_path: str) -> dict:

        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":

            result = self.pdf_parser.extract_text(
                file_path
            )

            for page in result["pages"]:

                page["content"] = self.cleaner.clean(
                    page["content"]
                )

            result["content"] = "\n\n".join(
                page["content"]
                for page in result["pages"]
            )

        elif extension == ".docx":

            result = self.docx_parser.extract_text(
                file_path
            )

            result["content"] = self.cleaner.clean(
                "\n\n".join(result["paragraphs"])
            )

        elif extension == ".txt":

            result = self.txt_parser.extract_text(
                file_path
            )

            result["content"] = self.cleaner.clean(
                result["content"]
            )

        else:
            raise ValueError(
                "Unsupported document format."
            )

        metadata = MetadataExtractor.extract(
            Path(file_path).name,
            result,
        )

        ocr_required_pages = []
        if extension == ".pdf":
            ocr_required_pages = self.pdf_parser.find_ocr_required_pages(file_path)

        return {
            "metadata": metadata,
            "content": result["content"],
            "pages": result.get("pages", []),
            "paragraphs": result.get("paragraphs", []),
            "tables": result.get("tables", []),
            "ocr_required_pages": ocr_required_pages,
        }