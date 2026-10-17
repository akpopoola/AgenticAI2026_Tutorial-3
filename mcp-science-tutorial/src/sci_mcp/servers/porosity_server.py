"""Reference solution for the Section 7 exercise: a porosity MCP server over a small well log.

Run standalone over stdio:   uv run sci-porosity-server
"""
from __future__ import annotations

from typing import Annotated

import pandas as pd
from pydantic import Field

from mcp.server.mcpserver import MCPServer

from sci_mcp.physics import porosity as phys
from sci_mcp.servers._common import DATA_DIR, compute, result

mcp = MCPServer(
    "porosity",
    instructions="Petrophysics helpers over a sample well log. Porosity values are fractions (0-1).",
)

LOG_PATH = DATA_DIR / "well_log_sample.csv"


def _log() -> pd.DataFrame:
    return pd.read_csv(LOG_PATH)


@mcp.resource("welllog://sample")
def welllog_sample() -> str:
    """The sample well log as CSV (depth_m, RHOB_g_cc, DT_us_ft, NPHI_frac, RT_ohm_m)."""
    return LOG_PATH.read_text()


@mcp.tool()
def get_log_sample(depth_m: Annotated[float, Field(description="Depth in metres; the nearest logged sample is returned")]) -> dict:
    """Return the log readings (RHOB, DT, NPHI, RT) nearest to a depth."""
    df = _log()
    row = df.iloc[(df["depth_m"] - depth_m).abs().argmin()]
    return {k: float(v) for k, v in row.items()}


@mcp.tool()
def density_porosity(
    rhob: Annotated[float, Field(description="Bulk density from the density log, g/cm3")],
    rho_matrix: Annotated[float, Field(description="Matrix density, g/cm3 (sandstone 2.65, limestone 2.71, dolomite 2.87)")] = 2.65,
    rho_fluid: Annotated[float, Field(description="Pore-fluid density, g/cm3 (fresh water 1.0, brine ~1.1)")] = 1.0,
) -> dict:
    """Density porosity phi = (rho_matrix - rhob) / (rho_matrix - rho_fluid), returned as a fraction."""
    phi = compute(phys.density_porosity, rhob, rho_matrix, rho_fluid)
    return result(phi, "fraction", "density porosity", rhob=rhob, rho_matrix=rho_matrix, rho_fluid=rho_fluid)


@mcp.tool()
def sonic_porosity(
    dt_us_ft: Annotated[float, Field(description="Sonic slowness from the sonic log, microseconds per foot (us/ft)")],
    dt_matrix: Annotated[float, Field(description="Matrix slowness (sandstone), microseconds per foot (us/ft)")] = 55.5,
    dt_fluid: Annotated[float, Field(description="Pore-fluid slowness (fresh water), microseconds per foot (us/ft)")] = 189.0,
    ) -> dict:
    """Wyllie time-average sonic porosity (fraction) from slowness in microseconds/ft."""
    return result(compute(phys.sonic_porosity_wyllie, dt_us_ft, dt_matrix, dt_fluid), "fraction", "Wyllie time-average", dt_us_ft=dt_us_ft)


@mcp.tool()
def archie_water_saturation(
    phi: Annotated[float, Field(description="Porosity, fraction (0-1)")],
    rt_ohm_m: Annotated[float, Field(description="True resistivity, ohm-m")],
    rw_ohm_m: Annotated[float, Field(description="Formation-water resistivity, ohm-m")],
    a: Annotated[float, Field(description="Lithology factor (typically 0.5-2.0)")] = 1.0,
    m: Annotated[float, Field(description="Saturation exponent (typically 1.5-3.0)")]= 2.0,
    n: Annotated[float, Field(description="Resistivity exponent (typically 1.5-3.0)")]= 2.0,
) -> dict:
    """Archie water saturation Sw (fraction) from porosity, true resistivity and formation-water resistivity."""
    return result(compute(phys.archie_water_saturation, phi, rt_ohm_m, rw_ohm_m, a, m, n), "fraction", "Archie", phi=phi, rt_ohm_m=rt_ohm_m, rw_ohm_m=rw_ohm_m)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
