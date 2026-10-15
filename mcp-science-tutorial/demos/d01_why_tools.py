"""Section 1 - Why tool calling for scientific agents.

Same question, asked 4 times WITHOUT tools vs. WITH a validated tool.
Ground truth comes from the tested physics code in sci_mcp.physics.

    uv run demos/d01_why_tools.py
"""
import asyncio
import re

from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox, stdio_module
from sci_mcp.physics.materials import scherrer_crystallite_size

QUESTION = (
    "Cu K-alpha X-rays (1.5406 angstrom) give an XRD peak at 2-theta = 38.2 degrees with an instrument-corrected "
    "FWHM of 0.35 degrees. Use the Scherrer equation with K = 0.9. Reply with ONLY the crystallite size in nm, as a number."
)


def first_number(text: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", text or "")
    return float(m.group()) if m else None


async def main() -> None:
    llm = LLM()
    truth = scherrer_crystallite_size(0.35, 38.2)
    print(f"Ground truth (tested code): {truth:.3f} nm\n")

    print("WITHOUT tools - the model 'does the maths in its head':")
    for i in range(4):
        msg = await llm.chat([{"role": "system", "content": "You are a helpful assistant."},
                              {"role": "user", "content": QUESTION}])
        v = first_number(msg.content)
        err = f"{abs(v - truth) / truth * 100:5.1f}% off" if v is not None else "no number"
        print(f"  run {i + 1}: {msg.content.strip()[:40]!r:44} -> {err}")

    print("\nWITH an MCP tool (materials server):")
    async with Toolbox() as tb:
        await tb.connect("materials", stdio_module("sci_mcp.servers.materials_server"))
        res = await run_agent(llm, tb, QUESTION.replace("Reply with ONLY the crystallite size in nm, as a number.", "Give the crystallite size in nm."))
        print(f"  answer: {res.answer.strip()}")
        print(f"  tool outputs: {[t.output.replace(chr(10), ' ')[:120] for t in res.trace]}")


if __name__ == "__main__":
    asyncio.run(main())
