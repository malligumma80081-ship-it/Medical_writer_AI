from app.retrieval.chroma_retrieval import ChromaRetrievalService


def test_retrieve_maps_vector_store_results(monkeypatch):
    class FakeEmbeddingService:
        def generate_embedding(self, query):
            assert query == "trial outcomes"
            return [0.1, 0.2]

    class FakeVectorStore:
        def search(self, **kwargs):
            assert kwargs == {
                "query_embedding": [0.1, 0.2],
                "project_id": "project-1",
                "limit": 5,
            }
            return [
                {
                    "id": "vector-1",
                    "document": "The primary endpoint was met.",
                    "metadata": {
                        "chunk_db_id": "chunk-1",
                        "document_id": "document-1",
                        "project_id": "project-1",
                        "file_name": "trial.pdf",
                        "section": "Results",
                        "page_number": 4,
                    },
                    "distance": 0.15,
                }
            ]

    monkeypatch.setattr(
        "app.retrieval.chroma_retrieval.EmbeddingService",
        FakeEmbeddingService,
    )
    monkeypatch.setattr(
        "app.retrieval.chroma_retrieval.ChromaStore",
        FakeVectorStore,
    )

    results = ChromaRetrievalService().retrieve(
        query="trial outcomes",
        project_id="project-1",
        limit=5,
    )

    assert results == [
        {
            "chunk_id": "chunk-1",
            "vector_id": "vector-1",
            "document_id": "document-1",
            "project_id": "project-1",
            "file_name": "trial.pdf",
            "section": "Results",
            "page_number": 4,
            "content": "The primary endpoint was met.",
            "distance": 0.15,
            "score": 0.85,
        }
    ]
