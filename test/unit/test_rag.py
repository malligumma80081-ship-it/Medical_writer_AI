from app.rag.query_processor import QueryProcessor
from app.rag.context_builder import ContextBuilder


def test_query_processor():
    processor = QueryProcessor()

    result = processor.process(
        "  What were the primary efficacy outcomes?  "
    )

    assert result == "What were the primary efficacy outcomes?"


def test_empty_query():
    processor = QueryProcessor()

    try:
        processor.process("")
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_context_builder():
    builder = ContextBuilder(max_tokens=3000)

    evidence = [
        {
            "document_id": "doc-1",
            "file_name": "trial.pdf",
            "section": "results",
            "page_number": 8,
            "chunk_id": "chunk-1",
            "content": "The primary endpoint was achieved.",
            "score": 0.85,
            "rerank_score": 2.1,
        }
    ]

    result = builder.build(evidence)

    assert len(result["sources"]) == 1
    assert result["sources"][0]["citation_id"] == "S1"
    assert result["sources"][0]["page_number"] == 8
    assert "[S1]" in result["context"]