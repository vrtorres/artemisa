from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.orm import Session

from artemisa.domain.enums import AuditAction, TaskPriority, TaskScope, TaskStatus
from artemisa.domain.errors import InvalidTaskOperationError, TaskNotFoundError
from artemisa.models.base import utc_now
from artemisa.models.task import Task
from artemisa.repositories.audit_repository import AuditRepository
from artemisa.repositories.task_repository import TaskRepository
from artemisa.services.audit_service import AuditService


class _Unset:
    pass


UNSET = _Unset()


class TaskService:
    """Task use cases. The caller owns commit/rollback of the session."""

    def __init__(self, session: Session) -> None:
        self.repository = TaskRepository(session)
        self.audit = AuditService(AuditRepository(session))

    def create_task(
        self,
        title: str,
        description: str | None = None,
        *,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime | None = None,
        scope: TaskScope = TaskScope.PERSONAL,
        actor: str = "system",
    ) -> Task:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Task title cannot be empty")
        task = self.repository.add(
            Task(
                title=clean_title,
                description=self._clean_description(description),
                priority=priority,
                due_date=due_date,
                scope=scope,
            )
        )
        self.audit.record(
            task_id=task.id,
            action=AuditAction.CREATED,
            changes={
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "scope": task.scope.value,
            },
            actor=actor,
        )
        return task

    def get_task(self, task_id: int) -> Task:
        return self._require_task(task_id)

    def list_tasks(
        self,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        scope: TaskScope | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        return self.repository.list(
            status=status,
            priority=priority,
            scope=scope,
            search=search,
            offset=offset,
            limit=limit,
        )

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        description: str | None | _Unset = UNSET,
        priority: TaskPriority | None = None,
        due_date: datetime | None | _Unset = UNSET,
        scope: TaskScope | None = None,
        actor: str = "system",
    ) -> Task:
        task = self._require_task(task_id)
        changes: dict[str, dict[str, str | None]] = {}
        if title is not None:
            clean_title = title.strip()
            if not clean_title:
                raise ValueError("Task title cannot be empty")
            if clean_title != task.title:
                changes["title"] = {"old": task.title, "new": clean_title}
                task.title = clean_title
        if description is not UNSET:
            clean_description = self._clean_description(description)
            if clean_description != task.description:
                changes["description"] = {"old": task.description, "new": clean_description}
                task.description = clean_description
        if priority is not None and priority != task.priority:
            changes["priority"] = {"old": task.priority.value, "new": priority.value}
            task.priority = priority
        if due_date is not UNSET:
            new_due_date = due_date if isinstance(due_date, datetime) else None
            if new_due_date != task.due_date:
                changes["due_date"] = {
                    "old": task.due_date.isoformat() if task.due_date else None,
                    "new": new_due_date.isoformat() if new_due_date else None,
                }
                task.due_date = new_due_date
        if scope is not None and scope != task.scope:
            changes["scope"] = {"old": task.scope.value, "new": scope.value}
            task.scope = scope
        if changes:
            task.version += 1
            self.repository.flush(task)
            self.audit.record(
                task_id=task.id,
                action=AuditAction.UPDATED,
                changes=changes,
                actor=actor,
            )
        return task

    def complete_task(self, task_id: int, *, actor: str = "system") -> Task:
        task = self._require_task(task_id)
        if task.status == TaskStatus.COMPLETED:
            raise InvalidTaskOperationError(f"Task {task_id} is already completed")
        completed_at = utc_now()
        old_status = task.status
        task.status = TaskStatus.COMPLETED
        task.completed_at = completed_at
        task.version += 1
        self.repository.flush(task)
        self.audit.record(
            task_id=task.id,
            action=AuditAction.COMPLETED,
            changes={
                "status": {"old": old_status, "new": task.status},
                "completed_at": completed_at.isoformat(),
            },
            actor=actor,
        )
        return task

    def delete_task(self, task_id: int, *, actor: str = "system") -> Task:
        task = self._require_task(task_id)
        deleted_at = utc_now()
        task.deleted_at = deleted_at
        task.version += 1
        self.repository.flush(task)
        self.audit.record(
            task_id=task.id,
            action=AuditAction.DELETED,
            changes={"deleted_at": deleted_at.isoformat()},
            actor=actor,
        )
        return task

    def _require_task(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    @staticmethod
    def _clean_description(description: str | None | _Unset) -> str | None:
        if description is UNSET:
            return None
        if description is None:
            return None
        value = description.strip()
        return value or None

