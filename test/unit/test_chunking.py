from app.chunking.tokenizer import count_tokens
from app.chunking.recursive_chunker import recursive_chunk
from app.chunking.section_detector import detect_section
from app.chunking.chunking_service import MedicalChunkingService


def test_token_count():
    assert count_tokens("Medical writing AI") > 0


def test_section_detection():
    assert detect_section("Abstract") == "abstract"
    assert detect_section("Results") == "results"


def test_recursive_chunking():
    text = (
        "Clinical research evaluates treatment outcomes. " * 100
    )

    chunks = recursive_chunk(
        text,
        max_tokens=100,
        overlap=20,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert count_tokens(chunk) <= 100


def test_page_metadata():
    service = MedicalChunkingService()

    segments = [{
        "page_number": 3,
        "text": "Results\nThe treatment showed improvement.",
    }]

    chunks = service.chunk_segments(segments)

    assert chunks
    assert chunks[0]["page_number"] == 3
    assert chunks[0]["section"] == "results"