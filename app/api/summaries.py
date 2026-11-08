
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.project import Project

from app.services.summary_service import MedicalSummaryService
from app.services.summary_persistence_service import (
    SummaryPersistenceService,
)
from app.services.structured_summary_service import (
    StructuredSummaryService,
)


# One router for both summary endpoints
router = APIRouter(
    prefix="/summaries",
    tags=["Medical Summaries"],
)


# --------------------------------------------------
# Request Schemas
# --------------------------------------------------

class SummaryRequest(BaseModel):
    project_id: UUID

    question: str = Field(
        min_length=5,
        max_length=2000,
    )


class StructuredSummaryRequest(BaseModel):
    project_id: UUID

    question: str = Field(
        min_length=5,
        max_length=2000,
    )

    document_type: str = Field(
        default="clinical_summary",
        min_length=3,
        max_length=100,
    )


# --------------------------------------------------
# Shared Project Access Validation
# --------------------------------------------------

def validate_project_access(
    project_id: UUID,
    db: Session,
    current_user,
) -> Project:

    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if (
        current_user.role != "ADMIN"
        and project.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return project


# --------------------------------------------------
# 1. Generate Medical Summary
# --------------------------------------------------

@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
)
def generate_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    validate_project_access(
        project_id=request.project_id,
        db=db,
        current_user=current_user,
    )

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the actual exception securely on the server.
        # Do not expose internal errors to API clients.
        print(f"Medical summary generation error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Summary generation failed. "
                "Check the model service and application logs."
            ),
        ) from exc


# --------------------------------------------------
# 2. Generate Structured Medical Summary
# --------------------------------------------------

@router.post(
    "/generate-structured",
    status_code=status.HTTP_200_OK,
    description=(
        "Returns a generation_id. Copy it into "
        "POST /api/v1/verification/{generation_id} "
        "to verify the generated summary."
    ),
)
def generate_structured_summary(
    request: StructuredSummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    validate_project_access(
        project_id=request.project_id,
        db=db,
        current_user=current_user,
    )

    try:
        service = StructuredSummaryService()

        result = service.generate(
            question=request.question,
            project_id=str(request.project_id),
            document_type=request.document_type,
        )

        persistence = SummaryPersistenceService(db)
        generation = persistence.save_summary(
            result=result,
            project_id=request.project_id,
            user_id=current_user.id,
        )

        return {
            "generation_id": str(generation.id),
            "project_id": str(request.project_id),
            "document_type": request.document_type,
            "result": result,
            "review_status": "PENDING_REVIEW",
            "human_review_required": True,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"Structured summary generation error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Structured summary generation failed.",
        ) from exc
  