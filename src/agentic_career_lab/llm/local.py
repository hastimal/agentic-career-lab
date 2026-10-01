from typing import Protocol

import httpx


class LocalLLM(Protocol):
    def is_available(self) -> bool: ...

    def generate(self, prompt: str) -> str: ...


class OllamaGemmaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "gemma4:12b"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def is_available(self) -> bool:
        try:
            # Check if ollama is reachable and model exists
            r = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if r.status_code != 200:
                return False
            data = r.json()
            models = [m.get("name") for m in data.get("models", [])]
            return self.model_name in models
        except Exception:
            return False

    def generate(self, prompt: str) -> str:
        try:
            r = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=30.0,
            )
            r.raise_for_status()
            return r.json().get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}") from e


class FakeGemmaClient:
    """Fake client for testing and deterministic UI behavior without Ollama installed."""

    def __init__(self, is_online: bool = True):
        self.is_online = is_online

    def is_available(self) -> bool:
        return self.is_online

    def generate(self, prompt: str) -> str:
        if not self.is_online:
            raise RuntimeError("Fake Ollama is offline")

        lower_prompt = prompt.lower()
        if "extract" in lower_prompt:
            # Fake extraction
            return '{"skills": ["Python", "SQL", "Docker", "REST APIs", "Google Cloud"], "experience": [{"title": "Student Developer", "company": "Example University Lab"}], "projects": [{"title": "Python REST API"}], "education": ["B.S. Computer Science, Expected 2027"], "technologies": ["Python", "SQL", "Docker", "Google Cloud", "REST APIs"]}'
        elif "suggest" in lower_prompt or "improve" in lower_prompt:
            # Fake suggestions
            return '{"suggestions": [{"original_text": "Built Python APIs for project.", "suggested_text": "Developed Python REST APIs supporting project workflows.", "evidence_used": ["Python", "REST APIs"]}]}'
        else:
            return "Fake response from Gemma 4."
