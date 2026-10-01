# ruff: noqa: E402
import pytest

from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.agents.skill_builder.planner import (
    CloudPlanningLLM,
    DeterministicPlanningLLM,
)
from agentic_career_lab.models import Opportunity, ResumeAnalysis


class MockGenaiClient:
    def __init__(self, succeeds=True, valid_json=True, is_configured=True):
        self.succeeds = succeeds
        self.valid_json = valid_json
        self.is_configured = is_configured
        self.model_name = "gemini-1.5-pro" if is_configured else None

    def is_available(self):
        return self.is_configured

    def generate(self, prompt: str):
        if not self.succeeds:
            raise RuntimeError("API Error")
        if not self.valid_json:
            return "invalid json {"
        return '{"summary": "test", "learning_steps": []}'

def get_agent_with_mock_client(succeeds=True, valid_json=True, is_configured=True):
    client = MockGenaiClient(succeeds, valid_json, is_configured)
    llm = CloudPlanningLLM(client) if is_configured else DeterministicPlanningLLM()
    return SkillBuilderAgent(llm)

@pytest.fixture
def mock_opportunity():
    return Opportunity(
        opportunity_id="1", role="Role", company="Company", location="Location",
        source_url="http://example.com", description="", requirements=[], source="mock", is_demo=True
    )

@pytest.fixture
def mock_resume():
    return ResumeAnalysis(
        profile=None, requirement_matches=[], missing_evidence=[], suggestions=[], safety_summary=""
    )

def test_gemini_configured_succeeds(mock_opportunity, mock_resume):
    agent = get_agent_with_mock_client()
    agent.run(mock_opportunity, mock_resume)
    plan_event = next(e for e in agent.events if e["task_type"] == "learning_plan" or e["task_type"] == "TaskType.LEARNING_PLAN")
    assert plan_event["fallback_used"] is False
    assert "gemini_vertex" in plan_event["runtime"]

def test_gemini_configured_raises_error(mock_opportunity, mock_resume):
    agent = get_agent_with_mock_client(succeeds=False)
    agent.run(mock_opportunity, mock_resume)
    plan_event = next(e for e in agent.events if e["task_type"] == "learning_plan" or e["task_type"] == "TaskType.LEARNING_PLAN")
    assert plan_event["fallback_used"] is True
    assert plan_event["runtime"] == "Python fallback"

def test_gemini_response_invalid_json(mock_opportunity, mock_resume):
    agent = get_agent_with_mock_client(valid_json=False)
    agent.run(mock_opportunity, mock_resume)
    plan_event = next(e for e in agent.events if e["task_type"] == "learning_plan" or e["task_type"] == "TaskType.LEARNING_PLAN")
    assert plan_event["fallback_used"] is True
    assert plan_event["runtime"] == "Python fallback"

def test_gemini_not_configured(mock_opportunity, mock_resume):
    agent = get_agent_with_mock_client(is_configured=False)
    agent.run(mock_opportunity, mock_resume)
