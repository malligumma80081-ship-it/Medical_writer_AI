import re


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n")

        # Remove null characters
        text = text.replace("\x00", "")

        # Remove repeated whitespace
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Normalize excessive newlines
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()