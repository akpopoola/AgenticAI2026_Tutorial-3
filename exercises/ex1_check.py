"""Part A self-check (no LLM, no API key):  uv run exercises/ex1_check.py [path/to/server.py]"""
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

DEFAULT = Path(__file__).with_name("porosity_exercise_server.py")


async def main(server: Path) -> int:
    failures = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failures
        failures += not cond
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    async with Client(StdioServerParameters(command=sys.executable, args=[str(server)])) as c:
        tools = {t.name: t for t in (await c.list_tools()).tools}
        check("tool 'density_porosity' is registered", "density_porosity" in tools)
        doc = (tools["density_porosity"].description or "") if "density_porosity" in tools else ""
        check("docstring was rewritten (mentions formula and units)", "TODO" not in doc and ("rho_matrix" in doc or "matrix" in doc.lower()) and "fraction" in doc.lower())
        r = await c.call_tool("density_porosity", {"rhob": 2.35})
        text = r.content[0].text
        check("rhob=2.35 -> phi 0.1818", (not r.is_error) and "0.1818" in text, f"(got: {text[:60]!r})")
        r = await c.call_tool("density_porosity", {"rhob": 2.40, "rho_matrix": 2.71, "rho_fluid": 1.1})
        check("limestone matrix -> phi 0.1925", (not r.is_error) and "0.1925" in r.content[0].text)
        r = await c.call_tool("density_porosity", {"rhob": 5.0})
        check("rhob=5.0 is rejected with is_error and a helpful message", r.is_error and "1.0" in r.content[0].text, f"(got: {r.content[0].text[:80]!r})")
    print("\nAll checks passed - move on to Part B." if not failures else f"\n{failures} check(s) failing - keep going.")
    return failures


if __name__ == "__main__":
    sys.exit(asyncio.run(main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT)))
