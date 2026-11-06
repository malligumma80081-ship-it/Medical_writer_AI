from uuid import UUID, uuid5, NAMESPACE_URL

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore


class IndexingService:

    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaStore()

    def index_document(self, document_id: UUID):

        document = self.db.get(Document, document_id)

        if not document:
            raise ValueError("Document not found")

        chunks = self.db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        ).all()

        if not chunks:
            raise ValueError("No chunks found. Run Day 5 chunking first.")

        texts = [chunk.content for chunk in chunks]

        vectors = self.embedding_service.generate_embeddings(texts)

        ids = []
        metadatas = []

        for chunk in chunks:
            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{document_id}:{chunk.chunk_index}",
                )
            )

            ids.append(point_id)
            metadata = {
                "document_id": str(document.id),
                "project_id": str(document.project_id),
                "chunk_index": chunk.chunk_index,
                "section": chunk.section or "general",
                "token_count": chunk.token_count,
            }
            if chunk.page_number is not None:
                metadata["page_number"] = chunk.page_number
            if document.file_name is not None:
                metadata["file_name"] = document.file_name
            metadatas.append(metadata)

        self.vector_store.index_document_chunks(
            document_id=str(document_id),
            ids=ids,
            documents=[chunk.content for chunk in chunks],
            embeddings=vectors,
            metadatas=metadatas,
        )

        return {
            "document_id": str(document_id),
            "total_chunks_indexed": len(ids),
            "embedding_dimensions": len(vectors[0]),
            "collection": self.vector_store.COLLECTION_NAME,
        }