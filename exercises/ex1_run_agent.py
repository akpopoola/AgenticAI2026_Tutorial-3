"""Part B: point the LLM agent at YOUR server.

    uv run exercises/ex1_run_agent.py                       # your exercise server, default questions
    uv run exercises/ex1_run_agent.py "your own question"   # custom question
    uv run exercises/ex1_run_agent.py --solution            # run the reference solution instead
"""
import asyncio
import sys
from pathlib import Path

from mcp import StdioServerParameters

from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox

HERE = Path(__file__).resolve().parent
QUESTIONS = [
    "What is the density porosity at 2540 m? Read the log sample first, then use the sandstone matrix and fresh water.",
    "Compare the porosity at 2520 m and 2580 m, and say which interval is the better reservoir. Fetch both log samples at the same time.",
    "A colleague reports RHOB = 235 at 2520 m. What is the porosity?",  # unit mistake: watch the error handling!
]


async def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    solution = "--solution" in sys.argv
    script = (HERE.parent / "solutions" if solution else HERE) / "porosity_exercise_server.py"
    llm = LLM()
    async with Toolbox() as tb:
        await tb.connect("por", StdioServerParameters(command=sys.executable, args=[str(script)]))
        for q in args or QUESTIONS:
            print(f"\nQ: {q}")
            res = await run_agent(llm, tb, q)
            print("A:", res.answer.strip())


if __name__ == "__main__":
    asyncio.run(main())
