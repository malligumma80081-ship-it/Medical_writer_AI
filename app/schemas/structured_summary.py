from pydantic import BaseModel, Field


class EvidenceFinding(BaseModel):
    finding: str = Field(
        description="Scientific finding reported in the source"
    )

    citation_ids: list[str] = Field(
        description="Supporting source IDs, such as S1 and S2"
    )

    evidence_note: str = Field(
        description="Brief explanation of what the source reports"
    )


class StructuredMedicalSummary(BaseModel):

    title: str

    study_overview: str

    primary_efficacy_outcomes: list[EvidenceFinding]

    secondary_outcomes: list[EvidenceFinding]

    safety_findings: list[EvidenceFinding]

    study_limitations: list[EvidenceFinding]

    evidence_gaps: list[str]

    human_review_note: str = (
        "Qualified human review required before use."
    )