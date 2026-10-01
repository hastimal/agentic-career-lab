# ruff: noqa: E402
import json
from typing import Protocol


class PlanningError(Exception):
    pass

from agentic_career_lab.llm.gemini import CloudLLM
from agentic_career_lab.models import (
    EvidenceStatus,
    LearningStep,
    PortfolioProject,
    SkillBuilderPlan,
    SkillGap,
)
from agentic_career_lab.services.learning_resources import ResourceCatalog


class PlanningLLM(Protocol):
    def is_available(self) -> bool: ...
    def create_learning_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan: ...


class DeterministicPlanningLLM:
    def __init__(self, is_online: bool = True):
        self.catalog = ResourceCatalog()
        self.is_online = is_online

    def is_available(self) -> bool:
        return self.is_online

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



class CloudPlanningLLM:
    def __init__(self, client: CloudLLM):
        self.client = client
        self.catalog = ResourceCatalog()

    def is_available(self) -> bool:
        return self.client.is_available()

    def create_learning_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan:
        missing_skills = [
            g.skill for g in gaps if g.status in (EvidenceStatus.MISSING, EvidenceStatus.PARTIAL)
        ]

        prompt = f"""
        You are a Career Planning Agent. Create a {duration_weeks}-week learning plan for a {target_role}.
        The student already has: {", ".join(strengths)}.
        The student is missing: {", ".join(missing_skills)}.
        Return a JSON response with:
        - "learning_steps": list of objects with "week" (int), "focus" (str), "skills" (list), "activities" (list), "expected_output" (str)
        - "portfolio_project": object with "title", "objective", "skills_practiced" (list), "deliverables" (list), "evidence_created" (list)
        - "summary": (str)
        """

        try:
            response_text = self.client.generate(prompt)
            data = json.loads(response_text)

            steps = []
            for s in data.get("learning_steps", []):
                steps.append(
                    LearningStep(
                        week=s.get("week", 1),
                        focus=s.get("focus", ""),
                        skills=s.get("skills", []),
                        activities=s.get("activities", []),
                        expected_output=s.get("expected_output", ""),
                    )
                )

            project_data = data.get("portfolio_project", {})
            project = PortfolioProject(
                title=project_data.get("title", "Integration Project"),
                objective=project_data.get("objective", ""),
                skills_practiced=project_data.get("skills_practiced", []),
                deliverables=project_data.get("deliverables", []),
                evidence_created=project_data.get("evidence_created", []),
            )

            resources = []
            for s in missing_skills:
                resources.extend(self.catalog.get_resources_for_skill(s))

            return SkillBuilderPlan(
                target_role=target_role,
                strengths=strengths,
                priority_gaps=gaps,
                learning_steps=steps,
                recommended_resources=resources,
                portfolio_project=project,
                summary=data.get("summary", "Cloud-generated plan."),
            )
        except Exception as e:
            raise PlanningError(f"Cloud generation or parsing failed: {e}") from e

class Planner:
    def __init__(self, llm: PlanningLLM):
        self.llm = llm

    def generate_plan(
        self, target_role: str, strengths: list[str], gaps: list[SkillGap], duration_weeks: int
    ) -> SkillBuilderPlan:
        return self.llm.create_learning_plan(target_role, strengths, gaps, duration_weeks)
