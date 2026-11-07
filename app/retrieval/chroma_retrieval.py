from typing import Any, cast

from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore


class ChromaRetrievalService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaStore()

    def retrieve(
        self,
        query: str,
        project_id: str,
        limit: int = 15,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError("Query cannot be empty")

        query_vector = (
            self.embedding_service.generate_embedding(query)
        )

        response = self.vector_store.search(
            query_embedding=query_vector,
            project_id=project_id,
            limit=limit,
        )

        results = []

        result_data = cast(dict[str, Any], response)
        ids = result_data["ids"][0]
        documents = result_data["documents"][0]
        metadatas = result_data["metadatas"][0]
        distances = result_data["distances"][0]

        for vector_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            results.append({
                "chunk_id": metadata.get("chunk_db_id"),
                "vector_id": vector_id,
                "document_id": metadata.get("document_id"),
                "project_id": metadata.get("project_id"),
                "file_name": metadata.get("file_name"),
                "section": metadata.get("section"),
                "page_number": metadata.get("page_number"),
                "content": content,
                "distance": float(distance),
                "score": max(0.0, 1.0 - float(distance)),
            })

        return results