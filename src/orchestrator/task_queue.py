from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .task import Task, TaskPriority, TaskResult


class QueueStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class TaskQueueConfig:
    max_size: int = 100
    default_timeout: int = 300
    enable_priorities: bool = True


class TaskQueue:
    def __init__(self, config: TaskQueueConfig | None = None):
        self.config = config or TaskQueueConfig()
        self._queue: list[Task] = []
        self._active: dict[str, Task] = {}
        self._completed: dict[str, TaskResult] = {}
        self._status = QueueStatus.IDLE

    def enqueue(self, task: Task) -> bool:
        if len(self._queue) >= self.config.max_size:
            return False
        self._queue.append(task)
        self._queue.sort(key=lambda t: t.priority.value, reverse=True)
        return True

    def dequeue(self) -> Task | None:
        if not self._queue:
            return None
        return self._queue.pop(0)

    def start_task(self, task_id: str) -> None:
        task = self.dequeue()
        if task:
            self._active[task_id] = task

    def complete_task(self, task_id: str, result: TaskResult) -> None:
        if task_id in self._active:
            del self._active[task_id]
        self._completed[task_id] = result

    def get_stats(self) -> dict[str, Any]:
        return {
            "queued": len(self._queue),
            "active": len(self._active),
            "completed": len(self._completed),
        }
