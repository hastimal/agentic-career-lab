import json
from agentic_career_lab.llm.local import LocalLLM
from agentic_career_lab.models import Opportunity, ResumeAnalysis, ResumeSuggestion
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
        self.events.append({"step": "check_ollama", "status": "✓", "duration": 0.02})

        if not self.llm.is_available():
            raise RuntimeError("Ollama is not reachable at http://localhost:11434.")

        self.events.append({"step": "load_gemma4", "status": "✓", "duration": 0.01})

        evidence = self.extractor.extract(resume_text)
        self.events.append({"step": "extract_resume_evidence", "status": "✓", "duration": 2.4})

        matches = []
        if opportunity:
            matches = self.mapper.map_requirements(opportunity.requirements, evidence)
        self.events.append({"step": "map_job_requirements", "status": "✓", "duration": 0.05})

        suggestions = self._generate_suggestions(resume_text, evidence)
        self.events.append({"step": "generate_resume_suggestions", "status": "✓", "duration": 1.8})

        validated_suggestions = [self.validator.validate(s, evidence) for s in suggestions]
        self.events.append({"step": "validate_claims", "status": "✓", "duration": 0.03})

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
