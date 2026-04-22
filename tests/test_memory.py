import pytest
from src.memory.wrapper import MemoryWrapper, MemoryQuery, MemoryResult


class TestMemoryQuery:
    def test_query_defaults(self):
        query = MemoryQuery(query="test search")
        assert query.query == "test search"
        assert query.limit == 5
        assert query.wing is None
        assert query.room is None


class TestMemoryResult:
    def test_result_creation(self):
        result = MemoryResult(
            text="test content",
            similarity=0.9,
            wing="test-wing",
            room="test-room",
            metadata={},
        )
        assert result.text == "test content"
        assert result.similarity == 0.9


class TestMemoryWrapper:
    def test_wrapper_creation(self):
        wrapper = MemoryWrapper()
        assert wrapper._cache == {}

    def test_search_returns_empty(self):
        wrapper = MemoryWrapper()
        results = wrapper.search("test")
        assert results == []

    def test_add_returns_empty_string(self):
        wrapper = MemoryWrapper()
        result = wrapper.add("test content", "wing", "room")
        assert result == ""
    def test_query_kg_returns_empty(self):
        wrapper = MemoryWrapper()
        results = wrapper.query_kg("Entity")
        assert results == []
    def test_get_stats(self):
        wrapper = MemoryWrapper()
        stats = wrapper.get_stats()
        assert stats["total_memories"] == 0
        assert stats["wings"] == []
