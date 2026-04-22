"""
Prometheus Metrics for Project Swarm
======================================
Metrics collection and exposition.
"""

import os
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest, CONTENT_TYPE_LATEST
from aiohttp import web


PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))



class SwarmMetrics:
    """All metrics for Project Swarm."""

    def __init__(self):
        self.agent_tasks_total = Counter(
            "swarm_agent_tasks_total",
            "Total number of tasks processed by agent",
            ["agent_type", "status"],
        )
        self.agent_task_duration = Histogram(
            "swarm_agent_task_duration_seconds",
            "Task processing duration",
            ["agent_type", "task_type"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 300],
        )
        self.active_agents = Gauge(
            "swarm_active_agents",
            "Number of currently active agents",
            ["agent_type"],
        )
        self.mcp_requests_total = Counter(
            "swarm_mcp_requests_total",
            "Total MCP requests",
            ["mcp_server", "method", "status"],
        )
        self.mcp_request_duration = Histogram(
            "swarm_mcp_request_duration_seconds",
            "MCP request duration",
            ["mcp_server", "method"],
        )
        self.memory_queries_total = Counter(
            "swarm_memory_queries_total",
            "Total memory queries",
            ["memory_type", "status"],
        )
        self.memory_vectors_stored = Gauge(
            "swarm_memory_vectors_stored",
            "Number of vectors in memory",
            ["memory_type"],
        )
        self.task_queue_size = Gauge(
            "swarm_task_queue_size",
            "Current task queue size",
            ["priority"],
        )
        self.orchestrator_cycles_total = Counter(
            "swarm_orchestrator_cycles_total",
            "Total orchestration cycles",
            ["status"],
        )
        self.github_operations_total = Counter(
            "swarm_github_operations_total",
            "Total GitHub operations",
            ["operation", "status"],
        )
        self.errors_total = Counter(
            "swarm_errors_total",
            "Total errors",
            ["error_type", "component"],
        )
        self.swarm_info = Info("swarm", "Project Swarm information")
        self.swarm_info.info({
            "version": os.getenv("SWARM_VERSION", "0.1.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
        })


_metrics: Optional[SwarmMetrics] = None


def get_metrics() -> SwarmMetrics:
    global _metrics
    if _metrics is None:
        _metrics = SwarmMetrics()
    return _metrics



async def metrics_handler(request: web.Request) -> web.Response:
    return web.Response(
        body=generate_latest(),
        content_type=CONTENT_TYPE_LATEST,
    )


def setup_metrics_routes(app: web.Application):
    app.router.add_get("/metrics", metrics_handler)
    app.router.add_get("/health", health_handler)



async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="OK")



class MetricTimer:
    def __init__(self, histogram: Histogram, labels: Dict[str, str]):
        self.histogram = histogram
        self.labels = labels

    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, *args):
        import time
        duration = time.time() - self.start
        self.histogram.labels(**self.labels).observe(duration)
