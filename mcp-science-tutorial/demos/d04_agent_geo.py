"""Section 4 - Use the MCP server from an LLM agent.

    uv run demos/d04_agent_geo.py
"""
import asyncio

from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox, stdio_module

PROMPT = (
    "A seismic reflector at 1500 m depth separates shale (Vp = 2800 m/s) above from sandstone (Vp = 3600 m/s) below. "
    "Estimate densities with Gardner, compute both impedances and the reflection coefficient, and the two-way time "
    "using the shale velocity. Is the reflection a positive or negative polarity?"
)


async def main() -> None:
    async with Toolbox() as tb:
        await tb.connect("geo", stdio_module("sci_mcp.servers.geoscience_server"))
        res = await run_agent(LLM(), tb, PROMPT)
    print("\nANSWER:\n" + res.answer)
    print(f"\n({res.turns} model turns, {len(res.trace)} tool calls, {res.seconds:.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())
