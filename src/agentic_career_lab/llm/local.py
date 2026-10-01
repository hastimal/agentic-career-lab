from .base import BaseLLMClient


class LocalLLMClient(BaseLLMClient):
    """Local LLM client placeholder (e.g. Gemma/Ollama)."""

    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        # Placeholder for Milestone 1
        return f"[Local LLM {self.model_name} at {self.base_url}] Response to: {prompt}"
