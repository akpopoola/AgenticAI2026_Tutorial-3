# AgenticAI2026_Tutorial-3: Model Context Protocol for scientific agents

Code for Tutorial 3 of the [Fall School on Agentic AI in Science 2026](https://ai-for-science.org/).

**MCP for Science tutorial** why scientific agents need tools and how the
**Model Context Protocol (MCP)** gives language-model applications access to validated scientific capabilities.
Examples come from materials science (XRD) and geoscience (rock physics, petrophysics).

* MCP Python SDK **v2** (`mcp>=2,<3`): `MCPServer`, `Client`, `ToolError`
* Any **OpenAI-compatible** endpoint with a token (API key) - OpenAI, Anthropic, Azure/OpenRouter/Groq, or a local vLLM/Ollama/LiteLLM (for your confidential data)
* Project managed with **uv**; no agent framework (this is worth exploring further)

## Pre-work (10 minutes, do this before the session)

1. Install uv - <https://docs.astral.sh/uv/getting-started/installation/>
   * macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. From this folder: `uv sync` (creates `.venv`, installs Python 3.12+ and all dependencies)
3. Activate the virtual environment `.venv\Scripts\activate`
4. Configure your endpoint: copy `.env.example` to `.env` and set
   `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` (must support tool/function calling-suggestion in the tutorial slide). Examples are provided, keep only one block and delete the other two in your new `.env` file
5. Verify: `uv run sci-check` - every line should say `[ ok ]`
6. Optional: `uv run pytest` runs the offline test-suite (no key needed)

**IDE:** Although you may use your editor of choice. I recommend VS Code

**Never commit** `.env`; it is git-ignored (to secure your API key).

## End of pre-work setup 

## High level agenda (~60 mins)

| # | Section | ~Min | Run |
|---|---------|------|-----|
| 1 | Why tool calling for scientific agents | 6 | `uv run demos/d01_why_tools.py` |
| 2 | How models request tools | 4 | `uv run demos/d02_raw_tool_call.py` |
| 3 | MCP capabilities and architecture | 5 | `uv run demos/d03_inspect_server.py` |
| 4 | Build and use a scientific MCP server | 9 | read `src/sci_mcp/servers/geoscience_server.py`, `uv run demos/d04_agent_geo.py` |
| 5 | Materials science and geoscience examples | 7 | `uv run demos/d05_materials_and_geo.py` |
| 6 | Simultaneous multiple tool calls | 5 | `uv run demos/d06_parallel_calls.py` |
| 7 | Porosity tool exercise and debrief | 12 | `exercises/EXERCISES.md` |
| 8 | Questions and research transfer | 4 | - |

## Layout

```
src/sci_mcp/
  physics/        pure, unit-tested functions (porosity, materials, geo) - no MCP, no LLM
  servers/        geoscience_server.py, materials_server.py, porosity_server.py  (MCPServer)
  client/         llm.py (OpenAI-compatible), toolbox.py (MCP <-> tool schemas), agent.py (the agent loop)
  check_setup.py  `uv run sci-check` to verify setup is good and you're ready to go
demos/            d01 ... d06, one per tutorial demo section
exercises/        porosity_exercise_server.py (TODOs), ex1_check.py, ex1_run_agent.py, EXERCISES.md
solutions/        porosity_exercise_server.py (reference, use it after you've tried your implementation) 
tests/            physics, servers, and an end-to-end agent test against a scripted fake endpoint
data/             well_log_sample.csv
```

Run a server on its own (stdio): `uv run sci-geo-server`, `uv run sci-materials-server`, `uv run sci-porosity-server`.
These can be registered in any MCP host (e.g. Claude Desktop, Claude Code, IDEs) with command `uv` and args
`["--directory", "<this folder>", "run", "sci-geo-server"]`.

## MCP SDK v2 cheat-sheet (what changed from v1)

| Task | v2 |
|------|----|
| Server class | `from mcp.server.mcpserver import MCPServer` (was `FastMCP` in `mcp.server.fastmcp`) |
| Declare tool / resource / prompt | `@mcp.tool()`, `@mcp.resource("uri://{x}")`, `@mcp.prompt()` |
| Run | `mcp.run(transport="stdio")` (also `"streamable-http"`) |
| Client | `from mcp import Client`; `async with Client(target) as c:` - target is stdio params, a URL, or an in-process `MCPServer` |
| Expected tool failure | `raise ToolError("message")` - the model sees the message; other exceptions show only `Error executing tool <name>` |
| Result | `CallToolResult`: `.content`, `.is_error`, `.structured_content` |

## Troubleshooting

* **`sci-check` says the endpoint did not request a tool** - pick a model with function/tool calling; some local models need a tool-capable chat template.
* **HTTP 400 mentioning `parallel_tool_calls`** - the loop only sends that field with `parallel=False` (demo d06); remove it in `client/llm.py` for strict servers.
* **Windows** - use PowerShell; commands are identical. Servers are launched with the same Python interpreter (`sys.executable`), so no PATH tweaks are required.

* **Important to Note:** Model answers differ run-to-run; the *tool outputs* do not. That is the point of the tutorial.

## **License**

This project is licensed under the [MIT License](LICENSE).
