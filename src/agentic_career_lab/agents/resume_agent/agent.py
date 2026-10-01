import json

from agentic_career_lab.llm.local import LocalLLM
from agentic_career_lab.models import Opportunity, ResumeAnalysis, ResumeSuggestion
from agentic_career_lab.routing import HybridRouter, RoutingEvent, TaskType
from agentic_career_lab.services.skill_normalizer import SkillNormalizer

from .extractor import ResumeExtractor
from .mapper import RequirementMapper
from .validator import ClaimValidator


class PrivateResumeAgent:
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.normalizer = SkillNormalizer()
        self.extractor = ResumeExtractor(self.llm)
        self.mapper = RequirementMapper(self.normalizer)
        self.validator = ClaimValidator(self.normalizer)
        self.events: list[dict[str, str | float]] = []

    def run(self, resume_text: str, opportunity: Opportunity | None) -> ResumeAnalysis:
        self.events.clear()

        # Routing Check for Resume Analysis
        analysis_route = HybridRouter.route(TaskType.RESUME_ANALYSIS)
        model_name = getattr(self.llm, "model_name", "gemma4:12b")
        self.events.append(
            RoutingEvent(
                task_type=str(analysis_route.task_type),
                runtime=f"{analysis_route.runtime} / {model_name}",
                reason=analysis_route.reason,
                privacy_level=str(analysis_route.privacy_level),
                duration_ms=10.0,
            ).model_dump()
        )

        if not self.llm.is_available():
            # NO CLOUD FALLBACK allowed
            raise RuntimeError(
                "Ollama is not reachable at http://localhost:11434. Local model unavailable."
            )

        evidence = self.extractor.extract(resume_text)

        matches = []
        if opportunity:
            match_route = HybridRouter.route(TaskType.SKILL_MATCHING)
            self.events.append(
                RoutingEvent(
                    task_type=str(match_route.task_type),
                    runtime=str(match_route.runtime),
                    reason=match_route.reason,
                    privacy_level=str(match_route.privacy_level),
                    duration_ms=5.0,
                ).model_dump()
            )
            matches = self.mapper.map_requirements(opportunity.requirements, evidence)

        # Routing Check for Resume Rewrite
        rewrite_route = HybridRouter.route(TaskType.RESUME_REWRITE)
        self.events.append(
            RoutingEvent(
                task_type=str(rewrite_route.task_type),
                runtime=str(rewrite_route.runtime),
                reason=rewrite_route.reason,
                privacy_level=str(rewrite_route.privacy_level),
                duration_ms=5.0,
            ).model_dump()
        )
        suggestions = self._generate_suggestions(resume_text, evidence)

        validation_route = HybridRouter.route(TaskType.CLAIM_VALIDATION)
        self.events.append(
            RoutingEvent(
                task_type=str(validation_route.task_type),
                runtime=str(validation_route.runtime),
                reason=validation_route.reason,
                privacy_level=str(validation_route.privacy_level),
                duration_ms=5.0,
            ).model_dump()
        )
        validated_suggestions = [self.validator.validate(s, evidence) for s in suggestions]

        # Calculate missing evidence simply for the output structure
        missing = [m.requirement for m in matches if m.status == "Missing"]

        return ResumeAnalysis(
            profile=None,
            requirement_matches=matches,
            missing_evidence=missing,
            suggestions=validated_suggestions,
            safety_summary="Validation complete.",
        )

    def _generate_suggestions(self, resume_text: str, evidence) -> list[ResumeSuggestion]:
        # Minimal mock implementation or relying on LLM
        prompt = "Suggest improvements for the resume. Return JSON."
        resp = self.llm.generate(prompt)

        try:
            data = json.loads(resp)
            s_list = data.get("suggestions", [])
            return [
                ResumeSuggestion(
                    original_text=s["original_text"],
                    suggested_text=s["suggested_text"],
                    evidence_used=s.get("evidence_used", []),
                )
                for s in s_list
            ]
        except Exception:
            return []
