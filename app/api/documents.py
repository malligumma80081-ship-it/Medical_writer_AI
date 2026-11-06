import uuid

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Path,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.project import Project

from app.core.dependencies import (
    get_current_user,
    require_roles,
)

from app.services.document_service import (
    DocumentService,
)

from app.schemas.document import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Medical Documents"],
)


@router.post(
    "/upload/{project_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: uuid.UUID = Path(
        description=(
            "Project UUID returned by POST /api/v1/projects or "
            "GET /api/v1/projects."
        )
    ),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MEDICAL_WRITER", "REVIEWER")
    ),
):

    project = db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    # Enforce project-level ownership.
    if (
        current_user.role != "ADMIN"
        and project.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot access this project.",
        )

    content = await file.read(20 * 1024 * 1024 + 1)

    service = DocumentService(db)

    try:

        document = service.upload(
            project=project,
            filename=file.filename or "",
            content=content,
        )

        return document

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Document processing failed.",
        )

    finally:
        await file.close()