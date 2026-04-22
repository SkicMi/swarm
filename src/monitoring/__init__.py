"""
Monitoring Module for Project Swarm
===================================
Sentry + Prometheus integration.
"""

import os

from .sentry import init_sentry, get_sentry, SentryConfig
from .prometheus import (
    get_metrics,
    setup_metrics_routes,
    MetricTimer,
    PROMETHEUS_PORT,
)

MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"


def init_monitoring(
    sentry_dsn: str | None = None,
    sentry_env: str | None = None,
    enable_sentry: bool = True,
) -> None:
    """Initialize all monitoring components."""
    if not MONITORING_ENABLED:
        return

    if enable_sentry and sentry_dsn:
        init_sentry(
            dsn=sentry_dsn,
            environment=sentry_env or os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        )

    get_metrics()


__all__ = [
    "init_monitoring",
    "init_sentry",
    "get_sentry",
    "get_metrics",
    "setup_metrics_routes",
    "MetricTimer",
    "PROMETHEUS_PORT",
    "SentryConfig",
]
