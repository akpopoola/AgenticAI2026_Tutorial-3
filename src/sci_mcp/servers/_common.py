"""Helpers shared by the tutorial servers."""
from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def result(value: float, units: str, method: str, **inputs) -> dict:
    """Uniform, self-describing tool result: value + units + method + the inputs used.

    Returning provenance (not just a number) lets the model quote units correctly and lets
    a human audit the call later. This is the 'validated capability' idea.
    """
    return {"value": round(value, 6), "units": units, "method": method, "inputs": inputs}


def compute(fn, *args, **kwargs):
    """Run a physics function; turn input-validation failures into a ToolError.

    MCP SDK v2: a ToolError becomes an `is_error=True` result whose message the MODEL can read and use to
    retry with corrected inputs. Any other exception is treated as a crash and the model only sees
    'Error executing tool <name>' (the traceback stays on the server).
    """
    try:
        return fn(*args, **kwargs)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
