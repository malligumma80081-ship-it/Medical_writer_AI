from pathlib import Path


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def validate_file(
    filename: str,
    content: bytes,
) -> None:

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file format.")

    if not content:
        raise ValueError("Empty file.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File exceeds 20 MB limit.")

    # Validate file signatures.
    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file.")

    elif extension == ".docx":
        if not content.startswith(b"PK"):
            raise ValueError("Invalid DOCX file.")

    elif extension == ".txt":
        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("TXT must use UTF-8 encoding.")