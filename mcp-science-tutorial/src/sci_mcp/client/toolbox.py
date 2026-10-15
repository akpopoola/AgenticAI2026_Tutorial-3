"""Bridge between MCP servers and an OpenAI-style tool-calling loop.

MCP SDK v2 pieces used here:
    from mcp import Client, StdioServerParameters
    async with Client(<stdio params | url | MCPServer instance>) as client: ...
    await client.list_tools() / client.call_tool(name, args) / client.read_resource(uri)
"""
from __future__ import annotations

import sys
from contextlib import AsyncExitStack
from typing import Any

from mcp import Client, StdioServerParameters

SEP = "__"  # OpenAI function names allow [a-zA-Z0-9_-]; we namespace as <server>__<tool>


def stdio_module(module: str, *args: str) -> StdioServerParameters:
    """Launch `python -m <module>` with the *same interpreter* (works in uv, venv, Windows, Colab)."""
    return StdioServerParameters(command=sys.executable, args=["-m", module, *args])


class Toolbox:
    """Connects to one or many MCP servers and exposes their tools to an LLM."""

    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self.clients: dict[str, Client] = {}
        self._tool_index: dict[str, tuple[str, str]] = {}  # openai name -> (server, mcp tool name)
        self._openai_tools: list[dict[str, Any]] = []

    async def __aenter__(self) -> "Toolbox":
        await self._stack.__aenter__()
        return self

    async def __aexit__(self, *exc) -> None:
        await self._stack.__aexit__(*exc)

    async def connect(self, name: str, target: Any) -> None:
        """`target` may be StdioServerParameters, a 'http://.../mcp' URL, or an in-process MCPServer."""
        client = await self._stack.enter_async_context(Client(target))
        self.clients[name] = client
        for tool in (await client.list_tools()).tools:
            fn_name = f"{name}{SEP}{tool.name}"
            self._tool_index[fn_name] = (name, tool.name)
            self._openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": fn_name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    },
                }
            )

    @property
    def openai_tools(self) -> list[dict[str, Any]]:
        return self._openai_tools

    async def call(self, fn_name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
        """Execute a tool call requested by the model. Returns (text, is_error)."""
        if fn_name not in self._tool_index:
            return f"Unknown tool {fn_name!r}", True
        server, tool = self._tool_index[fn_name]
        result = await self.clients[server].call_tool(tool, arguments)
        text = "\n".join(getattr(c, "text", "") for c in result.content if getattr(c, "type", "") == "text")
        return text, bool(result.is_error)

    async def read_resource(self, server: str, uri: str) -> str:
        res = await self.clients[server].read_resource(uri)
        return "\n".join(getattr(c, "text", "") for c in res.contents)
