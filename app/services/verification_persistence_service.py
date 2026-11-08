from uuid import UUID

from sqlalchemy.orm import Session

from app.models.claim_verification import ClaimVerification


class VerificationPersistenceService:

    def __init__(self, db: Session):
        self.db = db

    def save_report(
        self,
        generation_id: UUID,
        report: dict,
    ):

        try:
            for item in report["results"]:

                record = ClaimVerification(
                    generation_id=generation_id,
                    claim_text=item["claim"],
                    citation_ids=item["citation_ids"],
                    status=item["status"],
                    explanation=item["explanation"],
                    evidence_details={
                        "group": item["group"],
                        "supporting_evidence": (
                            item["supporting_evidence"]
                        ),
                        "missing_information": (
                            item["missing_information"]
                        ),
                        "numerical_check_passed": (
                            item["numerical_check_passed"]
                        ),
                    },
                )

                self.db.add(record)

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise