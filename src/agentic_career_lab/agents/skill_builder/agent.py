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
from .planner import Planner, PlanningLLM


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
        if not self.llm.is_available():
            fallback_used = True

        model_name = getattr(self.llm, "model_name", "gemini-1.5-pro")
        runtime_display = (
            f"{plan_route.runtime} / {model_name}" if not fallback_used else "python fallback"
        )
        reason_display = plan_route.reason if not fallback_used else "Gemini unavailable"

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

        plan = self.planner.generate_plan(opportunity.role, strengths, gaps, duration_weeks)

        return plan
