from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import logging

from .task import Task, TaskPriority, TaskResult

logger = logging.getLogger(__name__)


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


@dataclass
class HealingMetrics:
    total_heals: int = 0
    rate_limit_heals: int = 0
    error_heals: int = 0
    timeout_heals: int = 0


class SelfHealer:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.metrics = HealingMetrics()
        self._failure_counts: dict[str, int] = {}
        self._retry_counts: dict[str, int] = {}

    def calculate_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)

    def should_retry(self, task_id: str, error_type: str) -> bool:
        retry_count = self._retry_counts.get(task_id, 0)
        if retry_count >= self.max_retries:
            logger.warning(f"Task {task_id} exceeded max retries ({self.max_retries})")
            return False
        return True

    def record_failure(self, task_id: str, error_type: str) -> None:
        self._failure_counts[task_id] = self._failure_counts.get(task_id, 0) + 1

        if error_type == "rate_limit":
            self.metrics.rate_limit_heals += 1
        elif error_type == "timeout":
            self.metrics.timeout_heals += 1
        else:
            self.metrics.error_heals += 1

        self.metrics.total_heals += 1
        logger.info(f"Recorded {error_type} failure for task {task_id}")

    def record_retry(self, task_id: str) -> None:
        self._retry_counts[task_id] = self._retry_counts.get(task_id, 0) + 1

    def get_failure_count(self, task_id: str) -> int:
        return self._failure_counts.get(task_id, 0)

    def get_retry_count(self, task_id: str) -> int:
        return self._retry_counts.get(task_id, 0)

    def reset_task(self, task_id: str) -> None:
        self._failure_counts.pop(task_id, None)
        self._retry_counts.pop(task_id, None)

    def get_metrics(self) -> dict[str, Any]:
        return {
            "total_heals": self.metrics.total_heals,
            "rate_limit_heals": self.metrics.rate_limit_heals,
            "error_heals": self.metrics.error_heals,
            "timeout_heals": self.metrics.timeout_heals,
        }


class SwarmOrchestratorWithHealing(SwarmOrchestrator):
    def __init__(self, config: OrchestratorConfig | None = None):
        super().__init__(config)
        self._healer = SelfHealer(
            max_retries=config.max_retries if config else 3,
        )
        self._healing_enabled = config.enable_self_healing if config else True

    @property
    def healer(self) -> SelfHealer:
        return self._healer

    def is_healing_enabled(self) -> bool:
        return self._healing_enabled

    def handle_failure(
        self,
        task_id: str,
        error: Exception,
        error_type: str = "error",
    ) -> bool:
        if not self._healing_enabled:
            return False

        if not self._healer.should_retry(task_id, error_type):
            return False

        self._healer.record_failure(task_id, error_type)
        self._healer.record_retry(task_id)

        delay = self._healer.calculate_delay(
            self._healer.get_retry_count(task_id)
        )
        logger.info(
            f"Scheduling retry for task {task_id} "
            f"after {delay:.1f}s (attempt {self._healer.get_retry_count(task_id)})"
        )
        return True

    def get_healing_status(self) -> dict[str, Any]:
        return {
            "enabled": self._healing_enabled,
            "metrics": self._healer.get_metrics(),
        }

    def get_health_status(self) -> dict[str, Any]:
        base_stats = self.get_stats()
        healing_status = self.get_healing_status()
        return {
            **base_stats,
            **healing_status,
            "healthy": (
                healing_status["metrics"]["total_heals"] < 10
                and not self._rate_limited
            ),
        }