from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from artemisa.domain.enums import TaskPriority, TaskScope, TaskStatus


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    scope: TaskScope = TaskScope.PERSONAL


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    scope: TaskScope | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    scope: TaskScope
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    version: int


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str
