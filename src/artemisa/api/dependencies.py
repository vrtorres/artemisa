from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from artemisa.database import session_scope
from artemisa.services.task_service import TaskService


def get_session(request: Request) -> Iterator[Session]:
    """Abre una transacción por petición y delega commit/rollback a session_scope."""
    with session_scope(request.app.state.session_factory) as session:
        yield session


def get_task_service(session: Annotated[Session, Depends(get_session)]) -> TaskService:
    return TaskService(session)
