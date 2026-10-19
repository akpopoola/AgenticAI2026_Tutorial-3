"""A ~60-line tool-calling agent loop. This is the whole 'agent' - the rest is plumbing."""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any

from sci_mcp.client.llm import LLM
from sci_mcp.client.toolbox import Toolbox
# and do not use websearch, because it is not a scientific tool and we want to avoid hallucinations
#. Quote values with units and mention the method used.
# NEVER do the arithmetic yourself. 
SYSTEM = (
    "You are a careful scientific assistant. For any numerical result use the provided tools; "
    "never do the arithmetic yourself. Report values with units and mention the method used."
)


@dataclass
class ToolTrace:
    name: str
    arguments: dict[str, Any]
    output: str
    is_error: bool
    seconds: float


@dataclass
class AgentResult:
    answer: str
    turns: int
    trace: list[ToolTrace] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    seconds: float = 0.0


async def run_agent(
    llm: LLM,
    toolbox: Toolbox,
    prompt: str,
    *,
    system: str = SYSTEM,
    max_turns: int = 10,
    parallel: bool = True,
    verbose: bool = True,
) -> AgentResult:
    """Loop: ask model -> if it requested tools, run them (concurrently if `parallel`) -> feed results back."""
    t0 = time.perf_counter()
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    out = AgentResult(answer="", turns=0)

    async def execute(call) -> tuple[Any, ToolTrace]:
        start = time.perf_counter()
        try:
            args = json.loads(call.function.arguments or "{}")
            text, is_err = await toolbox.call(call.function.name, args)
        except Exception as exc:  # bad JSON, transport failure, ... -> let the model see and recover
            args, text, is_err = {}, f"Tool call failed: {exc}", True
        return call, ToolTrace(call.function.name, args, text, is_err, time.perf_counter() - start)

    for turn in range(1, max_turns + 1):
        out.turns = turn
        msg = await llm.chat(messages, toolbox.openai_tools, parallel_tool_calls=None if parallel else False)
        calls = msg.tool_calls or []
        messages.append(msg.model_dump(exclude_none=True) if hasattr(msg, "model_dump") else dict(msg))
        if not calls:
            out.answer = msg.content or ""
            break
        if verbose:
            print(f"[turn {turn}] model requested {len(calls)} tool call(s)")
        if parallel:
            done = await asyncio.gather(*(execute(c) for c in calls))
        else:
            done = [await execute(c) for c in calls]
        for call, trace in done:
            out.trace.append(trace)
            if verbose:
                flag = "ERROR " if trace.is_error else ""
                print(f"   -> {call.function.name}({json.dumps(trace.arguments)}) {flag}[{trace.seconds:.2f}s]")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": trace.output})
    else:
        out.answer = "(stopped: max_turns reached)"
    out.messages = messages
    out.seconds = time.perf_counter() - t0
    return out
