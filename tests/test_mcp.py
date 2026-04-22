import pytest
from src.mcp.client import MCPClient, MCPConnection, MCPConnectionState


class TestMCPConnectionState:
    def test_states(self):
        assert MCPConnectionState.DISCONNECTED.value == "disconnected"
        assert MCPConnectionState.CONNECTING.value == "connecting"
        assert MCPConnectionState.CONNECTED.value == "connected"
        assert MCPConnectionState.ERROR.value == "error"


class TestMCPConnection:
    def test_connection_defaults(self):
        conn = MCPConnection(name="test")
        assert conn.name == "test"
        assert conn.state == MCPConnectionState.DISCONNECTED


class TestMCPClient:
    def test_client_creation(self):
        client = MCPClient()
        assert client._connections == {}
        assert client._tools == {}

    def test_add_connection(self):
        client = MCPClient()
        conn = client.add_connection("test", "http://localhost:8080")
        assert conn.name == "test"
        assert "test" in client.list_connections()

    def test_get_connection(self):
        client = MCPClient()
        client.add_connection("test", "http://localhost:8080")
        conn = client.get_connection("test")
        assert conn is not None
        assert conn.name == "test"

    def test_get_connection_not_found(self):
        client = MCPClient()
        conn = client.get_connection("nonexistent")
        assert conn is None

    def test_register_tool(self):
        client = MCPClient()
        def hello(name: str) -> str:
            return f"Hello, {name}"
        client.register_tool("hello", hello)
        assert "hello" in client.list_tools()

    def test_call_tool(self):
        client = MCPClient()
        def add(a: int, b: int) -> int:
            return a + b
        client.register_tool("add", add)
        result = client.call_tool("add", a=2, b=3)
        assert result == 5

    def test_call_tool_not_found(self):
        client = MCPClient()
        with pytest.raises(ValueError, match="not found"):
            client.call_tool("nonexistent")
