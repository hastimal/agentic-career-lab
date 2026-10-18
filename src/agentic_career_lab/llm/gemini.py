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
        if self.project and self.location and self.project != "your-gcp-project-id":
            try:
                self.client = genai.Client(
                    vertexai=True, project=self.project, location=self.location
                )
            except Exception:
                pass

        # Fallback to standard API key if Vertex is not configured or failed
        if self.client is None and os.environ.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client()
            except Exception:
                pass

    def is_available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini client is not configured or available.")

        from agentic_career_lab.observability import trace_span

        with trace_span(
            "llm.gemini.generate",
            agent_name="Skill Builder",
            model_name=self.model_name,
            runtime="Gemini / Vertex AI",
            attributes={"prompt_length": len(prompt)},
        ) as span:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    span.set_attribute(
                        "llm.prompt_token_count",
                        getattr(response.usage_metadata, "prompt_token_count", 0),
                    )
                    span.set_attribute(
                        "llm.candidates_token_count",
                        getattr(response.usage_metadata, "candidates_token_count", 0),
                    )
                return response.text
            except Exception as e:
                span.set_attribute("error.message", str(e)[:200])
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
