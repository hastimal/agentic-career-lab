import os

from .base import BaseLLMClient


class CloudLLM(BaseLLMClient):
    pass


class GeminiVertexClient(CloudLLM):
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")

    def is_available(self) -> bool:
        return True  # In a real implementation this would check API keys or Vertex auth

    def generate(self, prompt: str) -> str:
        return f"[GeminiVertexClient {self.model_name}] Response to: {prompt}"


class FakeCloudLLM(CloudLLM):
    def __init__(self, is_online: bool = True):
        self.is_online = is_online

    def is_available(self) -> bool:
        return self.is_online

    def generate(self, prompt: str) -> str:
        if not self.is_online:
            raise RuntimeError("Fake Cloud LLM is offline")
        return '{"summary": "Fake learning plan", "target_role": "AI Engineer", "strengths": ["Python"], "priority_gaps": [], "learning_steps": [], "recommended_resources": []}'
