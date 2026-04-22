from dataclasses import dataclass, field
from typing import Any

from .agent import AgentConfig, AgentResult, AgentStatus
from .orchestrator import ModelType


@dataclass
class WorkerPoolConfig:
    max_workers: int = 5
    default_timeout: int = 300
    enable_model_routing: bool = True


class Worker:
    def __init__(self, worker_id: str, model: str, category: str = "deep"):
        self.worker_id = worker_id
        self.model = model
        self.category = category
        self.current_task_id: str | None = None
        self.status = AgentStatus.PENDING

    def can_handle(self, task_category: str, priority: int) -> bool:
        if self.current_task_id is not None:
            return False
        required_category = self._get_required_category(priority)
        return self.category == required_category

    def _get_required_category(self, priority: int) -> str:
        if priority >= 3:
            return "ultrabrain"
        elif priority >= 2:
            return "deep"
        return "quick"


class WorkerPool:
    def __init__(self, config: WorkerPoolConfig | None = None):
        self.config = config or WorkerPoolConfig()
        self.workers: list[Worker] = []
        self._worker_counter = 0
        self._initialize_workers()

    def _initialize_workers(self) -> None:
        worker_models = [
            ("nvidia/moonshotai/kimi-k2.5", "ultrabrain"),
            ("nvidia/nvidia/nemotron-4-340b-instruct", "deep"),
            ("nvidia/nvidia/nemotron-3-nano-30b-a3b", "quick"),
            ("nvidia/google/gemma-4-31b-it", "deep"),
            ("nvidia/nvidia/nemotron-3-super-120b-a12b", "deep"),
        ]
        for model, category in worker_models[:self.config.max_workers]:
            self._worker_counter += 1
            self.workers.append(Worker(f"worker-{self._worker_counter}", model, category))

    def get_available_worker(self, priority: int) -> Worker | None:
        for worker in self.workers:
            if worker.can_handle(worker.category, priority):
                return worker
        return None

    def assign_task(self, worker: Worker, task_id: str) -> None:
        worker.current_task_id = task_id
        worker.status = AgentStatus.RUNNING

    def complete_task(self, worker: Worker) -> None:
        worker.current_task_id = None
        worker.status = AgentStatus.PENDING

    def get_worker_stats(self) -> dict[str, Any]:
        return {
            "total": len(self.workers),
            "available": sum(1 for w in self.workers if w.current_task_id is None),
            "busy": sum(1 for w in self.workers if w.current_task_id is not None),
        }
