from .base import BaseLLMClient


class CloudLLMClient(BaseLLMClient):
    """Cloud LLM client placeholder (e.g. Gemini/Vertex AI)."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        # Placeholder for Milestone 1
        return f"[Cloud LLM {self.model_name}] Response to: {prompt}"
