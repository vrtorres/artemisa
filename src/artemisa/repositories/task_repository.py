from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from artemisa.domain.enums import TaskPriority, TaskScope, TaskStatus
from artemisa.models.task import Task


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        return task

    def get(self, task_id: int, *, include_deleted: bool = False) -> Task | None:
        statement = select(Task).where(Task.id == task_id)
        if not include_deleted:
            statement = statement.where(Task.deleted_at.is_(None))
        return self.session.scalar(statement)

    def list(
        self,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        scope: TaskScope | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[Task]:
        statement: Select[tuple[Task]] = select(Task)
        if not include_deleted:
            statement = statement.where(Task.deleted_at.is_(None))
        if status is not None:
            statement = statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if scope is not None:
            statement = statement.where(Task.scope == scope)
        if search:
            pattern = f"%{search.strip().lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Task.title).like(pattern),
                    func.lower(func.coalesce(Task.description, "")).like(pattern),
                )
            )
        statement = statement.order_by(Task.created_at.desc(), Task.id.desc())
        statement = statement.offset(max(offset, 0)).limit(min(max(limit, 1), 500))
        return self.session.scalars(statement).all()

    def flush(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        return task

