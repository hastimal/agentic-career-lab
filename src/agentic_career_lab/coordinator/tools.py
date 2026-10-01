from typing import Any

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.coordinator.state import LocalResumeContext
from agentic_career_lab.models import OpportunitySearchQuery, StudentProfile


def search_opportunities_tool(
    job_scout: JobScoutAgent,
    profile: StudentProfile,
    query: OpportunitySearchQuery,
) -> tuple[list[Any], list[Any]]:
    """Returns matches, events."""
    matches = job_scout.run(profile, query)
    return matches, job_scout.events


def analyze_resume_locally_tool(
    resume_agent: PrivateResumeAgent, selected_opportunity: Any, resume_context: LocalResumeContext
) -> tuple[Any | None, list[Any], str | None]:
    """Returns analysis, events, error_string."""
    try:
        # Pass the raw text locally ONLY here
        analysis = resume_agent.run(
            resume_text=resume_context.raw_resume_text, opportunity=selected_opportunity
        )
        return analysis, resume_agent.events, None
    except Exception as e:
        return None, resume_agent.events, str(e)


def build_skill_plan_tool(
    skill_builder: SkillBuilderAgent,
    selected_opportunity: Any,
    resume_analysis: Any,
    duration_weeks: int = 4,
) -> tuple[Any | None, list[Any], str | None]:
    """Returns plan, events, error_string."""
    try:
        plan = skill_builder.run(
            opportunity=selected_opportunity,
            resume_analysis=resume_analysis,
            duration_weeks=duration_weeks,
        )
        return plan, skill_builder.events, None
    except Exception as e:
        return None, skill_builder.events, str(e)
