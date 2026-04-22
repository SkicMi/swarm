from dataclasses import dataclass
from typing import Any

from .task import Task, TaskResult


@dataclass
class CoordinatorConfig:
    max_concurrent_tasks: int = 5
    task_timeout: int = 300
    enable_self_healing: bool = True
    max_retries: int = 3


class Coordinator:
    def __init__(self, config: CoordinatorConfig | None = None):
        self.config = config or CoordinatorConfig()
        self.tasks: dict[str, Task] = {}
        self.results: dict[str, TaskResult] = {}
        self._running = False

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def get_ready_tasks(self) -> list[Task]:
        ready = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue
            deps_met = all(
                self.tasks.get(dep_id).status == "completed"
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )
            if deps_met:
                ready.append(task)
        return ready

    def mark_completed(self, task_id: str, result: TaskResult) -> None:
        self.results[task_id] = result
        if task_id in self.tasks:
            self.tasks[task_id].status = result.status

    def get_stats(self) -> dict[str, Any]:
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "running": sum(1 for t in self.tasks.values() if t.status == "running"),
            "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "failed": sum(1 for t in self.tasks.values() if t.status == "failed"),
        }
