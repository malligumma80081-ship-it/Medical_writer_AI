from app.verification.claim_extractor import ClaimExtractor
from app.verification.evidence_matcher import EvidenceMatcher
from app.verification.claim_verifier import ClaimVerifier


class VerificationService:

    def __init__(self):

        self.extractor = ClaimExtractor()
        self.matcher = EvidenceMatcher()
        self.verifier = ClaimVerifier()

    def verify_summary(
        self,
        generation_id: str,
        summary: dict,
        sources: list[dict],
    ) -> dict:

        claims = self.extractor.extract(summary)

        results = []

        for item in claims:

            matched_sources = self.matcher.match(
                citation_ids=item["citation_ids"],
                sources=sources,
            )

            if not item["citation_ids"]:
                result = {
                    "status": "NEEDS_REVIEW",
                    "explanation": "The finding has no citation.",
                    "supporting_evidence": [],
                    "missing_information": [
                        "A source citation is required."
                    ],
                    "numerical_check_passed": None,
                }

            elif len(matched_sources) != len(
                set(item["citation_ids"])
            ):
                result = {
                    "status": "NEEDS_REVIEW",
                    "explanation": (
                        "One or more citation identifiers "
                        "could not be matched to source records."
                    ),
                    "supporting_evidence": [],
                    "missing_information": [
                        "Original source mapping is incomplete."
                    ],
                    "numerical_check_passed": None,
                }

            else:
                result = self.verifier.verify(
                    claim=item["claim"],
                    evidence=matched_sources,
                )

            results.append({
                "claim_id": item["claim_id"],
                "claim": item["claim"],
                "citation_ids": item["citation_ids"],
                "group": item["group"],
                **result,
            })

        statuses = [
            item["status"]
            for item in results
        ]

        return {
            "generation_id": generation_id,
            "total_claims": len(results),
            "supported_claims": statuses.count("SUPPORTED"),
            "partially_supported_claims": statuses.count(
                "PARTIALLY_SUPPORTED"
            ),
            "unsupported_claims": statuses.count("UNSUPPORTED"),
            "needs_review_claims": statuses.count("NEEDS_REVIEW"),
            "results": results,
            "human_review_required": True,
        }