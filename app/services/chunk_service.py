from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.chunking.chunking_service import MedicalChunkingService


class ChunkService:

    def __init__(self, db: Session):
        self.db = db
        self.chunker = MedicalChunkingService(
            max_tokens=500,
            overlap=75,
        )

    def create_document_chunks(self, document_id):
        document = self.db.get(Document, document_id)

        if not document:
            raise ValueError("Document not found")

        # Prefer page-level extraction when available.
        segments = document.pages or []

        if not segments:
            segments = [{
                "page_number": None,
                "text": document.extracted_text or "",
            }]

        chunks = self.chunker.chunk_segments(segments)

        if not chunks:
            raise ValueError("No text available for chunking")

        try:
            # Replace previous chunks if the operation is repeated.
            self.db.execute(
                delete(DocumentChunk).where(
                    DocumentChunk.document_id == document.id
                )
            )

            records = [
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=item["chunk_index"],
                    section=item["section"],
                    page_number=item["page_number"],
                    content=item["content"],
                    token_count=item["token_count"],
                )
                for item in chunks
            ]

            self.db.add_all(records)
            self.db.commit()

            return {
                "document_id": str(document.id),
                "total_chunks": len(records),
                "chunks": chunks,
            }

        except Exception:
            self.db.rollback()
            raise