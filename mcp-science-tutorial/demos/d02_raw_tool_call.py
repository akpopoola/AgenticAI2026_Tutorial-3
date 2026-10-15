"""Section 2 - How models request tools. No MCP yet: just the raw tool-calling protocol.

Watch the three message types: assistant(tool_calls) -> tool(result) -> assistant(final text).

    uv run demos/d02_raw_tool_call.py
"""
import asyncio
import json

from sci_mcp.client.llm import LLM
from sci_mcp.physics.geo import gardner_density

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "gardner_density",
            "description": "Estimate bulk density (g/cm3) from P-wave velocity (m/s) with Gardner's relation.",
            "parameters": {
                "type": "object",
                "properties": {"vp_m_s": {"type": "number", "description": "P-wave velocity in m/s"}},
                "required": ["vp_m_s"],
            },
        },
    }
]


async def main() -> None:
    llm = LLM()
    messages = [{"role": "user", "content": "A sandstone has Vp = 3200 m/s. What density does Gardner's relation give?"}]

    msg = await llm.chat(messages, TOOLS)
    print("1) MODEL REPLY (note: content is empty, the model asks US to run code):")
    print(json.dumps(msg.model_dump(exclude_none=True), indent=2))

    messages.append(msg.model_dump(exclude_none=True))
    for call in msg.tool_calls or []:
        args = json.loads(call.function.arguments)  # arguments arrive as a JSON *string*
        value = gardner_density(**args)  # <- the host application executes the function
        print(f"\n2) WE EXECUTE {call.function.name}({args}) = {value:.4f}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps({"value": value, "units": "g/cm3"})})

    final = await llm.chat(messages, TOOLS)
    print("\n3) FINAL ANSWER:", final.content)


if __name__ == "__main__":
    asyncio.run(main())
