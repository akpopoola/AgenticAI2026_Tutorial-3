"""Settings for any OpenAI-compatible endpoint, read from the environment / .env file."""
from __future__ import annotations

from dataclasses import dataclass

from dotenv import dotenv_values, find_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str

    @property
    def masked_key(self) -> str:
        k = self.api_key
        return "(not set)" if not k else (k[:3] + "..." + k[-4:] if len(k) > 10 else "***")


# Generic LLM_* names win; provider-specific names are accepted as fallbacks.
PROVIDERS = ("OPENAI", "ANTHROPIC", "OPENROUTER", "GROQ", "TOGETHER", "MISTRAL", "DEEPSEEK", "GEMINI", "XAI")


def _first(values: dict[str, str | None], names: list[str]) -> str:
    for n in names:
        v = values.get(n)
        if v:
            return v
    return ""


def load_settings() -> Settings:
    """Return exactly what the .env file defines; missing values are empty strings."""
    env = dotenv_values(find_dotenv(usecwd=True))
    return Settings(
        api_key=_first(env, ["LLM_API_KEY"] + [f"{p}_API_KEY" for p in PROVIDERS]),
        base_url=_first(env, ["LLM_BASE_URL"] + [f"{p}_BASE_URL" for p in PROVIDERS]),
        model=_first(env, ["LLM_MODEL", "MODEL"] + [f"{p}_MODEL" for p in PROVIDERS]).split(",")[0].strip(),
    )
