"""A thin wrapper around any OpenAI-compatible /chat/completions endpoint.

The `openai` package is used purely as an HTTP client: point `base_url` at any provider
that implements the same endpoint format and the rest of the tutorial code does not change.
"""
from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from sci_mcp.config import Settings, load_settings


class LLM:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        for field, var in (("base_url", "LLM_BASE_URL"), ("model", "LLM_MODEL")):
            if not getattr(self.settings, field):
                raise RuntimeError(f"{var} is not set in .env.")
        local = any(h in self.settings.base_url for h in ("localhost", "127.0.0.1", "0.0.0.0"))
        if not self.settings.api_key and not local:
            raise RuntimeError("LLM_API_KEY is not set. Copy .env.example to .env and add your token.")
        # Local servers (Ollama, vLLM) ignore the key but the client requires a non-empty one.
        self._client = AsyncOpenAI(api_key=self.settings.api_key or "not-needed", base_url=self.settings.base_url)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        *,
        parallel_tool_calls: bool | None = None,
        temperature: float | None = None,
    ):
        """One round trip. Returns the first choice's message object."""
        kwargs: dict[str, Any] = {"model": self.settings.model, "messages": messages}
        if temperature is not None:  # some models reject this parameter, so only send it when asked
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            if parallel_tool_calls is not None:  # not every compatible server accepts this field
                kwargs["parallel_tool_calls"] = parallel_tool_calls
        resp = await self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message
