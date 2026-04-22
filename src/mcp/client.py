from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class MCPConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPConnection:
    name: str
    state: MCPConnectionState = MCPConnectionState.DISCONNECTED
    url: str = ""
    last_error: str = ""


class MCPClient:
    def __init__(self):
        self._connections: dict[str, MCPConnection] = {}
        self._tools: dict[str, Callable] = {}

    def add_connection(self, name: str, url: str) -> MCPConnection:
        conn = MCPConnection(name=name, url=url)
        self._connections[name] = conn
        return conn

    def get_connection(self, name: str) -> MCPConnection | None:
        return self._connections.get(name)

    def register_tool(self, name: str, handler: Callable) -> None:
        self._tools[name] = handler

    def call_tool(self, tool_name: str, **params: Any) -> Any:
        handler = self._tools.get(tool_name)
        if not handler:
            raise ValueError(f"Tool {tool_name} not found")
        return handler(**params)

    def list_connections(self) -> list[str]:
        return list(self._connections.keys())

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
