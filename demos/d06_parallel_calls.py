"""Section 6 - Simultaneous (parallel) tool calls.

The model can return SEVERAL tool_calls in one reply. Because they are independent, the host may run them
concurrently. Each simulated instrument query takes 1.5 s, so 4 samples cost ~6 s sequentially but ~1.5 s in parallel.

    uv run demos/d06_parallel_calls.py
"""
import asyncio

from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox, stdio_module

PROMPT = (
    "Measure samples A1, A2, A3 and A4 with measure_sample using delay_s=1.5 and tell me which sample has the highest "
    "2-theta peak. Request all four measurements at the same time."
)


async def main() -> None:
    llm = LLM()
    async with Toolbox() as tb:
        await tb.connect("materials", stdio_module("sci_mcp.servers.materials_server"))
        for parallel in (False, True): # run the same prompt twice, once sequentially and once in parallel
            label = "PARALLEL (asyncio.gather)" if parallel else "SEQUENTIAL (one after another)"
            print(f"--- {label} ---")
            res = await run_agent(llm, tb, PROMPT, parallel=parallel)
            tool_time = sum(t.seconds for t in res.trace)
            print(f"tool calls: {len(res.trace)} | sum of tool time: {tool_time:.1f}s | wall-clock total: {res.seconds:.1f}s")
            print("answer:", res.answer.strip()[:300], "\n")
        print("Note: whether the model batches calls in one turn depends on the model and prompt - inspect the [turn] lines above.")


if __name__ == "__main__":
    asyncio.run(main())
