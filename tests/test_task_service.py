from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from artemisa.domain.enums import (
    AuditAction,
    TaskPriority,
    TaskScope,
    TaskStatus,
)
from artemisa.domain.errors import InvalidTaskOperationError, TaskNotFoundError
from artemisa.repositories.audit_repository import AuditRepository
from artemisa.services.task_service import TaskService


def test_task_lifecycle_is_audited(session: Session) -> None:
    service = TaskService(session)

    task = service.create_task("  Preparar informe  ", "  Resumen semanal ", actor="ana")
    service.update_task(task.id, description="Resumen mensual", actor="ana")
    service.complete_task(task.id, actor="ana")
    service.delete_task(task.id, actor="ana")

    assert task.title == "Preparar informe"
    assert task.status == TaskStatus.COMPLETED
    assert task.deleted_at is not None
    assert task.version == 4
    assert [entry.action for entry in AuditRepository(session).for_task(task.id)] == [
        AuditAction.CREATED,
        AuditAction.UPDATED,
        AuditAction.COMPLETED,
        AuditAction.DELETED,
    ]
    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)


def test_list_filters_pending_tasks_and_searches_text(session: Session) -> None:
    service = TaskService(session)
    first = service.create_task("Comprar semillas", "Para el huerto")
    second = service.create_task("Enviar informe", "Finanzas")
    service.complete_task(second.id)

    pending = service.list_tasks(status=TaskStatus.PENDING)
    matches = service.list_tasks(search="HUERTO")

    assert [task.id for task in pending] == [first.id]
    assert [task.id for task in matches] == [first.id]


def test_rejects_empty_title_and_duplicate_completion(session: Session) -> None:
    service = TaskService(session)
    with pytest.raises(ValueError):
        service.create_task("   ")

    task = service.create_task("Tarea")
    service.complete_task(task.id)
    with pytest.raises(InvalidTaskOperationError):
        service.complete_task(task.id)


def test_noop_update_does_not_create_an_audit_entry(session: Session) -> None:
    service = TaskService(session)
    task = service.create_task("Tarea", "Detalle")

    service.update_task(task.id, title="Tarea", description="Detalle")

    entries = AuditRepository(session).for_task(task.id)
    assert len(entries) == 1
    assert task.version == 1


def test_task_planning_fields_are_created_updated_and_audited(session: Session) -> None:
    service = TaskService(session)
    first_due_date = datetime(2026, 9, 10, 18, 0, tzinfo=UTC)
    second_due_date = datetime(2026, 9, 12, 12, 0, tzinfo=UTC)

    task = service.create_task(
        "Entregar propuesta",
        priority=TaskPriority.HIGH,
        due_date=first_due_date,
        scope=TaskScope.ENTREPRENEURSHIP,
        actor="ana",
    )

    assert task.priority == TaskPriority.HIGH
    assert task.due_date == first_due_date
    assert task.scope == TaskScope.ENTREPRENEURSHIP

    service.update_task(
        task.id,
        priority=TaskPriority.URGENT,
        due_date=second_due_date,
        scope=TaskScope.WORK,
        actor="ana",
    )

    assert task.priority == TaskPriority.URGENT
    assert task.due_date == second_due_date
    assert task.scope == TaskScope.WORK
    assert task.version == 2
    audit = AuditRepository(session).for_task(task.id)
    assert audit[-1].changes["priority"] == {"old": "alta", "new": "urgente"}


def test_list_filters_by_priority_and_scope(session: Session) -> None:
    service = TaskService(session)
    matching = service.create_task(
        "Llamar cliente",
        priority=TaskPriority.URGENT,
        scope=TaskScope.WORK,
    )
    service.create_task(
        "Comprar alimentos",
        priority=TaskPriority.URGENT,
        scope=TaskScope.FAMILY,
    )

    tasks = service.list_tasks(priority=TaskPriority.URGENT, scope=TaskScope.WORK)

    assert [task.id for task in tasks] == [matching.id]
