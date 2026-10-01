from agentic_career_lab.ui_helpers import (
    ACTIVITY,
    HOME,
    OPPORTUNITIES,
    RESUME,
    SKILLS,
    get_workflow_progress,
    normalize_navigation,
)


def test_canonical_navigation():
    assert HOME == "Home"
    assert OPPORTUNITIES == "Find Opportunities"
    assert RESUME == "Prepare Resume"
    assert SKILLS == "Build Skills"
    assert ACTIVITY == "Agent Activity"


def test_normalize_navigation():
    assert normalize_navigation("Home") == "Home"
    assert normalize_navigation("Find Opportunities") == "Find Opportunities"
    assert normalize_navigation("Prepare Resume") == "Prepare Resume"
    assert normalize_navigation("Build Skills") == "Build Skills"
    assert normalize_navigation("Agent Activity") == "Agent Activity"
    assert normalize_navigation("Overview") == "Home"
    assert normalize_navigation("Invalid Page") == "Home"
    assert normalize_navigation(None) == "Home"


def test_workflow_progress_fresh():
    progress = get_workflow_progress(None, None, None)
    assert progress["opportunity_selected"] is False
    assert progress["resume_analyzed"] is False
    assert progress["skill_plan_built"] is False
    assert progress["next_step"] == OPPORTUNITIES


def test_workflow_progress_opportunity_selected():
    progress = get_workflow_progress("some_opp", None, None)
    assert progress["opportunity_selected"] is True
    assert progress["resume_analyzed"] is False
    assert progress["skill_plan_built"] is False
    assert progress["next_step"] == RESUME


def test_workflow_progress_resume_analyzed():
    progress = get_workflow_progress("some_opp", "some_analysis", None)
    assert progress["opportunity_selected"] is True
    assert progress["resume_analyzed"] is True
    assert progress["skill_plan_built"] is False
    assert progress["next_step"] == SKILLS


def test_workflow_progress_complete():
    progress = get_workflow_progress("some_opp", "some_analysis", "some_plan")
    assert progress["opportunity_selected"] is True
    assert progress["resume_analyzed"] is True
    assert progress["skill_plan_built"] is True
    assert progress["next_step"] is None
