import pytest
from src.orchestrator import (
    SwarmOrchestrator,
    OrchestratorConfig,
    ModelType,
    get_model_for_task,
    get_orchestrator_model,
    TaskPriority,
)
from src.orchestrator.task import Task


class TestModelType:
    def test_model_values(self):
        assert ModelType.KIMI_K25.value == "nvidia/moonshotai/kimi-k2.5"
        assert ModelType.NEMOTRON_NANO.value == "nvidia/nvidia/nemotron-3-nano-30b-a3b"
        assert ModelType.NEMOTRON_4.value == "nvidia/nvidia/nemotron-4-340b-instruct"
        assert ModelType.BIG_PICKLE.value == "opencode/big-pickle"


class TestGetModelForTask:
    def test_orchestrator_model(self):
        assert get_orchestrator_model() == "opencode/big-pickle"

    def test_small_task(self):
        model = get_model_for_task("small")
        assert model == "nvidia/nvidia/nemotron-3-nano-30b-a3b"

    def test_medium_task(self):
        model = get_model_for_task("medium")
        assert model == "nvidia/moonshotai/kimi-k2.5"

    def test_large_task(self):
        model = get_model_for_task("large")
        assert model == "nvidia/nvidia/nemotron-4-340b-instruct"

    def test_unknown_task(self):
        model = get_model_for_task("unknown")
        assert model == "nvidia/moonshotai/kimi-k2.5"


class TestOrchestratorConfig:
    def test_config_defaults(self):
        config = OrchestratorConfig()
        assert config.model == "opencode/big-pickle"
        assert config.max_concurrent == 5
        assert config.task_timeout == 300
        assert config.enable_self_healing is True
        assert len(config.fallback_models) == 2


class TestSwarmOrchestrator:
    def test_orchestrator_creation(self):
        orch = SwarmOrchestrator()
        assert orch.active_tasks == {}
        assert orch.completed_tasks == {}
        assert orch._rate_limited is False

    def test_create_task(self):
        orch = SwarmOrchestrator()
        task = orch.create_task("t1", "Test task", TaskPriority.MEDIUM)
        assert task.id == "t1"
        assert task.description == "Test task"
        assert task.status == "pending"

    def test_get_task(self):
        orch = SwarmOrchestrator()
        orch.create_task("t1", "Test")
        task = orch.get_task("t1")
        assert task is not None
        assert task.id == "t1"

    def test_get_task_not_found(self):
        orch = SwarmOrchestrator()
        task = orch.get_task("nonexistent")
        assert task is None

    def test_get_pending_tasks(self):
        orch = SwarmOrchestrator()
        orch.create_task("t1", "Test1")
        orch.create_task("t2", "Test2", TaskPriority.HIGH)
        pending = orch.get_pending_tasks()
        assert len(pending) == 2

    def test_get_task_model_critical(self):
        orch = SwarmOrchestrator()
        task = orch.create_task("t1", "Critical task", TaskPriority.CRITICAL)
        model = orch.get_task_model(task)
        assert model is not None
        assert model != ""

    def test_get_task_model_high(self):
        orch = SwarmOrchestrator()
        task = orch.create_task("t1", "High priority", TaskPriority.HIGH)
        model = orch.get_task_model(task)
        assert model is not None
        assert model != ""

    def test_get_task_model_low(self):
        orch = SwarmOrchestrator()
        task = orch.create_task("t1", "Low priority", TaskPriority.LOW)
        model = orch.get_task_model(task)
        assert model is not None
        assert model != ""

    def test_complete_task(self):
        orch = SwarmOrchestrator()
        orch.create_task("t1", "Test")
        from src.orchestrator.task import TaskResult
        result = TaskResult(task_id="t1", status="completed")
        orch.complete_task("t1", result)
        assert orch.active_tasks["t1"].status == "completed"

    def test_get_stats(self):
        orch = SwarmOrchestrator()
        orch.create_task("t1", "Test")
        stats = orch.get_stats()
        assert stats["total"] == 1
        assert stats["pending"] == 1
        assert stats["rate_limited"] is False

    def test_set_rate_limited(self):
        orch = SwarmOrchestrator()
        orch.set_rate_limited(True)
        assert orch._rate_limited is True

    def test_get_fallback_model(self):
        orch = SwarmOrchestrator()
        model = orch.get_fallback_model()
        assert model is not None
        assert model != ""
