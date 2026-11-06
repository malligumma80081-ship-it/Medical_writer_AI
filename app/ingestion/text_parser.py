from pathlib import Path


class TXTParser:

    @staticmethod
    def extract_text(file_path: str) -> dict:

        path = Path(file_path)

        text = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        return {
            "file_name": path.name,
            "page_count": None,
            "metadata": {},
            "content": text,
        }