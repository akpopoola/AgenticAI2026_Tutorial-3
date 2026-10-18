"""End-to-end: agent loop + MCP over stdio + an OpenAI-compatible endpoint (scripted fake)."""
import subprocess
import sys
from pathlib import Path

import pytest

from fake_endpoint import make_server
from sci_mcp.client.agent import run_agent
from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox, stdio_module
from sci_mcp.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def llm_for(srv) -> LLM:
    return LLM(Settings(api_key="test-key", base_url=f"http://127.0.0.1:{srv.server_port}/v1", model="fake"))


async def test_parallel_tool_calls_run_concurrently():
    calls = [("materials__measure_sample", {"sample_id": f"A{i}", "delay_s": 1.0}) for i in range(4)]
    srv, seen = make_server(calls)
    async with Toolbox() as tb:
        await tb.connect("materials", stdio_module("sci_mcp.servers.materials_server"))
        par = await run_agent(llm_for(srv), tb, "measure", parallel=True, verbose=False)
        seq = await run_agent(llm_for(srv), tb, "measure", parallel=False, verbose=False)
    assert len(par.trace) == 4 and not any(t.is_error for t in par.trace)
    assert par.seconds < 2.5 < 3.5 < seq.seconds  # ~1s vs ~4s
    assert par.answer.startswith("RESULTS:") and par.turns == 2
    assert seen[0]["tools"][0]["function"]["name"].startswith("materials__")  # MCP schema reached the LLM
    srv.shutdown()


async def test_two_servers_and_tool_error_reaches_model():
    srv, seen = make_server([("geo__gardner_density", {"vp_m_s": 12}), ("materials__bragg_d_spacing", {"two_theta_deg": 38.47})])
    async with Toolbox() as tb:
        await tb.connect("geo", stdio_module("sci_mcp.servers.geoscience_server"))
        await tb.connect("materials", stdio_module("sci_mcp.servers.materials_server"))
        res = await run_agent(llm_for(srv), tb, "go", verbose=False)
    assert [t.is_error for t in res.trace] == [True, False]
    assert "1000-8000" in res.trace[0].output
    srv.shutdown()


def test_solution_passes_exercise_check():
    out = subprocess.run([sys.executable, str(ROOT / "exercises/ex1_check.py"), str(ROOT / "solutions/porosity_exercise_server.py")], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_skeleton_fails_exercise_check():
    out = subprocess.run([sys.executable, str(ROOT / "exercises/ex1_check.py")], capture_output=True, text=True)
    assert out.returncode != 0
