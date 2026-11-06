from docx import Document as WordDocument

from pathlib import Path


class DOCXParser:

    @staticmethod
    def extract_text(file_path: str) -> dict:

        document = WordDocument(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        tables = []

        for table in document.tables:

            table_data = []

            for row in table.rows:

                table_data.append([
                    cell.text.strip()
                    for cell in row.cells
                ])

            tables.append(table_data)

        return {
            "file_name": Path(file_path).name,
            "page_count": None,
            "metadata": {},
            "paragraphs": paragraphs,
            "tables": tables,
        }