from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(StrEnum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    URGENT = "urgente"


class TaskScope(StrEnum):
    PERSONAL = "personal"
    WORK = "trabajo"
    FAMILY = "familia"
    ENTREPRENEURSHIP = "emprendimiento"


class AuditAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"

