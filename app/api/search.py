from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.project import Project
from app.schemas.retrieval import SearchRequest
from app.retrieval.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"],
)


@router.post("/")
def semantic_search(
    request: SearchRequest,
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
        service = RetrievalService()

        results = service.retrieve(
            query=request.query,
            project_id=str(request.project_id),
            limit=request.limit,
        )

        return {
            "query": request.query,
            "result_count": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(400, str(exc))