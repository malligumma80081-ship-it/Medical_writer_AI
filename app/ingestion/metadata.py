from pathlib import Path


class MetadataExtractor:

    @staticmethod
    def extract(
        file_name: str,
        parser_result: dict,
    ) -> dict:

        extension = Path(file_name).suffix.lower()

        metadata = parser_result.get(
            "metadata",
            {},
        )

        return {
            "file_name": file_name,
            "file_type": extension.replace(".", ""),
            "title": (
                metadata.get("title")
                or Path(file_name).stem
            ),
            "author": metadata.get("author"),
            "subject": metadata.get("subject"),
            "page_count": parser_result.get(
                "page_count"
            ),
        }