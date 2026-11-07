from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.project import Project

from app.services.summary_service import MedicalSummaryService
from app.services.summary_persistence_service import (
    SummaryPersistenceService,
)


router = APIRouter(
    prefix="/summaries",
    tags=["Medical Summaries"],
)


class SummaryRequest(BaseModel):
    project_id: UUID
    question: str = Field(
        min_length=5,
        max_length=2000,
    )


@router.post("/generate")
def generate_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    project = db.get(Project, request.project_id)

    if not project:
        raise HTTPException(404, "Project not found")

    if (
        current_user.role != "ADMIN"
        and project.owner_id != current_user.id
    ):
        raise HTTPException(403, "Access denied")

    try:
        service = MedicalSummaryService()

        result = service.generate_summary(
            question=request.question,
            project_id=str(request.project_id),
        )

        persistence = SummaryPersistenceService(db)

        generation = persistence.save_summary(
            result=result,
            project_id=request.project_id,
            user_id=current_user.id,
        )

        return {
            "generation_id": str(generation.id),
            "question": result["question"],
            "summary": result["summary"],
            "model": result["model"],
            "provider": result["provider"],
            "retrieved_count": result["retrieved_count"],
            "evidence_count": result["evidence_count"],
            "sources": result["sources"],
            "review_status": "PENDING_REVIEW",
            "human_review_required": True,
        }

    except ValueError as exc:
        raise HTTPException(400, str(exc))

    except Exception:
        # Log the exception securely in production.
        raise HTTPException(
            503,
            "Summary generation failed. Check the model service and application logs.",
        )