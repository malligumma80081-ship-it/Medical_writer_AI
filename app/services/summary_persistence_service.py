import re
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.generation import Generation
from app.models.citation import Citation
from app.models.review import Review


class SummaryPersistenceService:

    def __init__(self, db: Session):
        self.db = db

    def save_summary(
        self,
        result: dict,
        project_id: UUID,
        user_id: UUID,
    ):

        try:
            generation = Generation(
                project_id=project_id,
                created_by=user_id,
                document_type="SCIENTIFIC_LITERATURE_SUMMARY",
                prompt=result["question"],
                generated_content=result["summary"],
                status="PENDING_REVIEW",
                model_name=result["model"],
            )

            self.db.add(generation)
            self.db.flush()

            # Only accept citation IDs that the server supplied.
            valid_sources = {
                source["citation_id"]: source
                for source in result["sources"]
            }

            cited_ids = set(
                re.findall(
                    r"\[(S\d+)\]",
                    result["summary"],
                )
            )

            for citation_id in sorted(cited_ids):
                source = valid_sources.get(citation_id)

                if not source:
                    continue

                chunk_db_id = source.get("chunk_id")

                self.db.add(
                    Citation(
                        generation_id=generation.id,
                        document_id=UUID(
                            source["document_id"]
                        ),
                        chunk_id=(
                            UUID(chunk_db_id)
                            if chunk_db_id
                            else None
                        ),
                        page_number=source.get("page_number"),
                        cited_text=source["content"],
                        verification_status="UNVERIFIED",
                    )
                )

            # Create a mandatory pending review record.
            review = Review(
                generation_id=generation.id,
                reviewer_id=None,
                status="PENDING",
                comments=None,
            )

            self.db.add(review)
            self.db.commit()
            self.db.refresh(generation)

            return generation

        except Exception:
            self.db.rollback()
            raise