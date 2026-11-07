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

        search_results = self.vector_store.search(
            query_embedding=query_vector,
            project_id=project_id,
            limit=limit,
        )

        return [
            {
                "chunk_id": result["metadata"].get("chunk_db_id"),
                "vector_id": result["id"],
                "document_id": result["metadata"].get("document_id"),
                "project_id": result["metadata"].get("project_id"),
                "file_name": result["metadata"].get("file_name"),
                "section": result["metadata"].get("section"),
                "page_number": result["metadata"].get("page_number"),
                "content": result["document"],
                "distance": float(result["distance"]),
                "score": max(0.0, 1.0 - float(result["distance"])),
            }
            for result in search_results
        ]