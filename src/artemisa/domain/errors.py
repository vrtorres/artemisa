class ArtemisaError(Exception):
    """Base class for expected domain errors."""


class TaskNotFoundError(ArtemisaError):
    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task {task_id} was not found")
        self.task_id = task_id


class InvalidTaskOperationError(ArtemisaError):
    """Raised when an operation conflicts with the current task state."""

