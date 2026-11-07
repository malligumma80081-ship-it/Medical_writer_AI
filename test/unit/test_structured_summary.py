from app.schemas.structured_summary import (
    StructuredMedicalSummary,
)


def test_valid_structured_summary():

    data = {
        "title": "Clinical Study Summary",
        "study_overview": "A randomized study.",
        "primary_efficacy_outcomes": [
            {
                "finding": "Primary endpoint was reported.",
                "citation_ids": ["S1"],
                "evidence_note": "Reported in Results.",
            }
        ],
        "secondary_outcomes": [],
        "safety_findings": [],
        "study_limitations": [],
        "evidence_gaps": [],
        "human_review_note": "Review required.",
    }

    result = StructuredMedicalSummary.model_validate(data)

    assert result.title == "Clinical Study Summary"
    assert result.primary_efficacy_outcomes[0].citation_ids == ["S1"]