import uuid

from pathlib import Path

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.project import Project

from app.ingestion.validators import validate_file
from app.ingestion.ingestion_service import (
    DocumentIngestionService,
)


class DocumentService:

    def __init__(self, db: Session):

        self.db = db

        self.ingestion = DocumentIngestionService()

        self.storage_dir = Path("data/raw")

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def upload(
        self,
        project: Project,
        filename: str,
        content: bytes,
    ) -> Document:

        validate_file(filename, content)

        extension = Path(filename).suffix.lower()

        document_id = uuid.uuid4()

        safe_filename = f"{document_id}{extension}"

        file_path = self.storage_dir / safe_filename

        document = None

        try:

            # Save file with generated filename.
            with file_path.open("xb") as file:
                file.write(content)

            # Extract document content.
            result = self.ingestion.process(
                str(file_path)
            )

            metadata = result["metadata"]

            page_count = metadata.get("page_count") or 0

            # Save database record.
            document = Document(
                id=document_id,
                project_id=project.id,
                title=metadata["title"],
                file_name=filename,
                file_type=metadata["file_type"],
                storage_path=str(file_path),
                page_count=page_count,
                source_metadata=metadata,
                extracted_text=result["content"],
                status="PROCESSED",
            )

            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            return document

        except Exception:

            self.db.rollback()

            if file_path.exists():
                file_path.unlink()

            raise