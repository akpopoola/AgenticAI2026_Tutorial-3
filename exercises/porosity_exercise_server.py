"""EXERCISE - Section 7. Complete the TODOs in density_porosity, then run: uv run exercises/ex1_check.py"""
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
    """TODO 1: replace this docstring. The model decides WHEN to call the tool from this text -
    state the formula, the units, and what is returned."""
    # TODO 2: validate inputs. Raise ToolError("...helpful message...") if rhob is outside 1.0-3.2 g/cm3
    #         or if rho_matrix <= rho_fluid. (The model reads the message and can retry.)
    # TODO 3: compute phi = (rho_matrix - rhob) / (rho_matrix - rho_fluid), clamp to 0..1
    # TODO 4: return {"value": phi, "units": "fraction", "method": "density porosity", "inputs": {...}}
    raise ToolError("density_porosity is not implemented yet - finish the TODOs")


# ---- If you have more time, Stretch goal (Part C): add a `sonic_porosity` tool (Wyllie: (dt - 55.5) / (189 - 55.5)) below ----


if __name__ == "__main__":
    mcp.run(transport="stdio")
