from app.db.base import Base
from app.models import (
    User,
    Project,
    Document,
    DocumentChunk,
    Generation,
    Citation,
    Review,
    AuditLog,
)


def test_all_models_registered():

    expected_tables = {
        "users",
        "projects",
        "documents",
        "document_chunks",
        "generations",
        "citations",
        "reviews",
        "audit_logs",
    }

    assert expected_tables.issubset(
        set(Base.metadata.tables.keys())
    )


def test_project_has_owner_relationship():

    assert hasattr(Project, "owner")
    assert hasattr(Project, "documents")


def test_document_has_chunks_relationship():

    assert hasattr(Document, "chunks")


def test_generation_has_citations_and_reviews():

    assert hasattr(Generation, "citations")
    assert hasattr(Generation, "reviews")