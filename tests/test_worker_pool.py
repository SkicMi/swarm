import pytest
from src.orchestrator.worker_pool import WorkerPool, WorkerPoolConfig, Worker
from src.orchestrator.agent import AgentStatus


class TestWorkerPoolConfig:
    def test_config_defaults(self):
        config = WorkerPoolConfig()
        assert config.max_workers == 5
        assert config.default_timeout == 300
        assert config.enable_model_routing is True


class TestWorker:
    def test_worker_creation(self):
        worker = Worker("w1", "nvidia/moonshotai/kimi-k2.5", "deep")
        assert worker.worker_id == "w1"
        assert worker.model == "nvidia/moonshotai/kimi-k2.5"
        assert worker.category == "deep"
        assert worker.current_task_id is None
        assert worker.status.value == "pending"

    def test_can_handle_when_idle(self):
        worker = Worker("w1", "nvidia/moonshotai/kimi-k2.5", "deep")
        assert worker.can_handle("deep", 2) is True

    def test_can_handle_when_busy(self):
        worker = Worker("w1", "nvidia/moonshotai/kimi-k2.5", "deep")
        worker.current_task_id = "task-1"
        assert worker.can_handle("deep", 2) is False


class TestWorkerPool:
    def test_pool_creation_default(self):
        pool = WorkerPool()
        assert pool.config.max_workers == 5
        assert len(pool.workers) == 5

    def test_pool_creation_custom_config(self):
        config = WorkerPoolConfig(max_workers=3)
        pool = WorkerPool(config)
        assert len(pool.workers) == 3

    def test_get_available_worker(self):
        pool = WorkerPool(WorkerPoolConfig(max_workers=3))
        worker = pool.get_available_worker(2)
        assert worker is not None

    def test_assign_and_complete_task(self):
        pool = WorkerPool(WorkerPoolConfig(max_workers=1))
        worker = pool.workers[0]
        pool.assign_task(worker, "task-1")
        assert worker.current_task_id == "task-1"
        assert worker.status.value == "running"
        pool.complete_task(worker)
        assert worker.current_task_id is None
        assert worker.status.value == "pending"

    def test_worker_stats(self):
        pool = WorkerPool(WorkerPoolConfig(max_workers=3))
        stats = pool.get_worker_stats()
        assert stats["total"] == 3
        assert stats["available"] == 3
        assert stats["busy"] == 0
