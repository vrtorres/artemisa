from __future__ import annotations

from typing import Any

from artemisa.domain.enums import AuditAction
from artemisa.models.audit_log import AuditLog
from artemisa.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def record(
        self,
        *,
        task_id: int,
        action: AuditAction,
        changes: dict[str, Any],
        actor: str,
    ) -> AuditLog:
        return self.repository.add(
            AuditLog(task_id=task_id, action=action, changes=changes, actor=actor)
        )

