import json

from mcp import Client

from sci_mcp.servers.geoscience_server import mcp as geo
from sci_mcp.servers.materials_server import mcp as mat
from sci_mcp.servers.porosity_server import mcp as por


async def test_geo_primitives():
    async with Client(geo) as c:  # in-process transport (SDK v2)
        assert {t.name for t in (await c.list_tools()).tools} == {"gardner_density", "acoustic_impedance", "reflection_coefficient", "two_way_time"}
        r = await c.call_tool("two_way_time", {"depth_m": 1500, "vp_m_s": 3000})
        assert json.loads(r.content[0].text)["value"] == 1000.0
        doc = await c.read_resource("geo://rock-properties/salt")
        assert "4400" in doc.contents[0].text
        assert [p.name for p in (await c.list_prompts()).prompts] == ["interpret_reflector"]


async def test_error_is_readable_by_model():
    async with Client(geo) as c:
        r = await c.call_tool("gardner_density", {"vp_m_s": 12})
        assert r.is_error and "1000-8000" in r.content[0].text


async def test_materials_and_porosity():
    async with Client(mat) as c:
        r = await c.call_tool("bragg_d_spacing", {"two_theta_deg": 38.47})
        assert abs(json.loads(r.content[0].text)["value"] - 2.338) < 0.002
    async with Client(por) as c:
        r = await c.call_tool("get_log_sample", {"depth_m": 2541})
        assert json.loads(r.content[0].text)["depth_m"] == 2540.0
        r = await c.call_tool("density_porosity", {"rhob": 2.35})
        assert abs(json.loads(r.content[0].text)["value"] - 0.181818) < 1e-4
        r = await c.call_tool("density_porosity", {"rhob": 235})
        assert r.is_error
