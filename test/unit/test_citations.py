from app.schemas.structured_summary import (
    StructuredMedicalSummary,
    EvidenceFinding,
)

from app.validation.citation_validator import (
    CitationValidator,
)


def test_valid_citation():

    summary = StructuredMedicalSummary(
        title="Study Summary",
        study_overview="Study overview.",
        primary_efficacy_outcomes=[
            EvidenceFinding(
                finding="The primary endpoint was reported.",
                citation_ids=["S1"],
                evidence_note="Reported in Results.",
            )
        ],
        secondary_outcomes=[],
        safety_findings=[],
        study_limitations=[],
        evidence_gaps=[],
    )

    sources = [
        {"citation_id": "S1"}
    ]

    result = CitationValidator().validate(
        summary,
        sources,
    )

    assert result["is_valid"] is True


def test_invalid_citation():

    summary = StructuredMedicalSummary(
        title="Study Summary",
        study_overview="Study overview.",
        primary_efficacy_outcomes=[
            EvidenceFinding(
                finding="The primary endpoint was reported.",
                citation_ids=["S99"],
                evidence_note="Unsupported source ID.",
            )
        ],
        secondary_outcomes=[],
        safety_findings=[],
        study_limitations=[],
        evidence_gaps=[],
    )

    sources = [
        {"citation_id": "S1"}
    ]

    result = CitationValidator().validate(
        summary,
        sources,
    )

    assert result["is_valid"] is False