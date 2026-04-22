from dataclasses import dataclass, field
from typing import Any
from collections import deque

from .task import Task, TaskResult, TaskPriority
from .worker_pool import WorkerPool


@dataclass
class TaskQueueConfig:
    max_size: int = 100
    enable_priority: bool = True


class TaskQueue:
    def __init__(self, config: TaskQueueConfig | None = None, worker_pool: WorkerPool | None = None):
        self.config = config or TaskQueueConfig()
        self.worker_pool = worker_pool or WorkerPool()
        self.queue: deque[Task] = deque()
        self.active_tasks: dict[str, Task] = {}
        self.results: dict[str, TaskResult] = {}

    def enqueue(self, task: Task) -> bool:
        if len(self.queue) >= self.config.max_size:
            return False
        if self.config.enable_priority:
            self._insert_by_priority(task)
        else:
            self.queue.append(task)
        return True

    def _insert_by_priority(self, task: Task) -> None:
        inserted = False
        for i, existing in enumerate(self.queue):
            if task.priority.value > existing.priority.value:
                self.queue.insert(i, task)
                inserted = True
                break
        if not inserted:
            self.queue.append(task)

    def dequeue(self) -> Task | None:
        if not self.queue:
            return None
        return self.queue.popleft()

    def start_task(self, task: Task) -> bool:
        worker = self.worker_pool.get_available_worker(task.priority.value)
        if worker is None:
            return False
        self.worker_pool.assign_task(worker, task.id)
        self.active_tasks[task.id] = task
        task.status = "running"
        return True

    def complete_task(self, task_id: str, result: TaskResult) -> None:
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        self.results[task_id] = result
        for worker in self.worker_pool.workers:
            if worker.current_task_id == task_id:
                self.worker_pool.complete_task(worker)
                break

    def get_pending_count(self) -> int:
        return len(self.queue)

    def get_stats(self) -> dict[str, Any]:
        return {
            "queued": len(self.queue),
            "active": len(self.active_tasks),
            "completed": len(self.results),
            "workers": self.worker_pool.get_worker_stats(),
        }
