from google.adk import Agent

from agentic_career_lab.coordinator.career_coordinator import CareerCoordinator
from agentic_career_lab.coordinator.state import (
    CareerAction,
    CareerWorkflowState,
    LocalResumeContext,
)


class ADKCareerCoordinator:
    """Google ADK facade over the deterministic career coordinator."""

    def __init__(self, domain_coordinator: CareerCoordinator):
        self.domain_coordinator = domain_coordinator

        # Register ADK Agents exactly matching the three specialists
        self.job_scout_agent = Agent(
            name="job_scout",
            tools=[self.domain_coordinator._run_job_scout],
            instruction="Fetch and normalize internship and job opportunities deterministically.",
        )

        self.private_resume_agent = Agent(
            name="private_resume_agent",
            tools=[self._run_resume_tool],
            instruction="Analyze a resume privately using a local model.",
        )

        self.skill_builder_agent = Agent(
            name="skill_builder",
            tools=[self.domain_coordinator._run_skill_builder],
            instruction="Generate a learning plan based on skill gaps.",
        )

        # Root coordinating ADK Agent
        self.root_agent = Agent(
            name="career_coordinator",
            sub_agents=[self.job_scout_agent, self.private_resume_agent, self.skill_builder_agent],
            instruction="Coordinate the sequence of career preparation steps.",
        )

    def _run_resume_tool(self, state: CareerWorkflowState, local_resume: LocalResumeContext):
        """Tool wrapper to pass local_resume correctly."""
        self.domain_coordinator._run_resume_agent(state, local_resume)

    def execute_action(
        self,
        action: CareerAction,
        state: CareerWorkflowState,
        local_resume: LocalResumeContext | None = None,
    ) -> CareerWorkflowState:
        """
        Executes deterministic routing using ADK registered tools directly.
        Avoids LLM reasoning overhead for UI-driven sequential steps.
        """
        try:
            if action == CareerAction.FIND_OPPORTUNITIES:
                self.job_scout_agent.tools[0](state)
            elif action == CareerAction.PREPARE_RESUME:
                self.private_resume_agent.tools[0](state, local_resume)
            elif action == CareerAction.BUILD_SKILLS:
                self.skill_builder_agent.tools[0](state)
            elif action == CareerAction.FULL_WORKFLOW:
                self.job_scout_agent.tools[0](state)
                if state.opportunities:
                    state.selected_opportunity = state.opportunities[0].opportunity
                self.private_resume_agent.tools[0](state, local_resume)
                self.skill_builder_agent.tools[0](state)

            self.domain_coordinator._log_event(
                state,
                agent="Career Coordinator",
                step=f"route_{action.value}",
                status="Success",
                runtime="Google ADK Orchestration",
                duration=0.1,
                summary=f"Successfully orchestrated {action.value}",
            )
        except Exception as e:
            self.domain_coordinator._log_event(
                state,
                agent="Career Coordinator",
                step=f"route_{action.value}",
                status="Failed",
                runtime="Google ADK Orchestration",
                duration=0.1,
                summary=f"Orchestration failed: {str(e)}",
                error_code="COORDINATOR_ERROR",
            )
            state.errors.append(str(e))

        return state

    def create_action_plan(self, state: CareerWorkflowState):
        return self.domain_coordinator.create_action_plan(state)
