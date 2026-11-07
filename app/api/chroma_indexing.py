from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.document import Document
from app.models.project import Project
from app.embeddings.chroma_indexing_service import (
    ChromaIndexingService,
)


router = APIRouter(
    prefix="/chroma",
    tags=["ChromaDB"],
)


@router.post("/index/{document_id}")
def index_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(404, "Document not found")

    project = db.get(Project, document.project_id)

    if not project:
        raise HTTPException(404, "Project not found")

    if (
        current_user.role != "ADMIN"
        and project.owner_id != current_user.id
    ):
        raise HTTPException(403, "Access denied")

    try:
        service = ChromaIndexingService(db)

        return service.index_document(document_id)

    except ValueError as exc:
        raise HTTPException(400, str(exc))