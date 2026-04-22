"""
Sentry Configuration for Project Swarm
====================================
Error tracking and performance monitoring.

Environment Variables:
- SENTRY_DSN: Your Sentry DSN URL
- ENVIRONMENT: production/staging/development
- SWARM_VERSION: Current version
"""

import os
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


class SentryConfig:
    """Sentry configuration manager."""

    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: Optional[str] = None,
        sample_rate: float = 1.0,
        traces_sample_rate: float = 0.1,
    ):
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.sample_rate = sample_rate
        self.traces_sample_rate = traces_sample_rate
        self._initialized = False

    def init(self) -> None:
        """Initialize Sentry with all integrations."""
        if not self.dsn:
            return

        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            integrations=[
                AioHttpIntegration(),
                LoggingIntegration(level="WARNING"),
            ],
            traces_sample_rate=self.traces_sample_rate,
            sample_rate=self.sample_rate,
            release=os.getenv("SWARM_VERSION", "0.1.0"),
            send_default_pii=False,
            attach_stacktrace=True,
            instrumenter="otelp",
        )
        self._initialized = True

    def capture_exception(self, error: Exception, **extra) -> None:
        """Capture an exception with extra context."""
        if not self._initialized:
            return
        with sentry_sdk.push_scope() as scope:
            for key, value in extra.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)

    def capture_message(self, message: str, level: str = "info", **extra) -> None:
        """Capture a message with level and context."""
        if not self._initialized:
            return
        with sentry_sdk.push_scope() as scope:
            for key, value in extra.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)

    def set_context(self, name: str, data: dict) -> None:
        """Set context for all future events."""
        if not self._initialized:
            return
        sentry_sdk.set_context(name, data)

    def set_user(self, user_id: str, **kwargs) -> None:
        """Set user context."""
        if not self._initialized:
            return
        sentry_sdk.set_user({"id": user_id, **kwargs})

    def add_breadcrumb(self, message: str, category: str = "general", **kwargs) -> None:
        """Add breadcrumb for transaction tracking."""
        if not self._initialized:
            return
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            data=kwargs,
        )


_sentry_config: Optional[SentryConfig] = None


def get_sentry() -> SentryConfig:
    global _sentry_config
    if _sentry_config is None:
        _sentry_config = SentryConfig()
    return _sentry_config


def init_sentry(
    dsn: Optional[str] = None,
    environment: Optional[str] = None,
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
) -> SentryConfig:
    global _sentry_config
    _sentry_config = SentryConfig(
        dsn=dsn,
        environment=environment,
        sample_rate=sample_rate,
        traces_sample_rate=traces_sample_rate,
    )
    _sentry_config.init()
    return _sentry_config
