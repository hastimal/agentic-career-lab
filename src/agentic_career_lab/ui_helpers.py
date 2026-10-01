from typing import Any

HOME = "Home"
OPPORTUNITIES = "Find Opportunities"
RESUME = "Prepare Resume"
SKILLS = "Build Skills"
ACTIVITY = "Agent Activity"

VALID_PAGES = {
    HOME,
    OPPORTUNITIES,
    RESUME,
    SKILLS,
    ACTIVITY,
}


def normalize_navigation(page: str | None) -> str:
    if page in VALID_PAGES:
        return page
    return HOME


def get_workflow_progress(
    selected_opportunity: Any | None,
    resume_analysis: Any | None,
    skill_builder_plan: Any | None,
) -> dict[str, Any]:
    opportunity_selected = selected_opportunity is not None
    resume_analyzed = resume_analysis is not None
    skill_plan_built = skill_builder_plan is not None

    if not opportunity_selected:
        next_step = OPPORTUNITIES
    elif not resume_analyzed:
        next_step = RESUME
    elif not skill_plan_built:
        next_step = SKILLS
    else:
        next_step = None

    return {
        "opportunity_selected": opportunity_selected,
        "resume_analyzed": resume_analyzed,
        "skill_plan_built": skill_plan_built,
        "next_step": next_step,
    }
