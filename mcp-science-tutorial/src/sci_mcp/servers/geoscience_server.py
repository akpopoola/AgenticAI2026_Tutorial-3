"""Geoscience MCP server (Sections 4 and 5).

Shows all three MCP primitives on one small server:
  * tools      - model-controlled actions (Gardner, impedance, reflection coefficient, TWT)
  * resources  - application-controlled read-only data (typical rock physical properties: e.g. velocities densities)
  * prompts    - user-controlled templates (interpret a reflector)

Run it standalone over stdio:   uv run sci-geo-server
"""
from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from mcp.server.mcpserver import MCPServer

from sci_mcp.physics import geo
from sci_mcp.servers._common import compute, result

mcp = MCPServer(
    "geoscience",
    instructions="Seismic rock-physics helpers. All velocities are m/s, densities g/cm3, impedance kg/m2/s.",
)

ROCK_TABLE = {
    "shale": {"vp_m_s": (2000, 4000), "rho_g_cc": (1.8, 3.3)},
    "sandstone": {"vp_m_s": (2000, 4500), "rho_g_cc": (1.6, 2.8)},
    "limestone": {"vp_m_s": (3500, 6000), "rho_g_cc": (1.9, 2.9)},
    "salt": {"vp_m_s": (4400, 5500), "rho_g_cc": (2.1, 2.6)},
}


@mcp.tool()
def gardner_density(vp_m_s: Annotated[float, Field(description="P-wave velocity in m/s (1000-8000)")]) -> dict:
    """Estimate bulk density from P-wave velocity using Gardner's relation (rho = 0.31 * Vp^0.25)."""
    return result(compute(geo.gardner_density, vp_m_s), "g/cm3", "Gardner (1974)", vp_m_s=vp_m_s)


@mcp.tool()
def acoustic_impedance(vp_m_s: float, rho_g_cc: float) -> dict:
    """Acoustic impedance Z = rho * Vp. vp in m/s, rho in g/cm3. Returns kg/m2/s."""
    return result(compute(geo.acoustic_impedance, vp_m_s, rho_g_cc), "kg/m2/s", "Z = rho*Vp", vp_m_s=vp_m_s, rho_g_cc=rho_g_cc)


@mcp.tool()
def reflection_coefficient(z_upper: float, z_lower: float) -> dict:
    """Normal-incidence reflection coefficient R = (Z2 - Z1)/(Z2 + Z1) for an interface (impedances in kg/m2/s)."""
    return result(compute(geo.reflection_coefficient, z_upper, z_lower), "dimensionless", "normal-incidence R", z_upper=z_upper, z_lower=z_lower)


@mcp.tool()
def two_way_time(depth_m: float, vp_m_s: float) -> dict:
    """Two-way travel time (ms) to a reflector at depth_m for an average velocity vp_m_s."""
    return result(compute(geo.two_way_time_ms, depth_m, vp_m_s), "ms", "TWT = 2z/v", depth_m=depth_m, vp_m_s=vp_m_s)


@mcp.resource("geo://rock-properties")
def rock_properties() -> str:
    """Typical Vp and density ranges for common lithologies (JSON)."""
    return json.dumps(ROCK_TABLE, indent=2)


@mcp.resource("geo://rock-properties/{lithology}")
def rock_property(lithology: str) -> str:
    """Typical Vp / density range for one lithology."""
    key = lithology.lower()
    if key not in ROCK_TABLE:
        raise ValueError(f"unknown lithology {lithology!r}; choose from {sorted(ROCK_TABLE)}")
    return json.dumps({key: ROCK_TABLE[key]}, indent=2)


@mcp.prompt()
def interpret_reflector(upper: str, lower: str) -> str:
    """Template: ask the model to estimate and interpret the reflection at an interface."""
    return (
        f"A seismic reflector separates {upper} (above) from {lower} (below). "
        "Look up typical properties from the geo://rock-properties resource, use the tools to compute "
        "impedances and the reflection coefficient, and state the polarity and strength of the reflection."
    )


def main() -> None:
    import sys

    if "--http" in sys.argv:  # remote-style transport: Client("http://127.0.0.1:8000/mcp")
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
