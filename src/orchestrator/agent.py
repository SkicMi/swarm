from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentConfig:
    model: str = "opencode/big-pickle"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 300


@dataclass
class AgentResult:
    task_id: str
    status: AgentStatus
    output: Any = None
    error: str = ""
    duration: float = 0.0
    model: str = ""
