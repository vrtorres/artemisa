from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from artemisa.api.app import create_app
from artemisa.models import Base
from artemisa.repositories.audit_repository import AuditRepository


@pytest.fixture
def api() -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with TestClient(create_app(factory)) as client:
        yield client, factory
    engine.dispose()


def test_health_check(api: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = api

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_crud_and_completion(api: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, factory = api

    created = client.post(
        "/api/v1/tasks",
        headers={"X-Actor": "ana"},
        json={
            "title": "  Preparar informe  ",
            "description": "Resumen semanal",
            "priority": "alta",
            "due_date": "2026-09-20T18:00:00Z",
            "scope": "trabajo",
        },
    )

    assert created.status_code == 201
    task = created.json()
    task_id = task["id"]
    assert task["title"] == "Preparar informe"
    assert task["status"] == "pending"
    assert task["priority"] == "alta"
    assert task["scope"] == "trabajo"
    assert task["version"] == 1

    listed = client.get(
        "/api/v1/tasks",
        params={"status": "pending", "priority": "alta", "scope": "trabajo"},
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [task_id]

    updated = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers={"X-Actor": "ana"},
        json={"description": None, "due_date": None, "priority": "urgente"},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] is None
    assert updated.json()["due_date"] is None
    assert updated.json()["priority"] == "urgente"
    assert updated.json()["version"] == 2

    completed = client.post(
        f"/api/v1/tasks/{task_id}/complete",
        headers={"X-Actor": "ana"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"] is not None

    duplicate = client.post(f"/api/v1/tasks/{task_id}/complete")
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == f"Task {task_id} is already completed"

    with factory() as session:
        entries = AuditRepository(session).for_task(task_id)
        assert [entry.actor for entry in entries] == ["ana", "ana", "ana"]

    deleted = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"X-Actor": "ana"},
    )
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing = client.get(f"/api/v1/tasks/{task_id}")
    assert missing.status_code == 404
    assert missing.json() == {"detail": f"Task {task_id} was not found"}


def test_validation_and_failed_writes_are_rolled_back(
    api: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = api

    empty_title = client.post("/api/v1/tasks", json={"title": "   "})
    invalid_priority = client.post(
        "/api/v1/tasks",
        json={"title": "Tarea", "priority": "critical"},
    )
    unknown_field = client.post(
        "/api/v1/tasks",
        json={"title": "Tarea", "unexpected": True},
    )

    assert empty_title.status_code == 422
    assert empty_title.json() == {"detail": "Task title cannot be empty"}
    assert invalid_priority.status_code == 422
    assert unknown_field.status_code == 422
    assert client.get("/api/v1/tasks").json() == []


def test_openapi_documents_versioned_routes(
    api: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = api

    schema = client.get("/openapi.json")

    assert schema.status_code == 200
    paths = schema.json()["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/tasks" in paths
    assert "/api/v1/tasks/{task_id}" in paths
    assert "/api/v1/tasks/{task_id}/complete" in paths
