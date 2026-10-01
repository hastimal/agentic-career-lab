from agentic_career_lab.models import Opportunity, StudentProfile, OpportunityMatch
from agentic_career_lab.services.skill_normalizer import SkillNormalizer


class Matcher:
    def __init__(self, normalizer: SkillNormalizer):
        self.normalizer = normalizer

    def match(self, profile: StudentProfile, opportunity: Opportunity) -> OpportunityMatch:
        normalized_student_skills = {self.normalizer.normalize(s) for s in profile.skills}

        demonstrated = []
        partial = []
        missing = []

        for req in opportunity.requirements:
            norm_req = self.normalizer.normalize(req.skill)

            if norm_req in normalized_student_skills:
                demonstrated.append(req.skill)
            else:
                # Basic partial matching: if requirement is a substring of student skill or vice versa
                is_partial = False
                for s_skill in normalized_student_skills:
                    if norm_req in s_skill or s_skill in norm_req:
                        is_partial = True
                        break

                if is_partial:
                    partial.append(req.skill)
                else:
                    missing.append(req.skill)

        why_relevant = self._generate_explanation(demonstrated, partial, missing)

        return OpportunityMatch(
            opportunity=opportunity,
            demonstrated_skills=demonstrated,
            partial_skills=partial,
            missing_skills=missing,
            why_relevant=why_relevant,
        )

    def _generate_explanation(
        self, demonstrated: list[str], partial: list[str], missing: list[str]
    ) -> str:
        parts = []
        if demonstrated:
            parts.append(f"This role aligns with your {', '.join(demonstrated)} experience.")
        if partial:
            parts.append(f"Your background provides partial alignment for {', '.join(partial)}.")
        if missing:
            parts.append(f"However, {', '.join(missing)} are not yet demonstrated.")

        if not parts:
            return "No clear alignment found based on the provided skills."

        return " ".join(parts)
