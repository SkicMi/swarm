from dataclasses import dataclass, field
from typing import Any

from .agent import AgentConfig, AgentResult, AgentStatus
from .task import Task, TaskPriority, TaskResult


@dataclass
class CoordinatorConfig:
    max_queue_size: int = 100
    default_timeout: int = 300
    enable_priorities: bool = True


class Coordinator:
    def __init__(self, config: CoordinatorConfig | None = None):
        self.config = config or CoordinatorConfig()
        self._tasks: dict[str, Task] = {}
        self._results: dict[str, TaskResult] = {}
        self._queue: list[str] = []

    def add_task(self, task: Task) -> None:
        self._tasks[task.id] = task
        self._queue.append(task.id)

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def get_ready_tasks(self) -> list[Task]:
        return [t for t in self._tasks.values() if t.status == "pending"]

    def mark_completed(self, task_id: str, result: TaskResult) -> None:
        self._results[task_id] = result

    def get_stats(self) -> dict[str, Any]:
        return {"total": len(self._tasks), "pending": len(self._queue)}
