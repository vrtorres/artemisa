from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Path, Query, Response, status

from artemisa.api.dependencies import get_task_service
from artemisa.api.schemas import (
    ErrorResponse,
    HealthResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from artemisa.domain.enums import TaskPriority, TaskScope, TaskStatus
from artemisa.services.task_service import TaskService

router = APIRouter()
ServiceDependency = Annotated[TaskService, Depends(get_task_service)]
ActorHeader = Annotated[str, Header(alias="X-Actor", min_length=1, max_length=100)]
TaskId = Annotated[int, Path(ge=1)]
not_found_response = {404: {"model": ErrorResponse}}


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(
    payload: TaskCreate,
    service: ServiceDependency,
    actor: ActorHeader = "api",
) -> object:
    return service.create_task(**payload.model_dump(), actor=actor)


@router.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    service: ServiceDependency,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: TaskPriority | None = None,
    scope: TaskScope | None = None,
    search: Annotated[str | None, Query(max_length=255)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> object:
    return service.list_tasks(
        status=task_status,
        priority=priority,
        scope=scope,
        search=search,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    responses=not_found_response,
    tags=["tasks"],
)
def get_task(task_id: TaskId, service: ServiceDependency) -> object:
    return service.get_task(task_id)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    responses=not_found_response,
    tags=["tasks"],
)
def update_task(
    task_id: TaskId,
    payload: TaskUpdate,
    service: ServiceDependency,
    actor: ActorHeader = "api",
) -> object:
    changes = payload.model_dump(exclude_unset=True)
    return service.update_task(task_id, **changes, actor=actor)


@router.post(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    responses={**not_found_response, 409: {"model": ErrorResponse}},
    tags=["tasks"],
)
def complete_task(
    task_id: TaskId,
    service: ServiceDependency,
    actor: ActorHeader = "api",
) -> object:
    return service.complete_task(task_id, actor=actor)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=not_found_response,
    tags=["tasks"],
)
def delete_task(
    task_id: TaskId,
    service: ServiceDependency,
    actor: ActorHeader = "api",
) -> Response:
    service.delete_task(task_id, actor=actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
