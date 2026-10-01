# ruff: noqa: E402
import pytest

from agentic_career_lab.routing import (
    CloudPlanningContext,
    HybridRouter,
    PrivacyGuardError,
    RuntimeType,
    TaskType,
    assert_cloud_safe,
)


def test_routing_decisions():
    # 1. opportunity_search routes to Python/provider
    d = HybridRouter.route(TaskType.OPPORTUNITY_SEARCH)
    assert d.runtime == RuntimeType.PYTHON
    assert d.cloud_allowed is True

    # 2. resume_analysis routes to Gemma/Ollama
    d = HybridRouter.route(TaskType.RESUME_ANALYSIS)
    assert d.runtime == RuntimeType.GEMMA_OLLAMA
    assert d.cloud_allowed is False
    assert d.fallback_allowed is False

    # 3. resume_rewrite routes to Gemma/Ollama
    d = HybridRouter.route(TaskType.RESUME_REWRITE)
    assert d.runtime == RuntimeType.GEMMA_OLLAMA

    # 4. skill_matching routes to Python
    d = HybridRouter.route(TaskType.SKILL_MATCHING)
    assert d.runtime == RuntimeType.PYTHON

    # 5. gap_analysis routes to Python
    d = HybridRouter.route(TaskType.GAP_ANALYSIS)
    assert d.runtime == RuntimeType.PYTHON

    # 6. learning_plan routes to Gemini/Vertex
    d = HybridRouter.route(TaskType.LEARNING_PLAN)
    assert d.runtime == RuntimeType.GEMINI_VERTEX
    assert d.cloud_allowed is True
    assert d.fallback_allowed is True

    # 7. resource_lookup routes to Python
    d = HybridRouter.route(TaskType.RESOURCE_LOOKUP)
    assert d.runtime == RuntimeType.PYTHON

    # 8. portfolio_project routes to Gemini/Vertex
    d = HybridRouter.route(TaskType.PORTFOLIO_PROJECT)
    assert d.runtime == RuntimeType.GEMINI_VERTEX

    # 9. claim_validation routes to Python
    d = HybridRouter.route(TaskType.CLAIM_VALIDATION)
    assert d.runtime == RuntimeType.PYTHON


def test_privacy_guard_safe():
    ctx = CloudPlanningContext(
        target_role="AI Engineer",
        required_skills=["Python"],
        demonstrated_skills=["Python"],
        partial_skills=[],
        missing_skills=[],
        plan_duration_weeks=4,
    )
    assert_cloud_safe(ctx)


def test_privacy_guard_forbidden_keys():
    bad_payload = {"raw_resume_text": "secret resume data"}
    with pytest.raises(PrivacyGuardError, match="Forbidden key 'raw_resume_text'"):
        assert_cloud_safe(bad_payload)


def test_privacy_guard_secret():
    bad_payload = {"some_field": "PRIVATE_RESUME_SECRET_12345"}
    with pytest.raises(PrivacyGuardError, match="Private resume secret"):
        assert_cloud_safe(bad_payload)


from agentic_career_lab.agents.skill_builder.planner import (
    DeterministicPlanningLLM,
)
from agentic_career_lab.llm.local import OllamaGemmaClient
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.runtime.factory import (
    create_job_provider,
    create_resume_llm,
    create_skill_planner,
)


def test_resume_factory_returns_ollama():
    llm = create_resume_llm()
    assert isinstance(llm, OllamaGemmaClient)
    assert not isinstance(llm, type(None))

def test_job_provider_factory_returns_mock():
    provider = create_job_provider()
    assert isinstance(provider, MockOpportunityProvider)

def test_skill_planner_factory(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    planner = create_skill_planner()
    # It should fallback deterministically if no api key
    assert isinstance(planner, DeterministicPlanningLLM)

