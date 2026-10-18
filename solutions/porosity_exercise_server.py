"""SOLUTION - Section 7 exercise. Compare with exercises/porosity_exercise_server.py."""
from __future__ import annotations

from typing import Annotated

import pandas as pd
from pydantic import Field

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from sci_mcp.servers._common import DATA_DIR

mcp = MCPServer("porosity-exercise", instructions="Porosity helpers over a sample well log. Porosity is a fraction (0-1).")


@mcp.tool()
def get_log_sample(depth_m: Annotated[float, Field(description="Depth in metres; nearest logged sample is returned")]) -> dict:
    """Return the log readings (RHOB g/cm3, DT us/ft, NPHI fraction, RT ohm-m) nearest to a depth."""
    df = pd.read_csv(DATA_DIR / "well_log_sample.csv")
    row = df.iloc[(df["depth_m"] - depth_m).abs().argmin()]
    return {k: float(v) for k, v in row.items()}


@mcp.tool()
def density_porosity(
    rhob: Annotated[float, Field(description="Bulk density from the density log, g/cm3")],
    rho_matrix: Annotated[float, Field(description="Matrix density, g/cm3 (sandstone 2.65, limestone 2.71, dolomite 2.87)")] = 2.65,
    rho_fluid: Annotated[float, Field(description="Pore-fluid density, g/cm3 (fresh water 1.0, brine ~1.1)")] = 1.0,
) -> dict:
    """Density porosity: phi = (rho_matrix - rhob) / (rho_matrix - rho_fluid). Returns a fraction between 0 and 1."""
    if not 1.0 <= rhob <= 3.2:
        raise ToolError(f"rhob={rhob} g/cm3 is outside the plausible log range 1.0-3.2; check units")
    if rho_matrix <= rho_fluid:
        raise ToolError("rho_matrix must be greater than rho_fluid")
    phi = min(max((rho_matrix - rhob) / (rho_matrix - rho_fluid), 0.0), 1.0)
    return {"value": round(phi, 4), "units": "fraction", "method": "density porosity",
            "inputs": {"rhob": rhob, "rho_matrix": rho_matrix, "rho_fluid": rho_fluid}}


# ---- If you have more time, Stretch goal (Part C) --------------------------------------------------------------------------
@mcp.tool()
def sonic_porosity(dt_us_ft: float, dt_matrix: float = 55.5, dt_fluid: float = 189.0) -> dict:
    """Wyllie time-average sonic porosity (fraction) from slowness in microseconds per foot (us/ft)."""
    if dt_us_ft <= 0:
        raise ToolError("dt_us_ft must be positive")
    phi = min(max((dt_us_ft - dt_matrix) / (dt_fluid - dt_matrix), 0.0), 1.0)
    return {"value": round(phi, 4), "units": "fraction", "method": "Wyllie time-average", "inputs": {"dt_us_ft": dt_us_ft}}


if __name__ == "__main__":
    mcp.run(transport="stdio")
