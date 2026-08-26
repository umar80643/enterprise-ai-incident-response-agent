from abc import ABC, abstractmethod

from app.core.config import get_settings


class ModelProvider(ABC):
    @abstractmethod
    async def structured(self, agent: str, prompt: str, schema): ...


class DeterministicProvider(ModelProvider):
    async def structured(self, agent, prompt, schema):
        raise RuntimeError(
            "Deterministic workflow agents implement typed local logic directly; no fake LLM response is generated."
        )


class UnavailableConfiguredProvider(ModelProvider):
    def __init__(self, name):
        self.name = name

    async def structured(self, agent, prompt, schema):
        raise RuntimeError(
            f"{self.name} provider adapter is configured but SDK/network invocation is not enabled in this offline demo build."
        )


def get_provider():
    s = get_settings()
    if s.llm_provider == "deterministic":
        return DeterministicProvider()
    supported = {
        "openai": s.openai_api_key,
        "anthropic": s.anthropic_api_key,
        "gemini": s.google_api_key,
        "ollama": s.ollama_base_url,
    }
    if s.llm_provider not in supported:
        raise RuntimeError(f"Unsupported LLM_PROVIDER={s.llm_provider}")
    if not supported[s.llm_provider]:
        raise RuntimeError(f"Missing credentials/config for {s.llm_provider}")
    return UnavailableConfiguredProvider(s.llm_provider)
