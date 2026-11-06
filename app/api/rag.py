from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.project import Project
from app.rag.rag_pipeline import MedicalRAGPipeline


router = APIRouter(
    prefix="/rag",
    tags=["Medical RAG"],
)


class RAGRequest(BaseModel):
    project_id: UUID
    query: str = Field(
        min_length=3,
        max_length=2000,
    )
    retrieval_limit: int = Field(
        default=15,
        ge=1,
        le=50,
    )
    final_limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )


@router.post("/retrieve")
def retrieve_evidence(
    request: RAGRequest,
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
        pipeline = MedicalRAGPipeline()

        return pipeline.run(
            query=request.query,
            project_id=str(request.project_id),
            retrieval_limit=request.retrieval_limit,
            final_limit=request.final_limit,
        )

    except ValueError as exc:
        raise HTTPException(400, str(exc))