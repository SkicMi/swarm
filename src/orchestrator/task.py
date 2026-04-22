from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    id: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"
    agent_type: str = "deep"
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_id: str
    status: str
    output: Any = None
    error: str = ""
    duration: float = 0.0
