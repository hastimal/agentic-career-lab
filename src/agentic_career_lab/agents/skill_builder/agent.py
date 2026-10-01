from agentic_career_lab.models import EvidenceStatus, Opportunity, ResumeAnalysis, SkillBuilderPlan
from agentic_career_lab.routing import (
    CloudPlanningContext,
    HybridRouter,
    RoutingEvent,
    TaskType,
    assert_cloud_safe,
)
from agentic_career_lab.services.skill_normalizer import SkillNormalizer

from .gap_analyzer import GapAnalyzer
from .planner import DeterministicPlanningLLM, Planner, PlanningError, PlanningLLM


class SkillBuilderAgent:
    def __init__(self, llm: PlanningLLM):
        self.llm = llm
        self.normalizer = SkillNormalizer()
        self.gap_analyzer = GapAnalyzer(self.normalizer)
        self.planner = Planner(self.llm)
        self.events: list[dict[str, str | float]] = []

    def run(
        self, opportunity: Opportunity, resume_analysis: ResumeAnalysis, duration_weeks: int = 4
    ) -> SkillBuilderPlan:
        self.events.clear()

        # Routing for Gap Analysis
        gap_route = HybridRouter.route(TaskType.GAP_ANALYSIS)
        self.events.append(
            RoutingEvent(
                task_type=str(gap_route.task_type),
                runtime=str(gap_route.runtime),
                reason=gap_route.reason,
                privacy_level=str(gap_route.privacy_level),
                duration_ms=10.0,
            ).model_dump()
        )

        gaps = self.gap_analyzer.analyze(opportunity, resume_analysis)

        # Sort gaps by priority: High first, then Medium, then Low
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        gaps.sort(key=lambda x: priority_order.get(x.priority, 3))

        strengths = [
            self.normalizer.normalize(req.requirement)
            for req in resume_analysis.requirement_matches
            if req.status == EvidenceStatus.DEMONSTRATED
        ]

        # Prepare safe payload for cloud planner
        safe_payload = CloudPlanningContext(
            target_role=opportunity.role,
            required_skills=[req.skill for req in opportunity.requirements],
            demonstrated_skills=strengths,
            partial_skills=[g.skill for g in gaps if g.status == EvidenceStatus.PARTIAL],
            missing_skills=[g.skill for g in gaps if g.status == EvidenceStatus.MISSING],
            plan_duration_weeks=duration_weeks,
        )
        assert_cloud_safe(safe_payload)

        # Routing for Learning Plan
        plan_route = HybridRouter.route(TaskType.LEARNING_PLAN)

        fallback_used = False
        reason_display = plan_route.reason

        try:
            if not self.llm.is_available():
                raise PlanningError("LLM is not available")
            plan = self.planner.generate_plan(opportunity.role, strengths, gaps, duration_weeks)

            if hasattr(self.llm, "client") and hasattr(self.llm.client, "model_name") and self.llm.client.model_name:
                model_name = self.llm.client.model_name
                runtime_display = f"{plan_route.runtime} / {model_name}"
            elif hasattr(self.llm, "model_name") and self.llm.model_name:
                model_name = self.llm.model_name
                runtime_display = f"{plan_route.runtime} / {model_name}"
            else:
                runtime_display = f"{plan_route.runtime}"

        except PlanningError as e:
            fallback_used = True
            reason_display = f"Gemini / Vertex generation failed or unavailable: {str(e)}"
            runtime_display = "Python fallback"

            fallback_planner = Planner(DeterministicPlanningLLM())
            plan = fallback_planner.generate_plan(opportunity.role, strengths, gaps, duration_weeks)

        self.events.append(
            RoutingEvent(
                task_type=str(plan_route.task_type),
                runtime=runtime_display,
                reason=reason_display,
                privacy_level=str(plan_route.privacy_level),
                fallback_used=fallback_used,
                duration_ms=2100.0,
            ).model_dump()
        )

        return plan
