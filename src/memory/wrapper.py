from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryQuery:
    query: str
    limit: int = 5
    wing: str | None = None
    room: str | None = None


@dataclass
class MemoryResult:
    text: str
    similarity: float
    wing: str
    room: str
    metadata: dict[str, Any]


class MemoryWrapper:
    def __init__(self):
        self._cache: dict[str, list[MemoryResult]] = {}

    def search(self, query: str, limit: int = 5) -> list[MemoryResult]:
        return []

    def add(self, content: str, wing: str, room: str) -> str:
        return ""

    def query_kg(self, entity: str) -> list[dict[str, Any]]:
        return []

    def add_fact(self, subject: str, predicate: str, object: str) -> None:
        pass

    def get_stats(self) -> dict[str, Any]:
        return {"total_memories": 0, "wings": []}
