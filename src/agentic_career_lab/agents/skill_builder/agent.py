from agentic_career_lab.models import EvidenceStatus, Opportunity, ResumeAnalysis, SkillBuilderPlan
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

        self.events.append({"step": "load_selected_opportunity", "status": "✓", "duration": 0.01})
        self.events.append({"step": "load_resume_evidence", "status": "✓", "duration": 0.01})

        gaps = self.gap_analyzer.analyze(opportunity, resume_analysis)
        self.events.append({"step": "compare_requirements", "status": "✓", "duration": 0.05})

        # Sort gaps by priority: High first, then Medium, then Low
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        gaps.sort(key=lambda x: priority_order.get(x.priority, 3))
        self.events.append({"step": "prioritize_gaps", "status": "✓", "duration": 0.01})

        strengths = [
            self.normalizer.normalize(req.requirement)
            for req in resume_analysis.requirement_matches
            if req.status == EvidenceStatus.DEMONSTRATED
        ]

        plan = self.planner.generate_plan(opportunity.role, strengths, gaps, duration_weeks)
        self.events.append({"step": "build_learning_plan", "status": "✓", "duration": 2.1})
        self.events.append({"step": "recommend_project", "status": "✓", "duration": 1.2})

        return plan
