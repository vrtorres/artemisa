from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemisa.domain.enums import TaskPriority, TaskScope, TaskStatus
from artemisa.models.base import Base, TimestampMixin


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_status_deleted_at", "status", "deleted_at"),
        Index("ix_tasks_priority_scope", "priority", "scope"),
        Index("ix_tasks_due_date", "due_date"),
        Index("ix_tasks_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda enum: [item.value for item in enum]),
        default=TaskStatus.PENDING,
        nullable=False,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=lambda enum: [item.value for item in enum]),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scope: Mapped[TaskScope] = mapped_column(
        Enum(TaskScope, values_callable=lambda enum: [item.value for item in enum]),
        default=TaskScope.PERSONAL,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="task", passive_deletes=True
    )


from artemisa.models.audit_log import AuditLog

