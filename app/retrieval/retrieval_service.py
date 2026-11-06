from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.chroma_store import ChromaStore


class RetrievalService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaStore()

    def retrieve(
        self,
        query: str,
        project_id: str,
        limit: int = 5,
    ):

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        query_vector = (
            self.embedding_service.generate_embedding(query)
        )

        results = self.vector_store.search(
            query_embedding=query_vector,
            project_id=project_id,
            limit=limit,
        )

        evidence = []

        for result in results:
            evidence.append({
                "chunk_id": result["id"],
                "document_id": result["metadata"].get("document_id"),
                "section": result["metadata"].get("section"),
                "page_number": result["metadata"].get("page_number"),
                "content": result["document"],
                "score": 1.0 - float(result["distance"]),
                "file_name": result["metadata"].get("file_name"),
            })

        return evidence