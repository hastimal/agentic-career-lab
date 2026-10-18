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
        num_weeks = max(1, duration_weeks)

        # Distribute skills and milestones across the exact requested number of weeks
        if num_weeks == 2:
            mid = (
                max(1, len(missing_skills) // 2) if len(missing_skills) > 1 else len(missing_skills)
            )
            w1_skills = missing_skills[:mid] if missing_skills else ["Core Skills"]
            w2_skills = missing_skills[mid:] if len(missing_skills) > 1 else missing_skills

            # Map resources to activity tasks
            w1_res = self.catalog.get_resources_for_skill(w1_skills[0]) if w1_skills else []
            w1_res_map = {}
            for idx, r in enumerate(w1_res[:3]):
                w1_res_map[idx] = r.resource_id

            w2_res = self.catalog.get_resources_for_skill(w2_skills[0]) if w2_skills else []
            w2_res_map = {}
            for idx, r in enumerate(w2_res[:3]):
                w2_res_map[idx] = r.resource_id

            steps.append(
                LearningStep(
                    week=1,
                    focus="Core Foundations & Tooling Setup",
                    skills=w1_skills,
                    activities=[
                        "Review official documentation and core architectural concepts",
                        "Complete interactive 'Hello World' lab or setup walkthrough",
                        "Configure local testing and development environment",
                    ],
                    expected_output="Configured development environment and verified beginner exercise",
                    activity_resource_ids=w1_res_map,
                )
            )
            steps.append(
                LearningStep(
                    week=2,
                    focus="Practical Implementation & Integration",
                    skills=w2_skills,
                    activities=[
                        "Implement end-to-end prototype incorporating target skill requirements",
                        "Write unit tests validating expected behavior and boundary conditions",
                        "Document architectural decisions and deployment instructions in README",
                    ],
                    expected_output="Functional code repository with automated tests and architecture summary",
                    activity_resource_ids=w2_res_map,
                )
            )
        else:
            # 4-week structured curriculum (Week 1: Fundamentals, Week 2: Deep Dive, Week 3: Integration, Week 4: Capstone)
            primary_skills = (
                missing_skills[: len(missing_skills) // 2]
                if len(missing_skills) >= 2
                else missing_skills
            )
            secondary_skills = (
                missing_skills[len(missing_skills) // 2 :]
                if len(missing_skills) >= 2
                else missing_skills
            )

            w1_res = (
                self.catalog.get_resources_for_skill(primary_skills[0]) if primary_skills else []
            )
            w1_map = {idx: r.resource_id for idx, r in enumerate(w1_res[:3])}

            w2_res = (
                self.catalog.get_resources_for_skill(primary_skills[0]) if primary_skills else []
            )
            w2_map = {idx: r.resource_id for idx, r in enumerate(w2_res[1:4])}

            w3_res = (
                self.catalog.get_resources_for_skill(secondary_skills[0])
                if secondary_skills
                else []
            )
            w3_map = {idx: r.resource_id for idx, r in enumerate(w3_res[:3])}

            w4_res = (
                self.catalog.get_resources_for_skill(missing_skills[0]) if missing_skills else []
            )
            w4_map = {idx: r.resource_id for idx, r in enumerate(w4_res[-3:])}

            steps.append(
                LearningStep(
                    week=1,
                    focus="Core Fundamentals & Development Environment",
                    skills=primary_skills or ["Foundational Architecture"],
                    activities=[
                        "Read official documentation and architectural patterns",
                        "Install CLI tools, SDKs, and configure credentials",
                        "Complete initial guided tutorial with self-paced validation",
                    ],
                    expected_output="Working local development environment and verified starter exercise",
                    activity_resource_ids=w1_map,
                )
            )
            steps.append(
                LearningStep(
                    week=2,
                    focus="Intermediate Application & Hands-on Labs",
                    skills=primary_skills or ["Intermediate Concepts"],
                    activities=[
                        "Complete practical hands-on labs on official learning platforms",
                        "Build modular component isolating core APIs and error handling",
                        "Write unit and integration tests using pytest",
                    ],
                    expected_output="Tested service module with error handling and test suite",
                    activity_resource_ids=w2_map,
                )
            )
            steps.append(
                LearningStep(
                    week=3,
                    focus="Advanced Architecture & Cloud/Container Integration",
                    skills=secondary_skills or ["Integration & Deployment"],
                    activities=[
                        "Integrate service with containerization, API routing, and telemetry",
                        "Apply security best practices (least privilege, environment variables)",
                        "Conduct peer code review and benchmark performance",
                    ],
                    expected_output="Containerized microservice with health checks and logging",
                    activity_resource_ids=w3_map,
                )
            )
            steps.append(
                LearningStep(
                    week=4,
                    focus="Portfolio Capstone & Resume Evidence Deliverable",
                    skills=missing_skills or ["Full Stack Synthesis"],
                    activities=[
                        "Assemble capstone repository demonstrating end-to-end capabilities",
                        "Record demo walkthrough or architectural design document",
                        "Draft evidence-backed bullet points for resume update",
                    ],
                    expected_output="Production-ready GitHub repository with README, demo, and verified evidence",
                    activity_resource_ids=w4_map,
                )
            )

        resources = []
        for s in missing_skills:
            resources.extend(self.catalog.get_resources_for_skill(s))

        project = PortfolioProject(
            title=f"{target_role} Practical Capstone Project",
            objective=f"Demonstrate verified proficiency in {', '.join(missing_skills[:3]) if missing_skills else 'target role competencies'}",
            skills_practiced=missing_skills,
            deliverables=[
                "Production-ready Git repository",
                "Comprehensive README with architecture diagram",
                "Automated test suite",
            ],
            evidence_created=[
                "Measurable project deliverable",
                "Verifiable code repository",
                "Hands-on implementation experience",
            ],
        )

        return SkillBuilderPlan(
            target_role=target_role,
            strengths=strengths,
            priority_gaps=gaps,
            learning_steps=steps,
            recommended_resources=resources,
            portfolio_project=project,
            summary=f"Personalized {num_weeks}-week roadmap targeting {len(missing_skills)} identified skill gap(s) for {target_role}.",
        )


FakePlanningLLM = DeterministicPlanningLLM


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
