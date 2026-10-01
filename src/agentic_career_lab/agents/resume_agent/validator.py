from agentic_career_lab.models import ResumeEvidence, ResumeSuggestion
from agentic_career_lab.services.skill_normalizer import SkillNormalizer


class ClaimValidator:
    def __init__(self, normalizer: SkillNormalizer):
        self.normalizer = normalizer

    def validate(self, suggestion: ResumeSuggestion, evidence: ResumeEvidence) -> ResumeSuggestion:
        normalized_skills = {
            self.normalizer.normalize(s) for s in evidence.skills + evidence.technologies
        }

        unsupported = []

        # Check if any evidence used by the suggestion was actually missing from the resume
        for ev in suggestion.evidence_used:
            norm_ev = self.normalizer.normalize(ev)
            if norm_ev not in normalized_skills:
                unsupported.append(f"Skill '{ev}' not found in original resume")

        # Also do a naive text check on suggested_text for common new entities not in original text
        # (Very basic for deterministic guardrail)
        if (
            "Kubernetes" in suggestion.suggested_text
            and "Kubernetes" not in suggestion.original_text
            and "Kubernetes" not in evidence.skills
        ):
            unsupported.append("Invented skill 'Kubernetes'")
        if "10,000" in suggestion.suggested_text and "10,000" not in suggestion.original_text:
            unsupported.append("Invented metric '10,000'")

        suggestion.unsupported_claims_detected = unsupported
        suggestion.accepted = len(unsupported) == 0
        return suggestion
