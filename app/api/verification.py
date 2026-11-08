import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.generation import Generation
from app.models.project import Project

from app.verification.verification_service import (
    VerificationService,
)

from app.services.verification_persistence_service import (
    VerificationPersistenceService,
)


router = APIRouter(
    prefix="/verification",
    tags=["Evidence Verification"],
)


@router.post(
    "/{generation_id}",
    description=(
        "Use the generation_id returned by "
        "POST /api/v1/summaries/generate-structured. "
        "This endpoint verifies structured JSON summaries."
    ),
)
def verify_generation(
    generation_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    generation = db.get(Generation, generation_id)

    if not generation:
        raise HTTPException(
            404,
            "Generation not found",
        )

    project = db.get(Project, generation.project_id)

    if not project:
        raise HTTPException(
            404,
            "Project not found",
        )

    if (
        current_user.role != "ADMIN"
        and project.owner_id != current_user.id
    ):
        raise HTTPException(
            403,
            "Access denied",
        )

    try:
        if not generation.generated_content:
            raise ValueError("Generated summary is unavailable.")

        try:
            summary = json.loads(generation.generated_content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Only structured JSON summaries can be verified."
            ) from exc

        if not isinstance(summary, dict):
            raise ValueError(
                "Only structured JSON summaries can be verified."
            )

        evidence_snapshot = generation.evidence_snapshot or {}

        sources = evidence_snapshot.get("sources", [])

        if not sources:
            raise ValueError(
                "Original evidence snapshot is unavailable."
            )

        service = VerificationService()

        report = service.verify_summary(
            generation_id=str(generation.id),
            summary=summary,
            sources=sources,
        )

        persistence = VerificationPersistenceService(db)

        persistence.save_report(
            generation_id=generation.id,
            report=report,
        )

        return report

    except ValueError as exc:
        raise HTTPException(400, str(exc))

    except Exception:
        raise HTTPException(
            503,
            "Evidence verification failed.",
        )