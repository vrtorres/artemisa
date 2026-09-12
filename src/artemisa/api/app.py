from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker

from artemisa.api.routes import router
from artemisa.database import create_database_engine, create_session_factory
from artemisa.domain.errors import InvalidTaskOperationError, TaskNotFoundError


def create_app(session_factory: sessionmaker[Session] | None = None) -> FastAPI:
    app = FastAPI(
        title="Artemisa API",
        version="0.2.0",
        description="API REST para la gestión auditada de tareas.",
    )
    app.state.session_factory = session_factory or create_session_factory(
        create_database_engine()
    )
    app.include_router(router, prefix="/api/v1")

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found(
        request: Request, exc: TaskNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidTaskOperationError)
    async def invalid_operation(
        request: Request, exc: InvalidTaskOperationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def invalid_value(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    return app
