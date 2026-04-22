import pytest
from src.orchestrator.task_queue import TaskQueue, TaskQueueConfig
from src.orchestrator.task import Task, TaskPriority, TaskResult
from src.orchestrator.worker_pool import WorkerPool, WorkerPoolConfig


class TestTaskQueueConfig:
    def test_config_defaults(self):
        config = TaskQueueConfig()
        assert config.max_size == 100
        assert config.enable_priority is True


class TestTaskQueue:
    def test_queue_creation(self):
        queue = TaskQueue()
        assert queue.config.max_size == 100
        assert queue.get_pending_count() == 0

    def test_enqueue(self):
        queue = TaskQueue()
        task = Task(id="t1", description="Test task")
        result = queue.enqueue(task)
        assert result is True
        assert queue.get_pending_count() == 1

    def test_enqueue_full_queue(self):
        config = TaskQueueConfig(max_size=2)
        queue = TaskQueue(config=config)
        queue.enqueue(Task(id="t1", description="Test 1"))
        queue.enqueue(Task(id="t2", description="Test 2"))
        result = queue.enqueue(Task(id="t3", description="Test 3"))
        assert result is False

    def test_priority_ordering(self):
        queue = TaskQueue()
        queue.enqueue(Task(id="low", description="Low", priority=TaskPriority.LOW))
        queue.enqueue(Task(id="high", description="High", priority=TaskPriority.HIGH))
        queue.enqueue(Task(id="medium", description="Medium", priority=TaskPriority.MEDIUM))
        first = queue.dequeue()
        assert first.id == "high"
        second = queue.dequeue()
        assert second.id == "medium"

    def test_dequeue(self):
        queue = TaskQueue()
        queue.enqueue(Task(id="t1", description="Test"))
        task = queue.dequeue()
        assert task is not None
        assert task.id == "t1"

    def test_start_task(self):
        pool = WorkerPool(WorkerPoolConfig(max_workers=5))
        queue = TaskQueue(worker_pool=pool)
        task = Task(id="t1", description="Test", priority=TaskPriority.HIGH)
        queue.enqueue(task)
        result = queue.start_task(task)
        assert result is True

    def test_complete_task(self):
        pool = WorkerPool(WorkerPoolConfig(max_workers=1))
        queue = TaskQueue(worker_pool=pool)
        task = Task(id="t1", description="Test", priority=TaskPriority.MEDIUM)
        queue.enqueue(task)
        queue.start_task(task)
        result = TaskResult(task_id="t1", status="completed")
        queue.complete_task("t1", result)
        assert "t1" in queue.results

    def test_stats(self):
        queue = TaskQueue(WorkerPool(WorkerPoolConfig(max_workers=2)))
        stats = queue.get_stats()
        assert "queued" in stats
        assert "active" in stats
        assert "completed" in stats
        assert "workers" in stats
