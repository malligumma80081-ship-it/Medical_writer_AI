from app.verification.evidence_matcher import EvidenceMatcher


def test_evidence_matching():

    sources = [
        {
            "citation_id": "S1",
            "document_id": "doc-1",
            "content": "Reported endpoint result.",
        }
    ]

    result = EvidenceMatcher().match(
        ["S1"],
        sources,
    )

    assert len(result) == 1
    assert result[0]["citation_id"] == "S1"


def test_missing_evidence():

    result = EvidenceMatcher().match(
        ["S99"],
        [],
    )

    assert result == []