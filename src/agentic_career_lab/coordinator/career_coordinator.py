import time
from typing import Any

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.agents.resume_agent.agent import PrivateResumeAgent
from agentic_career_lab.agents.skill_builder.agent import SkillBuilderAgent
from agentic_career_lab.coordinator.events import AgentExecutionEvent
from agentic_career_lab.coordinator.state import (
    CareerAction,
    CareerActionPlan,
    CareerWorkflowState,
    LocalResumeContext,
)
from agentic_career_lab.coordinator.tools import (
    analyze_resume_locally_tool,
    build_skill_plan_tool,
    search_opportunities_tool,
)


class CareerCoordinator:
    """Orchestrates Job Scout, Private Resume Agent, and Skill Builder."""

    def __init__(
        self,
        job_scout: JobScoutAgent,
        resume_agent: PrivateResumeAgent,
        skill_builder: SkillBuilderAgent,
    ):
        self.job_scout = job_scout
        self.resume_agent = resume_agent
        self.skill_builder = skill_builder

    def execute_action(
        self,
        action: CareerAction,
        state: CareerWorkflowState,
        local_resume: LocalResumeContext | None = None,
    ) -> CareerWorkflowState:
        """Executes a specific workflow step and returns the updated state."""
        start_time = time.time()

        try:
            if action == CareerAction.FIND_OPPORTUNITIES:
                self._run_job_scout(state)

            elif action == CareerAction.PREPARE_RESUME:
                self._run_resume_agent(state, local_resume)

            elif action == CareerAction.BUILD_SKILLS:
                self._run_skill_builder(state)

            elif action == CareerAction.FULL_WORKFLOW:
                self._run_job_scout(state)
                # Need to select the first opportunity deterministically for full flow demo
                if state.opportunities:
                    state.selected_opportunity = state.opportunities[0].opportunity
                self._run_resume_agent(state, local_resume)
                self._run_skill_builder(state)

            duration = (time.time() - start_time) * 1000
            self._log_event(
                state,
                agent="Career Coordinator",
                step=f"route_{action.value}",
                status="Success",
                runtime="Google ADK Orchestration",
                duration=duration,
                summary=f"Successfully orchestrated {action.value}",
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self._log_event(
                state,
                agent="Career Coordinator",
                step=f"route_{action.value}",
                status="Failed",
                runtime="Google ADK Orchestration",
                duration=duration,
                summary=f"Orchestration failed: {str(e)}",
                error_code="COORDINATOR_ERROR",
            )
            state.errors.append(str(e))

        return state

    def _run_job_scout(self, state: CareerWorkflowState):
        if not state.student_profile or not state.search_query:
            raise ValueError("StudentProfile and OpportunitySearchQuery required for Job Scout.")

        matches, events = search_opportunities_tool(
            self.job_scout, state.student_profile, state.search_query
        )
        state.opportunities = matches
        self._map_events(state, events, "Job Scout", "Python / Provider")
        state.completed_steps.append("job_scout")

    def _run_resume_agent(
        self, state: CareerWorkflowState, local_resume: LocalResumeContext | None
    ):
        if not state.selected_opportunity:
            raise ValueError("selected_opportunity required for Resume Agent.")
        if not local_resume:
            raise ValueError("LocalResumeContext required for Resume Agent.")

        analysis, events, err = analyze_resume_locally_tool(
            self.resume_agent, state.selected_opportunity, local_resume
        )
        self._map_events(state, events, "Private Resume Agent", "Gemma 4 / Ollama")

        if err:
            state.errors.append(f"Private Resume Agent failed: {err}")
            self._log_event(
                state,
                agent="Private Resume Agent",
                step="extract_resume_evidence",
                status="Failed",
                runtime="Gemma 4 / Ollama",
                duration=0,
                summary=f"Failed: {err}",
                error_code="LOCAL_OLLAMA_ERROR",
            )
        else:
            state.resume_analysis = analysis
            state.completed_steps.append("private_resume")

    def _run_skill_builder(self, state: CareerWorkflowState):
        if not state.selected_opportunity or not state.resume_analysis:
            raise ValueError("selected_opportunity and resume_analysis required for Skill Builder.")

        plan, events, err = build_skill_plan_tool(
            self.skill_builder, state.selected_opportunity, state.resume_analysis, duration_weeks=4
        )
        self._map_events(state, events, "Skill Builder", "Python / Gemini")

        if err:
            state.errors.append(f"Skill Builder failed: {err}")
            self._log_event(
                state,
                agent="Skill Builder",
                step="build_plan",
                status="Failed",
                runtime="Python / Gemini",
                duration=0,
                summary=f"Failed: {err}",
                error_code="SKILL_BUILDER_ERROR",
            )
        else:
            state.skill_builder_plan = plan
            state.completed_steps.append("skill_builder")

    def _map_events(
        self,
        state: CareerWorkflowState,
        agent_events: list[Any],
        agent_name: str,
        default_runtime: str,
    ):
        for e in agent_events:
            # Check if it's a new RoutingEvent dict
            if "task_type" in e:
                step = e.get("task_type", "unknown_task")
                runtime = e.get("runtime", default_runtime)
                if e.get("fallback_used"):
                    runtime += " fallback"
                summary = e.get("reason", "")
                privacy = e.get("privacy_level", "")
                if privacy:
                    summary += f" | Privacy: {privacy}"
                self._log_event(
                    state,
                    agent=agent_name,
                    step=step,
                    status=e.get("status", "Success"),
                    runtime=runtime,
                    duration=e.get("duration_ms", 0.0),
                    summary=summary,
                )
            else:
                self._log_event(
                    state,
                    agent=agent_name,
                    step=e.get("step", "unknown_step"),
                    status=e.get("status", "Success"),
                    runtime=default_runtime,
                    duration=e.get("duration", 0.0) * 1000,
                    summary=e.get("summary", ""),
                )

    def _log_event(
        self,
        state: CareerWorkflowState,
        agent: str,
        step: str,
        status: str,
        runtime: str,
        duration: float,
        summary: str,
        error_code: str | None = None,
    ):
        state.activity_events.append(
            AgentExecutionEvent(
                agent=agent,
                action=step,
                status=status,
                runtime=runtime,
                duration_ms=duration,
                summary=summary,
                error_code=error_code,
            )
        )

    def create_action_plan(self, state: CareerWorkflowState) -> CareerActionPlan:
        """Returns the final compiled output from the current state."""
        return CareerActionPlan(
            target_opportunity=state.selected_opportunity,
            resume_evidence_summary="Processed" if state.resume_analysis else None,
            priority_skill_gaps=state.skill_builder_plan.priority_gaps
            if state.skill_builder_plan
            else [],
            recommended_resources=state.skill_builder_plan.recommended_resources
            if state.skill_builder_plan
            else [],
            learning_plan=state.skill_builder_plan.learning_steps
            if state.skill_builder_plan
            else [],
            portfolio_project=state.skill_builder_plan.portfolio_project
            if state.skill_builder_plan
            else None,
            workflow_status="Complete" if state.skill_builder_plan else "Incomplete",
        )
