# Section 7 - Porosity tool exercise (~12 minutes)

You will give an LLM a *validated* porosity calculator through MCP, then break it on purpose.

Files: `exercises/porosity_exercise_server.py` (edit this), `exercises/ex1_check.py`, `exercises/ex1_run_agent.py`.
Data: `data/well_log_sample.csv` (depth, RHOB, DT, NPHI, RT).

## Part A - Implement the tool (5 min, no API key needed)

Open `porosity_exercise_server.py` and finish `density_porosity` (TODO 1-4):

1. Write a docstring a *model* can act on: formula, units, return shape.
2. Reject bad input with `ToolError("...")` (rhob outside 1.0-3.2 g/cm3; rho_matrix <= rho_fluid).
3. Compute `phi = (rho_matrix - rhob) / (rho_matrix - rho_fluid)` and clamp to 0<`phi`<1.
4. Return value + units + method + inputs (provenance, like the other servers).

Check yourself: `uv run exercises\ex1_check.py` - every line should say PASS.

## Part B - Let the agent use it (4 min)

`uv run exercises/ex1_run_agent.py`

Look at the three questions:
* Q1 needs two tools in sequence (`get_log_sample` then `density_porosity`).
* Q2 asks for two independent samples - do you see two tool calls in one `[turn]`?
* Q3 has a unit mistake (RHOB = 235). Does the model retry after the ToolError, or answer anyway?
  Delete your range check, re-run Q3, and compare. Which version would you trust in a paper?

## If you have time, Part C - Stretch / debrief (3 min)

* Add a `sonic_porosity` tool (Wyllie: `(dt - 55.5) / (189 - 55.5)`) and ask the agent to compare density and
  sonic porosity at 2540 m. Which parts of the reply came from tools, and which from the model?
* Change the tool description only (not the code) and watch the model's behaviour change.
* Reference solution: `solutions/porosity_exercise_server.py` (`uv run exercises/ex1_run_agent.py --solution`).

## Discussion prompts
1. Where in your own research is there a function an LLM should *call* rather than *imitate*?
2. What is the cost of a wrong-but-plausible number in that workflow?
3. Which inputs need validation so the failure is loud and readable?
