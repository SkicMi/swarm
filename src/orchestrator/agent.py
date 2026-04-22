from dataclasses import dataclass
from enum import Enum
from typing import Any


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentConfig:
    name: str
    model: str = "opencode/big-pickle"
    category: str = "deep"
    timeout: int = 300
    max_retries: int = 3
    temperature: float = 0.7
    system_prompt: str = ""
    tools: list[str] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []


@dataclass
class AgentResult:
    status: AgentStatus
    output: str = ""
    error: str = ""
    duration: float = 0.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
