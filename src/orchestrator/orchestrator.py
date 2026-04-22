from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .agent import AgentConfig, AgentResult, AgentStatus
from .task import Task, TaskPriority, TaskResult


class ModelType(Enum):
    KIMI_K25 = "nvidia/moonshotai/kimi-k2.5"
    NEMOTRON_NANO = "nvidia/nvidia/nemotron-3-nano-30b-a3b"
    NEMOTRON_SUPER = "nvidia/nvidia/nemotron-3-super-120b-a12b"
    NEMOTRON_4 = "nvidia/nvidia/nemotron-4-340b-instruct"
    GEMMA_4 = "nvidia/google/gemma-4-31b-it"
    LLAMA_VISION = "nvidia/meta/llama-3.2-11b-vision-instruct"
    MISTRAL_LARGE = "nvidia/mistralai/mistral-large-3-675b-instruct-2512"
    LLAMA_MAVERICK = "nvidia/meta/llama-4-maverick-17b-128e-instruct"
    BIG_PICKLE = "opencode/big-pickle"


MODEL_MAPPING = {
    "orchestrator": ModelType.BIG_PICKLE,
    "small": ModelType.NEMOTRON_NANO,
    "medium": ModelType.KIMI_K25,
    "large": ModelType.NEMOTRON_4,
}


def get_model_for_task(task_size: str) -> str:
    model = MODEL_MAPPING.get(task_size, ModelType.KIMI_K25)
    return model.value


def get_orchestrator_model() -> str:
    return ModelType.BIG_PICKLE.value


@dataclass
class OrchestratorConfig:
    model: str = field(default_factory=get_orchestrator_model)
    max_concurrent: int = 5
    task_timeout: int = 300
    enable_self_healing: bool = True
    max_retries: int = 3
    fallback_models: list[str] = field(default_factory=lambda: [
        ModelType.KIMI_K25.value,
        ModelType.NEMOTRON_NANO.value,
    ])


class SwarmOrchestrator:
    def __init__(self, config: OrchestratorConfig | None = None):
        self.config = config or OrchestratorConfig()
        self.active_tasks: dict[str, Task] = {}
        self.completed_tasks: dict[str, TaskResult] = {}
        self._rate_limited = False

    def create_task(self, task_id: str, description: str, priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            status="pending",
        )
        self.active_tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self.active_tasks.get(task_id)

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.active_tasks.values() if t.status == "pending"]

    def get_task_model(self, task: Task) -> str:
        if task.priority == TaskPriority.CRITICAL:
            return ModelType.NEMOTRON_4.value
        elif task.priority == TaskPriority.HIGH:
            return ModelType.KIMI_K25.value
        elif task.priority == TaskPriority.LOW:
            return ModelType.NEMOTRON_NANO.value
        return ModelType.KIMI_K25.value

    def complete_task(self, task_id: str, result: TaskResult) -> None:
        self.completed_tasks[task_id] = result
        if task_id in self.active_tasks:
            self.active_tasks[task_id].status = result.status

    def get_stats(self) -> dict[str, Any]:
        return {
            "total": len(self.active_tasks),
            "pending": sum(1 for t in self.active_tasks.values() if t.status == "pending"),
            "completed": len(self.completed_tasks),
            "rate_limited": self._rate_limited,
        }

    def set_rate_limited(self, limited: bool) -> None:
        self._rate_limited = limited

    def get_fallback_model(self) -> str:
        if self.config.fallback_models:
            return self.config.fallback_models[0]
        return ModelType.KIMI_K25.value
