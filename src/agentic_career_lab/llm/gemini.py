import os

from google import genai

from .base import BaseLLMClient


class CloudLLM(BaseLLMClient):
    pass

class GeminiVertexClient(CloudLLM):
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        self.project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION")

        self.client = None
        if self.project and self.location:
            try:
                self.client = genai.Client(vertexai=True, project=self.project, location=self.location)
            except Exception:
                pass
        else:
            # Fallback to standard API key if provided
            if os.environ.get("GEMINI_API_KEY"):
                try:
                    self.client = genai.Client()
                except Exception:
                    pass

    def is_available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini client is not configured or available.")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}") from e

class FakeCloudLLM(CloudLLM):
    def __init__(self, is_online: bool = True):
        self.is_online = is_online

    def is_available(self) -> bool:
        return self.is_online

    def generate(self, prompt: str) -> str:
        if not self.is_online:
            raise RuntimeError("Fake Cloud LLM is offline")
        return '{"summary": "Fake learning plan", "target_role": "AI Engineer", "strengths": ["Python"], "priority_gaps": [], "learning_steps": [], "recommended_resources": []}'
