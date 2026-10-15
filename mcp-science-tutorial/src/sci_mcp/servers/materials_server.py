"""Materials-science MCP server (Section 5 and the parallel-call demo in Section 6).

Run standalone over stdio:   uv run sci-materials-server
"""
from __future__ import annotations

import asyncio

from mcp.server.mcpserver import MCPServer

from sci_mcp.physics import materials as mat
from sci_mcp.servers._common import compute, result

mcp = MCPServer(
    "materials",
    instructions="XRD and alloy helpers. Angles in degrees 2-theta, lengths in angstrom unless stated.",
)


@mcp.tool()
def bragg_d_spacing(two_theta_deg: float, wavelength_A: float = 1.5406, order: int = 1) -> dict:
    """Bragg's law: d-spacing (angstrom) from a diffraction peak position. Default radiation is Cu K-alpha."""
    return result(compute(mat.bragg_d_spacing, two_theta_deg, wavelength_A, order), "angstrom", "Bragg", two_theta_deg=two_theta_deg, wavelength_A=wavelength_A, order=order)


@mcp.tool()
def cubic_lattice_parameter(d_A: float, h: int, k: int, l: int) -> dict:
    """Cubic lattice parameter a (angstrom) from a d-spacing and Miller indices (h k l)."""
    return result(compute(mat.cubic_lattice_parameter, d_A, h, k, l), "angstrom", "a = d*sqrt(h2+k2+l2)", d_A=d_A, hkl=[h, k, l])


@mcp.tool()
def scherrer_crystallite_size(fwhm_deg: float, two_theta_deg: float, wavelength_A: float = 1.5406, K: float = 0.9) -> dict:
    """Scherrer crystallite size (nm) from peak FWHM (degrees 2-theta). Instrument broadening must already be removed."""
    return result(compute(mat.scherrer_crystallite_size, fwhm_deg, two_theta_deg, wavelength_A, K), "nm", "Scherrer", fwhm_deg=fwhm_deg, two_theta_deg=two_theta_deg, K=K)


@mcp.tool()
def vegard_lattice_parameter(a_A: float, a_B: float, fraction_B: float) -> dict:
    """Vegard's-law lattice parameter (angstrom) of a binary solid solution with fraction_B of component B."""
    return result(compute(mat.vegard_lattice_parameter, a_A, a_B, fraction_B), "angstrom", "Vegard", a_A=a_A, a_B=a_B, fraction_B=fraction_B)


@mcp.tool()
async def measure_sample(sample_id: str, delay_s: float = 1.0) -> dict:
    """Simulate a slow instrument query (e.g. a lab database or diffractometer queue). Used in the parallel-call demo."""
    await asyncio.sleep(max(0.0, min(delay_s, 5.0)))
    peak = 38.2 + (sum(map(ord, sample_id)) % 50) / 10  # deterministic fake 2-theta peak
    return {"sample_id": sample_id, "peak_two_theta_deg": round(peak, 2), "fwhm_deg": 0.35, "note": "synthetic data for teaching"}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
