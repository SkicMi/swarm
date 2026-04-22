import pytest
from src.orchestrator.agent import AgentConfig, AgentResult, AgentStatus
from src.orchestrator.task import Task, TaskPriority, TaskResult
from src.orchestrator.coordinator import Coordinator, CoordinatorConfig


class TestAgentStatus:
    def test_agent_status_values(self):
        assert AgentStatus.PENDING.value == "pending"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"
        assert AgentStatus.CANCELLED.value == "cancelled"


class TestAgentConfig:
    def test_agent_config_defaults(self):
        config = AgentConfig(name="test")
        assert config.name == "test"
        assert config.model == "opencode/big-pickle"
        assert config.category == "deep"
        assert config.timeout == 300
        assert config.max_retries == 3


class TestAgentResult:
    def test_agent_result_defaults(self):
        result = AgentResult(status=AgentStatus.COMPLETED)
        assert result.status == AgentStatus.COMPLETED
        assert result.output == ""
        assert result.error == ""
        assert result.duration == 0.0


class TestTaskPriority:
    def test_priority_values(self):
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.MEDIUM.value == 2
        assert TaskPriority.HIGH.value == 3
        assert TaskPriority.CRITICAL.value == 4


class TestTask:
    def test_task_defaults(self):
        task = Task(id="t1", description="Test task")
        assert task.id == "t1"
        assert task.description == "Test task"
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == "pending"


class TestTaskResult:
    def test_task_result(self):
        result = TaskResult(task_id="t1", status="completed", output="done")
        assert result.task_id == "t1"
        assert result.status == "completed"
        assert result.output == "done"


class TestCoordinatorConfig:
    def test_config_defaults(self):
        config = CoordinatorConfig()
        assert config.max_concurrent_tasks == 5
        assert config.task_timeout == 300
        assert config.enable_self_healing is True


class TestCoordinator:
    def test_coordinator_creation(self):
        coord = Coordinator()
        assert coord.tasks == {}
        assert coord.results == {}
        assert coord._running is False

    def test_add_task(self):
        coord = Coordinator()
        task = Task(id="t1", description="Test")
        coord.add_task(task)
        assert "t1" in coord.tasks

    def test_get_task(self):
        coord = Coordinator()
        task = Task(id="t1", description="Test")
        coord.add_task(task)
        retrieved = coord.get_task("t1")
        assert retrieved is not None
        assert retrieved.id == "t1"

    def test_get_task_not_found(self):
        coord = Coordinator()
        result = coord.get_task("nonexistent")
        assert result is None

    def test_get_ready_tasks_empty(self):
        coord = Coordinator()
        ready = coord.get_ready_tasks()
        assert ready == []

    def test_mark_completed(self):
        coord = Coordinator()
        task = Task(id="t1", description="Test")
        coord.add_task(task)
        result = TaskResult(task_id="t1", status="completed")
        coord.mark_completed("t1", result)
        assert coord.tasks["t1"].status == "completed"

    def test_get_stats(self):
        coord = Coordinator()
        coord.add_task(Task(id="t1", description="Test", status="completed"))
        coord.add_task(Task(id="t2", description="Test2", status="pending"))
        stats = coord.get_stats()
        assert stats["total"] == 2
        assert stats["completed"] == 1
        assert stats["pending"] == 1
