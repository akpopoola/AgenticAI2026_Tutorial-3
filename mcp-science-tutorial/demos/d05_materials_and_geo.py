"""Section 5 - Materials science and geoscience examples, one agent, two MCP servers.

    uv run demos/d05_materials_and_geo.py
"""
import asyncio

from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox, stdio_module

PROMPTS = {
    "materials (XRD)": (
        "An aluminium sample shows a Cu K-alpha peak at 2-theta = 38.47 degrees, indexed as (111), with FWHM 0.30 degrees. "
        "Give the d-spacing, the cubic lattice parameter and the Scherrer crystallite size."
    ),
    "materials (alloy)": "A solid solution is 30% B in A, with a_A = 4.05 and a_B = 3.61 angstrom. Predict the lattice parameter (Vegard).",
    "geoscience": (
        "Use the rock-properties resource: what are typical Vp and density for limestone? Then find the reflection coefficient "
        "for shale (Vp 2800 m/s, rho 2.3 g/cm3) above limestone (Vp 5200 m/s, rho 2.65 g/cm3)."
    ),
}
# Rock-properties resource first:

async def main() -> None:
    llm = LLM()
    async with Toolbox() as tb:
        await tb.connect("materials", stdio_module("sci_mcp.servers.materials_server"))
        await tb.connect("geo", stdio_module("sci_mcp.servers.geoscience_server"))
        print(f"Agent sees {len(tb.openai_tools)} tools from {len(tb.clients)} servers\n")
        rock_properties = await tb.read_resource("geo", "geo://rock-properties")
        for title, prompt in PROMPTS.items():
            print(f"=== {title} ===")
            if title == "geoscience":
                prompt = f"{prompt}\n\nRock-properties resource (JSON):\n{rock_properties}"
            res = await run_agent(llm, tb, prompt)
            print(res.answer.strip(), "\n")


if __name__ == "__main__":
    asyncio.run(main())
