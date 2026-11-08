from app.verification.claim_extractor import ClaimExtractor


def test_claim_extraction():

    summary = {
        "primary_efficacy_outcomes": [
            {
                "finding": "The endpoint improved.",
                "citation_ids": ["S1"],
            }
        ],
        "secondary_outcomes": [],
        "safety_findings": [],
        "study_limitations": [],
    }

    claims = ClaimExtractor().extract(summary)

    assert len(claims) == 1
    assert claims[0]["citation_ids"] == ["S1"]