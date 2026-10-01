import os

from agentic_career_lab.agents.skill_builder.planner import (
    CloudPlanningLLM,
    DeterministicPlanningLLM,
    PlanningLLM,
)
from agentic_career_lab.llm.gemini import GeminiVertexClient
from agentic_career_lab.llm.local import OllamaGemmaClient
from agentic_career_lab.providers.base import OpportunityProvider
from agentic_career_lab.providers.mock import MockOpportunityProvider


def create_resume_llm():
    """Create local LLM for private resume parsing."""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.environ.get("GEMMA_MODEL", "gemma4:12b")
    return OllamaGemmaClient(base_url=base_url, model_name=model_name)

def create_skill_planner() -> PlanningLLM:
    """Create a real Gemini planner if available, else fallback."""
    gemini_client = GeminiVertexClient()
    if gemini_client.is_available():
        return CloudPlanningLLM(gemini_client)
    return DeterministicPlanningLLM()

def create_job_provider() -> OpportunityProvider:
    """Create the initial opportunity provider."""
    return MockOpportunityProvider()
