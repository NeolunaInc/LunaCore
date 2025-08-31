import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BaseEvent(BaseModel):
    """Base event class with common fields."""

    type: str = "event"
    data: Any = None
    id: str = str(uuid.uuid4())
    timestamp: datetime = datetime.utcnow()
    correlation_id: str | None = None


class TaskStartedEvent(BaseEvent):
    """Event emitted when a task starts."""

    type: str = "task.started"
    task_id: str
    agent_id: str


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task completes successfully."""

    type: str = "task.completed"
    task_id: str
    result: Any


class TaskFailedEvent(BaseEvent):
    """Event emitted when a task fails."""

    type: str = "task.failed"
    task_id: str
    error: str


class EscalationNeededEvent(BaseEvent):
    """Event emitted when escalation is needed."""

    type: str = "escalation.needed"
    task_id: str
    reason: str
