from typing import Literal
from pydantic import BaseModel, Field


VerificationStatus = Literal[
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "UNSUPPORTED",
    "NEEDS_REVIEW",
]


class ClaimVerificationResult(BaseModel):

    claim: str

    citation_ids: list[str]

    status: VerificationStatus

    explanation: str

    supporting_evidence: list[str] = Field(
        default_factory=list
    )

    missing_information: list[str] = Field(
        default_factory=list
    )

    numerical_check_passed: bool | None = None


class VerificationReport(BaseModel):

    generation_id: str

    total_claims: int

    supported_claims: int

    partially_supported_claims: int

    unsupported_claims: int

    needs_review_claims: int

    results: list[ClaimVerificationResult]

    human_review_required: bool = True