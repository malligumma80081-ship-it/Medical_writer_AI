from uuid import uuid5, NAMESPACE_URL

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore


class ChromaIndexingService:

    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaStore()

    def index_document(self, document_id):

        document = self.db.get(Document, document_id)

        if not document:
            raise ValueError("Document not found")

        chunks = self.db.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.chunk_index)
        ).all()

        if not chunks:
            raise ValueError(
                "No chunks found. Complete Day 5 first."
            )

        texts = [chunk.content for chunk in chunks]

        embeddings = (
            self.embedding_service.generate_embeddings(texts)
        )

        ids = []
        metadatas = []

        for chunk in chunks:

            vector_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{document_id}:{chunk.chunk_index}",
                )
            )

            ids.append(vector_id)

            metadata = {
                "project_id": str(document.project_id),
                "document_id": str(document.id),
                "chunk_index": int(chunk.chunk_index),
                "section": chunk.section or "general",
                "file_name": document.file_name,
            }

            if chunk.page_number is not None:
                metadata["page_number"] = int(
                    chunk.page_number
                )

            # Preserve the database chunk ID if available.
            if getattr(chunk, "id", None) is not None:
                metadata["chunk_db_id"] = str(chunk.id)

            metadatas.append(metadata)

        self.vector_store.upsert_chunks(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        return {
            "document_id": str(document_id),
            "total_chunks_indexed": len(ids),
            "embedding_dimensions": len(embeddings[0]),
            "vector_database": "ChromaDB",
        }