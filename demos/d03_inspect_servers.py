"""Section 3 - MCP capabilities and architecture. Talk to an MCP server with NO LLM involved.

The host launches the server as a subprocess (stdio transport) and speaks JSON-RPC to it.

    uv run demos/d03_inspect_server.py
"""
import asyncio
import json

from mcp import Client

from sci_mcp.client.toolbox import stdio_module


async def main() -> None:
    print("\nInspecting the geoscience server ...\n")
    async with Client(stdio_module("sci_mcp.servers.geoscience_server")) as client:
        print("TOOLS (model-controlled)")
        for t in (await client.list_tools()).tools:
            print(f"  - {t.name}: {t.description}")
            print(f"      input schema: {json.dumps(t.input_schema['properties'])}")

        print("\nRESOURCES (application-controlled)")
        for r in (await client.list_resources()).resources:
            print(f"  - {r.uri}  {r.description or ''}")
        for rt in (await client.list_resource_templates()).resource_templates:
            print(f"  - {rt.uri_template}  (template)")

        print("\nPROMPTS (user-controlled)")
        for p in (await client.list_prompts()).prompts:
            print(f"  - {p.name}: {p.description}")

        print("\nDirect call, no LLM: reflection_coefficient(z_upper=6.0e6, z_lower=8.5e6)")
        res = await client.call_tool("reflection_coefficient", {"z_upper": 6.0e6, "z_lower": 8.5e6})
        print("  ", res.content[0].text.replace("\n", " "))

        print("\nRead resource geo://rock-properties/salt")
        doc = await client.read_resource("geo://rock-properties/salt")
        print("  ", doc.contents[0].text.replace("\n", " "))

        print("\nA bad call is reported as data, not a crash:")
        bad = await client.call_tool("gardner_density", {"vp_m_s": 120})
        print(f"   is_error={bad.is_error}: {bad.content[0].text[:110]}")
    #
    print("\nInspecting the material server ...\n")
    async with Client(stdio_module("sci_mcp.servers.materials_server")) as client2:
            print("TOOLS (model-controlled)")
            for t in (await client2.list_tools()).tools:
                print(f"  - {t.name}: {t.description}")
                print(f"      input schema: {json.dumps(t.input_schema['properties'])}")
    
            print("\nRESOURCES (application-controlled)")
            for r in (await client2.list_resources()).resources:
                print(f"  - {r.uri}  {r.description or ''}")
            for rt in (await client2.list_resource_templates()).resource_templates:
                print(f"  - {rt.uri_template}  (template)")
    
            print("\nPROMPTS (user-controlled)")
            for p in (await client2.list_prompts()).prompts:
                print(f"  - {p.name}: {p.description}")

            print("\nDirect call, no LLM: scherrer_crystallite_size(fwhm_deg=0.35, two_theta_deg=38.2)")
            res = await client2.call_tool("scherrer_crystallite_size", {"fwhm_deg": 0.35, "two_theta_deg": 38.2})
            print("  ", res.content[0].text.replace("\n", " "))

if __name__ == "__main__":
    asyncio.run(main())
