from typing import Protocol

from agentic_career_lab.models import (
    EvidenceStatus,
    LearningStep,
    PortfolioProject,
    SkillBuilderPlan,
    SkillGap,
)
from agentic_career_lab.services.learning_resources import ResourceCatalog


class PlanningLLM(Protocol):
    def create_learning_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan: ...


class FakePlanningLLM:
    def __init__(self):
        self.catalog = ResourceCatalog()

    def create_learning_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan:
        missing_skills = [
            g.skill for g in gaps if g.status in (EvidenceStatus.MISSING, EvidenceStatus.PARTIAL)
        ]

        steps = []
        if duration_weeks >= 2:
            steps.append(
                LearningStep(
                    week=1,
                    focus="Fundamentals",
                    skills=missing_skills,
                    activities=["Read documentation", "Complete basic tutorial"],
                    expected_output="Basic understanding",
                )
            )
            steps.append(
                LearningStep(
                    week=2,
                    focus="Application",
                    skills=missing_skills,
                    activities=["Build a small script"],
                    expected_output="Working script",
                )
            )

        resources = []
        for s in missing_skills:
            resources.extend(self.catalog.get_resources_for_skill(s))

        project = PortfolioProject(
            title="Skill Integration App",
            objective="Integrate newly learned skills",
            skills_practiced=missing_skills,
            deliverables=["Codebase", "README"],
            evidence_created=["Practical usage"],
        )

        return SkillBuilderPlan(
            target_role=target_role,
            strengths=strengths,
            priority_gaps=gaps,
            learning_steps=steps,
            recommended_resources=resources,
            portfolio_project=project,
            summary="This is a deterministic fake plan.",
        )


class Planner:
    def __init__(self, llm: PlanningLLM):
        self.llm = llm

    def generate_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan:
        return self.llm.create_learning_plan(target_role, strengths, gaps, duration_weeks)
