from app.vectorstore.chroma_store import ChromaStore


class FakeCollection:
    def __init__(self):
        self.deleted = []
        self.upserted = []
        self.query_args = None

    def delete(self, **kwargs):
        self.deleted.append(kwargs)

    def upsert(self, **kwargs):
        self.upserted.append(kwargs)

    def query(self, **kwargs):
        self.query_args = kwargs
        return {
            "ids": [["chunk-1"]],
            "documents": [["A clinical result."]],
            "metadatas": [[{"project_id": "project-1"}]],
            "distances": [[0.15]],
        }


def test_index_replaces_document_chunks(monkeypatch, tmp_path):
    collection = FakeCollection()
    client_options = {}

    class FakeClient:
        def __init__(self, path):
            client_options["path"] = path

        def get_or_create_collection(self, **kwargs):
            client_options["collection"] = kwargs
            return collection

    monkeypatch.setattr("app.vectorstore.chroma_store.chromadb.PersistentClient", FakeClient)
    monkeypatch.setattr(
        "app.vectorstore.chroma_store.settings.CHROMA_PERSIST_DIRECTORY",
        str(tmp_path / "vectors"),
    )

    store = ChromaStore()
    store.index_document_chunks(
        document_id="document-1",
        ids=["chunk-1"],
        documents=["A clinical result."],
        embeddings=[[0.1, 0.2]],
        metadatas=[{"project_id": "project-1"}],
    )

    assert client_options["path"] == str(tmp_path / "vectors")
    assert client_options["collection"] == {
        "name": "medical_chunks",
        "metadata": {"hnsw:space": "cosine"},
    }
    assert collection.deleted == [{"where": {"document_id": "document-1"}}]
    assert collection.upserted[0]["ids"] == ["chunk-1"]


def test_search_filters_project_and_returns_distances(monkeypatch, tmp_path):
    collection = FakeCollection()

    class FakeClient:
        def __init__(self, path):
            pass

        def get_or_create_collection(self, **kwargs):
            return collection

    monkeypatch.setattr("app.vectorstore.chroma_store.chromadb.PersistentClient", FakeClient)
    monkeypatch.setattr(
        "app.vectorstore.chroma_store.settings.CHROMA_PERSIST_DIRECTORY",
        str(tmp_path / "vectors"),
    )

    results = ChromaStore().search(
        query_embedding=[0.1, 0.2],
        project_id="project-1",
        limit=3,
    )

    assert collection.query_args == {
        "query_embeddings": [[0.1, 0.2]],
        "where": {"project_id": "project-1"},
        "n_results": 3,
        "include": ["documents", "metadatas", "distances"],
    }
    assert results == [{
        "id": "chunk-1",
        "document": "A clinical result.",
        "metadata": {"project_id": "project-1"},
        "distance": 0.15,
    }]


def test_persistent_store_indexes_and_searches_local_vectors(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        "app.vectorstore.chroma_store.settings.CHROMA_PERSIST_DIRECTORY",
        str(tmp_path / "vectors"),
    )
    store = ChromaStore()

    store.index_document_chunks(
        document_id="document-1",
        ids=["chunk-1"],
        documents=["A clinical result."],
        embeddings=[[1.0, 0.0]],
        metadatas=[{
            "document_id": "document-1",
            "project_id": "project-1",
            "section": "results",
            "page_number": 1,
            "token_count": 4,
            "file_name": "study.pdf",
        }],
    )

    results = store.search(
        query_embedding=[1.0, 0.0],
        project_id="project-1",
        limit=3,
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-1"
    assert results[0]["document"] == "A clinical result."
    assert results[0]["metadata"]["file_name"] == "study.pdf"
    assert results[0]["distance"] == 0
