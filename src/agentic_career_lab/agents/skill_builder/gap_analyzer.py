from agentic_career_lab.models import (
    EvidenceStatus,
    Opportunity,
    RequirementType,
    ResumeAnalysis,
    SkillGap,
)
from agentic_career_lab.services.skill_normalizer import SkillNormalizer


class GapAnalyzer:
    def __init__(self, normalizer: SkillNormalizer):
        self.normalizer = normalizer

    def analyze(self, opportunity: Opportunity, resume_analysis: ResumeAnalysis) -> list[SkillGap]:
        normalized_demonstrated = []
        normalized_partial = []

        for m in resume_analysis.requirement_matches:
            if m.status == EvidenceStatus.DEMONSTRATED:
                normalized_demonstrated.append(self.normalizer.normalize(m.requirement))
            elif m.status == EvidenceStatus.PARTIAL:
                normalized_partial.append(self.normalizer.normalize(m.requirement))

        gaps = []
        for req in opportunity.requirements:
            norm_req = self.normalizer.normalize(req.skill)

            if norm_req in normalized_demonstrated:
                status = EvidenceStatus.DEMONSTRATED
                priority = "Low"
                reason = "Already demonstrated."
            elif norm_req in normalized_partial:
                status = EvidenceStatus.PARTIAL
                if req.req_type == RequirementType.REQUIRED:
                    priority = "Medium"
                    reason = "Required but only partial evidence exists."
                else:
                    priority = "Low"
                    reason = "Preferred skill with partial evidence."
            else:
                status = EvidenceStatus.MISSING
                if req.req_type == RequirementType.REQUIRED:
                    priority = "High"
                    reason = "Required skill completely missing from resume."
                else:
                    priority = "Medium"
                    reason = "Preferred skill missing from resume."

            gaps.append(
                SkillGap(
                    skill=req.skill,
                    status=status,
                    requirement_type=req.req_type,
                    priority=priority,
                    reason=reason,
                    explanation=f"Matches status {status}.",
                )
            )

        return gaps
