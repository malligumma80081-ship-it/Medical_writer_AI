from pathlib import Path

from app.ingestion.cleaner import TextCleaner
from app.ingestion.validators import validate_file
from app.ingestion.metadata import MetadataExtractor


def test_text_cleaner():

    text = "Medical    research\n\n\nEvidence"

    result = TextCleaner.clean(text)

    assert result == "Medical research\n\nEvidence"


def test_valid_pdf():

    content = b"%PDF-1.7 sample"

    validate_file(
        "research.pdf",
        content,
    )


def test_reject_invalid_pdf():

    content = b"not a real pdf"

    try:
        validate_file("research.pdf", content)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid PDF was accepted")


def test_reject_unsupported_file():

    try:
        validate_file("program.exe", b"content")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported file was accepted")


def test_metadata_extraction():

    result = MetadataExtractor.extract(
        "clinical_guideline.pdf",
        {
            "metadata": {
                "title": "Clinical Guideline",
                "author": "Research Team",
            },
            "page_count": 25,
        },
    )

    assert result["title"] == "Clinical Guideline"
    assert result["file_type"] == "pdf"
    assert result["page_count"] == 25