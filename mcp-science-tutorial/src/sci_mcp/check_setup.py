"""Pre-work check:  uv run sci-check   -  verifies Python, MCP SDK v2, your API key and tool-calling support."""
from __future__ import annotations

import asyncio
import importlib.metadata as md
import sys

from mcp import Client
from mcp.server.mcpserver import MCPServer

from sci_mcp.config import load_settings

OK, BAD = "[ ok ]", "[FAIL]"


async def _check_mcp() -> bool:
    srv = MCPServer("selftest")

    @srv.tool()
    def ping() -> str:
        """Return pong."""
        return "pong"

    async with Client(srv) as c:  # in-process: no subprocess, no network
        r = await c.call_tool("ping", {})
    return "pong" in r.content[0].text


async def _check_llm(s) -> tuple[bool, str]:
    from sci_mcp.client.llm import LLM

    tools = [{"type": "function", "function": {"name": "add", "description": "Add two numbers",
              "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}}]
    msg = await LLM(s).chat([{"role": "user", "content": "Use the add tool to compute 2 + 3."}], tools)
    if msg.tool_calls:
        return True, f"model requested tool: {msg.tool_calls[0].function.name}({msg.tool_calls[0].function.arguments})"
    return False, "endpoint answered but did NOT request a tool; choose a model with function-calling support"


def main() -> None:
    ok = True
    print(f"{OK if sys.version_info >= (3, 11) else BAD} Python {sys.version.split()[0]} (need >= 3.11)")
    ver = md.version("mcp")
    major_ok = ver.split(".")[0] == "2"
    ok &= major_ok
    print(f"{OK if major_ok else BAD} mcp {ver} (need v2.x)")
    mcp_ok = asyncio.run(_check_mcp())
    ok &= mcp_ok
    print(f"{OK if mcp_ok else BAD} in-process MCP server + client round trip")

    s = load_settings()
    print(f"      endpoint: {s.base_url}   model: {s.model}   key: {s.masked_key}")
    if not s.api_key:
        print(f"{BAD} LLM_API_KEY missing - copy .env.example to .env and edit it")
        ok = False
    else:
        try:
            good, detail = asyncio.run(_check_llm(s))
        except Exception as exc:
            good, detail = False, f"{type(exc).__name__}: {exc}"
        ok &= good
        print(f"{OK if good else BAD} LLM tool calling - {detail}")
    print("\nAll good - you are ready for the tutorial." if ok else "\nFix the items marked FAIL, then re-run.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
