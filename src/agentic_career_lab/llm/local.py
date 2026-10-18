import json
import os
import time
from collections.abc import Generator
from typing import Protocol

import httpx


class LocalLLM(Protocol):
    def is_available(self) -> bool: ...

    def generate(self, prompt: str) -> str: ...

    def generate_stream(self, prompt: str) -> Generator[str, None, None]: ...


class OllamaGemmaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "gemma4:12b"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def is_available(self) -> bool:
        try:
            # Check if ollama is reachable and model exists
            r = httpx.get(f"{self.base_url}/api/tags", timeout=3.0)
            if r.status_code != 200:
                return False
            data = r.json()
            models = [m.get("name") for m in data.get("models", [])]
            return self.model_name in models
        except Exception:
            return False

    def _get_timeout_config(self) -> httpx.Timeout:
        """Configurable timeout parameters with sensible cold-start and read bounds."""
        connect_timeout = float(os.environ.get("OLLAMA_CONNECT_TIMEOUT", "10.0"))
        read_timeout = float(os.environ.get("OLLAMA_TIMEOUT", "180.0"))
        write_timeout = float(os.environ.get("OLLAMA_WRITE_TIMEOUT", "30.0"))
        pool_timeout = float(os.environ.get("OLLAMA_POOL_TIMEOUT", "10.0"))
        return httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout,
        )

    def generate(self, prompt: str) -> str:
        from agentic_career_lab.observability import trace_span

        with trace_span(
            "llm.ollama.generate",
            agent_name="Private Resume Agent",
            model_name=self.model_name,
            runtime="Gemma 4 / Ollama",
            attributes={"prompt_length": len(prompt)},
        ) as span:
            try:
                timeouts = self._get_timeout_config()
                r = httpx.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model_name, "prompt": prompt, "stream": False},
                    timeout=timeouts,
                )
                r.raise_for_status()
                resp = r.json()
                eval_count = resp.get("eval_count")
                if eval_count:
                    span.set_attribute("llm.eval_tokens", eval_count)
                prompt_eval_count = resp.get("prompt_eval_count")
                if prompt_eval_count:
                    span.set_attribute("llm.prompt_eval_tokens", prompt_eval_count)
                return resp.get("response", "")
            except httpx.TimeoutException as te:
                span.set_attribute("error.message", f"Timeout ({te})")
                raise RuntimeError(
                    f"Ollama generation timed out while generating with {self.model_name}. "
                    "The local model may still be loading or system is under high memory pressure."
                ) from te
            except Exception as e:
                span.set_attribute("error.message", str(e)[:200])
                raise RuntimeError(f"Ollama generation failed: {e}") from e

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """True progressive token streaming yielding actual generated text chunks."""
        from agentic_career_lab.observability import trace_span

        start_time = time.time()
        first_token_received = False

        with trace_span(
            "llm.ollama.generate_stream",
            agent_name="CareerChatOrchestrator",
            model_name=self.model_name,
            runtime="Gemma 4 / Ollama (Streaming)",
            attributes={"prompt_length": len(prompt)},
        ) as span:
            try:
                timeouts = self._get_timeout_config()
                with httpx.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={"model": self.model_name, "prompt": prompt, "stream": True},
                    timeout=timeouts,
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                if not first_token_received:
                                    first_token_duration_ms = (time.time() - start_time) * 1000
                                    span.set_attribute(
                                        "llm.first_token_ms", first_token_duration_ms
                                    )
                                    first_token_received = True
                                yield chunk
                            if data.get("done"):
                                eval_count = data.get("eval_count")
                                if eval_count:
                                    span.set_attribute("llm.eval_tokens", eval_count)
                                break
            except httpx.TimeoutException as te:
                span.set_attribute("error.message", f"Stream timeout ({te})")
                raise RuntimeError(
                    f"Ollama token stream timed out: {te}. Please ensure Ollama is running and has sufficient RAM/VRAM."
                ) from te
            except Exception as e:
                span.set_attribute("error.message", str(e)[:200])
                raise RuntimeError(f"Ollama streaming failed: {e}") from e


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
            return '{"skills": ["Python", "SQL", "Docker", "REST APIs", "Google Cloud"], "experience": [{"title": "Student Developer", "company": "Example University Lab"}], "projects": [{"title": "Python REST API"}], "education": ["B.S. Computer Science, Expected 2027"], "technologies": ["Python", "SQL", "Docker", "Google Cloud", "REST APIs"]}'
        elif "suggest" in lower_prompt or "improve" in lower_prompt:
            return '{"suggestions": [{"original_text": "Built Python APIs for project.", "suggested_text": "Developed Python REST APIs supporting project workflows.", "evidence_used": ["Python", "REST APIs"]}]}'
        else:
            return "Fake response from Gemma 4."

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        if not self.is_online:
            raise RuntimeError("Fake Ollama is offline")
        full_text = self.generate(prompt)
        # Yield words to simulate streaming chunks deterministically in tests
        words = full_text.split(" ")
        for i, w in enumerate(words):
            yield w + (" " if i < len(words) - 1 else "")
