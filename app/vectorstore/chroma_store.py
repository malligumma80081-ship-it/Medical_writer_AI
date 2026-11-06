from pathlib import Path
from typing import Any, cast

import chromadb

from app.core.config import settings


class ChromaStore:
    COLLECTION_NAME = "medical_chunks"

    def __init__(self):
        persist_directory = Path(settings.CHROMA_PERSIST_DIRECTORY)
        if not persist_directory.is_absolute():
            persist_directory = Path.cwd() / persist_directory

        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def index_document_chunks(
        self,
        document_id: str,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.delete(where={"document_id": document_id})
        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=cast(Any, embeddings),
                metadatas=cast(Any, metadatas),
            )

    def search(
        self,
        query_embedding: list[float],
        project_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            where={"project_id": project_id},
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )

        ids = result["ids"][0]
        document_results = result.get("documents") or []
        metadata_results = result.get("metadatas") or []
        distance_results = result.get("distances") or []
        documents = document_results[0] or [] if document_results else []
        metadatas = metadata_results[0] or [] if metadata_results else []
        distances = distance_results[0] or [] if distance_results else []
        return [
            {
                "id": chunk_id,
                "document": document,
                "metadata": metadata or {},
                "distance": distance,
            }
            for chunk_id, document, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            )
        ]
