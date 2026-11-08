from uuid import UUID
from typing import cast

from sqlalchemy.orm import Session

from app.api import summaries
from app.services.summary_persistence_service import (
    SummaryPersistenceService,
)


def test_structured_summary_response_includes_generation_id(
    monkeypatch,
):
    project_id = UUID("a2137098-e6f8-44c8-9307-ff32ad53ca3e")
    user_id = UUID("c7a6ab15-c680-4dae-bd02-08a4d6c6d3db")
    generation_id = UUID("d5063389-b588-4421-846e-f770ed6e0d1f")
    result = {
        "question": "Summarize study results",
        "document_type": "clinical_summary",
        "model": "llama3.2",
        "summary": {},
        "sources": [],
    }

    class FakeDatabase:
        def get(self, model, key):
            assert model is summaries.Project
            assert key == project_id
            return type("Project", (), {"owner_id": user_id})()

    class FakeSummaryService:
        def generate(self, **kwargs):
            assert kwargs == {
                "question": "Summarize study results",
                "project_id": str(project_id),
                "document_type": "clinical_summary",
            }
            return result

    class FakePersistenceService:
        def __init__(self, db):
            assert isinstance(db, FakeDatabase)

        def save_summary(self, **kwargs):
            assert kwargs == {
                "result": result,
                "project_id": project_id,
                "user_id": user_id,
            }
            return type("Generation", (), {"id": generation_id})()

    monkeypatch.setattr(
        summaries,
        "StructuredSummaryService",
        FakeSummaryService,
    )
    monkeypatch.setattr(
        summaries,
        "SummaryPersistenceService",
        FakePersistenceService,
    )

    response = summaries.generate_structured_summary(
        request=summaries.StructuredSummaryRequest(
            project_id=project_id,
            question="Summarize study results",
        ),
        db=cast(Session, FakeDatabase()),
        current_user=type(
            "User",
            (),
            {"id": user_id, "role": "USER"},
        )(),
    )

    assert response["generation_id"] == str(generation_id)
    assert response["result"] == result


def test_summary_persistence_saves_sources_for_verification(
    monkeypatch,
):
    generation_id = UUID("d5063389-b588-4421-846e-f770ed6e0d1f")
    sources = [{"citation_id": "S1", "content": "Study evidence."}]
    created = {}

    class FakeGeneration:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.id = generation_id

    class FakeReview:
        def __init__(self, **_kwargs):
            pass

    class FakeDatabase:
        def add(self, _instance):
            pass

        def flush(self):
            pass

        def commit(self):
            pass

        def refresh(self, _instance):
            pass

        def rollback(self):
            raise AssertionError("Unexpected rollback")

    monkeypatch.setattr(
        "app.services.summary_persistence_service.Generation",
        FakeGeneration,
    )
    monkeypatch.setattr(
        "app.services.summary_persistence_service.Review",
        FakeReview,
    )

    generation = SummaryPersistenceService(
        cast(Session, FakeDatabase())
    ).save_summary(
        result={
            "question": "Summarize study results",
            "document_type": "clinical_summary",
            "model": "llama3.2",
            "summary": {"primary_efficacy_outcomes": []},
            "sources": sources,
        },
        project_id=UUID("a2137098-e6f8-44c8-9307-ff32ad53ca3e"),
        user_id=UUID("c7a6ab15-c680-4dae-bd02-08a4d6c6d3db"),
    )

    assert generation.id == generation_id
    assert created["document_type"] == "clinical_summary"
    assert created["evidence_snapshot"] == {"sources": sources}
