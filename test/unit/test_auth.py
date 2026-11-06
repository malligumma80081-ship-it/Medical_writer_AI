import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.auth_session import AuthSession
from app.models.document import Document
from app.models.project import Project
from app.models.user import User
from app.services.token_service import (
    create_access_token,
    create_refresh_token,
)


@pytest.fixture
def auth_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        with test_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, test_session
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_refresh_accepts_sqlite_naive_expiration(auth_test_client):
    client, test_session = auth_test_client

    with test_session() as db:
        user = User(
            full_name="Test User",
            email="refresh-test@example.com",
            hashed_password=hash_password("test-password-1234"),
            role="MEDICAL_WRITER",
        )
        db.add(user)
        db.flush()

        refresh_token, jti, expires_at = create_refresh_token(str(user.id))
        auth_session = AuthSession(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
        )
        db.add(auth_session)
        db.commit()
        session_id = auth_session.id

    with test_session() as db:
        stored_session = db.get(AuthSession, session_id)
        assert stored_session is not None
        assert stored_session.expires_at.tzinfo is None

    response = client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"] != refresh_token

    with test_session() as db:
        old_session = db.scalar(
            select(AuthSession).where(AuthSession.id == session_id)
        )
        assert old_session is not None
        assert old_session.revoked_at is not None


@pytest.mark.parametrize("invalid_token", ["bearer", '"bearer"'])
def test_refresh_rejects_token_type_label(auth_test_client, invalid_token):
    client, _ = auth_test_client

    response = client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token": invalid_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token."


def test_access_token_can_create_project(auth_test_client):
    client, _ = auth_test_client
    email = "project-test@example.com"
    password = "test-password-1234"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Project Test User",
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert project_response.status_code == 201
    assert project_response.json()["owner_id"] == register_response.json()["id"]


def test_access_token_with_non_uuid_subject_is_unauthorized(auth_test_client):
    client, _ = auth_test_client
    token = create_access_token("not-a-uuid", "MEDICAL_WRITER")

    response = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("role", ["MEDICAL_WRITER", "ADMIN", "REVIEWER"])
def test_document_upload_allows_supported_roles(auth_test_client, role):
    client, test_session = auth_test_client
    with test_session() as db:
        user = User(
            full_name="Upload Test User",
            email=f"{role.lower()}@example.com",
            hashed_password=hash_password("test-password-1234"),
            role=role,
        )
        db.add(user)
        db.commit()
        user_id = str(user.id)

    token = create_access_token(user_id, role)
    response = client.post(
        f"/api/v1/documents/upload/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("sample.txt", b"sample text", "text/plain")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found."


@pytest.mark.parametrize(
    ("role", "path", "expected_status"),
    [
        ("ADMIN", "/api/v1/admin/dashboard", 200),
        ("ADMIN", "/api/v1/reviews/pending", 200),
        ("REVIEWER", "/api/v1/admin/dashboard", 403),
        ("REVIEWER", "/api/v1/reviews/pending", 200),
        ("MEDICAL_WRITER", "/api/v1/admin/dashboard", 403),
        ("MEDICAL_WRITER", "/api/v1/reviews/pending", 403),
    ],
)
def test_admin_and_review_role_access(
    auth_test_client,
    role,
    path,
    expected_status,
):
    client, test_session = auth_test_client
    with test_session() as db:
        user = User(
            full_name="Role Test User",
            email=f"{role.lower()}-{path.rsplit('/', 1)[-1]}@example.com",
            hashed_password=hash_password("test-password-1234"),
            role=role,
        )
        db.add(user)
        db.commit()
        user_id = str(user.id)

    token = create_access_token(user_id, role)
    response = client.get(
        path,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == expected_status


def test_document_upload_requires_access_token(auth_test_client):
    client, _ = auth_test_client

    response = client.post(
        f"/api/v1/documents/upload/{uuid.uuid4()}",
        files={"file": ("sample.txt", b"sample text", "text/plain")},
    )

    assert response.status_code == 401


def test_chunk_endpoint_creates_chunks_for_document(auth_test_client):
    client, test_session = auth_test_client
    with test_session() as db:
        user = User(
            full_name="Chunk Test User",
            email="chunk-test@example.com",
            hashed_password=hash_password("test-password-1234"),
            role="MEDICAL_WRITER",
        )
        db.add(user)
        db.flush()

        project = Project(name="Chunk Test Project", owner_id=user.id)
        db.add(project)
        db.flush()

        document = Document(
            project_id=project.id,
            title="Chunk Test Document",
            file_name="chunk-test.txt",
            file_type="txt",
            storage_path="data/raw/chunk-test.txt",
            page_count=1,
            extracted_text=(
                "Introduction\n"
                "Clinical research evaluates treatment outcomes. " * 20
            ),
            pages=[{
                "page_number": 1,
                "text": (
                    "Introduction\n"
                    "Clinical research evaluates treatment outcomes. " * 20
                ),
            }],
        )
        db.add(document)
        db.commit()
        document_id = document.id
        user_id = str(user.id)

    token = create_access_token(user_id, "MEDICAL_WRITER")
    response = client.post(
        f"/api/v1/chunks/create/{document_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["document_id"] == str(document_id)
    assert response.json()["total_chunks"] > 0


def test_chunk_endpoint_returns_404_for_missing_document(auth_test_client):
    client, test_session = auth_test_client
    with test_session() as db:
        user = User(
            full_name="Missing Document User",
            email="missing-document@example.com",
            hashed_password=hash_password("test-password-1234"),
            role="MEDICAL_WRITER",
        )
        db.add(user)
        db.commit()
        user_id = str(user.id)

    token = create_access_token(user_id, "MEDICAL_WRITER")
    response = client.post(
        "/api/v1/chunks/create/82b39c21-40fe-44a4-8722-2b823750a92a",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
