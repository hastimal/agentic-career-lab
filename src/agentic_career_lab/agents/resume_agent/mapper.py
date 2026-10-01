from agentic_career_lab.models import (
    OpportunityRequirement,
    ResumeEvidence,
    RequirementEvidenceMatch,
    EvidenceStatus,
)
from agentic_career_lab.services.skill_normalizer import SkillNormalizer


class RequirementMapper:
    def __init__(self, normalizer: SkillNormalizer):
        self.normalizer = normalizer

    def map_requirements(
        self, requirements: list[OpportunityRequirement], evidence: ResumeEvidence
    ) -> list[RequirementEvidenceMatch]:
        normalized_skills = {
            self.normalizer.normalize(s) for s in evidence.skills + evidence.technologies
        }

        matches = []
        for req in requirements:
            norm_req = self.normalizer.normalize(req.skill)

            if norm_req in normalized_skills:
                matches.append(
                    RequirementEvidenceMatch(
                        requirement=req.skill,
                        status=EvidenceStatus.DEMONSTRATED,
                        evidence=f"Found explicit evidence of {req.skill} in resume.",
                        explanation="",
                    )
                )
            else:
                # Basic partial
                is_partial = False
                for s_skill in normalized_skills:
                    if norm_req in s_skill or s_skill in norm_req:
                        is_partial = True
                        break

                if is_partial:
                    matches.append(
                        RequirementEvidenceMatch(
                            requirement=req.skill,
                            status=EvidenceStatus.PARTIAL,
                            evidence="",
                            explanation=f"Resume shows partial alignment for {req.skill}.",
                        )
                    )
                else:
                    matches.append(
                        RequirementEvidenceMatch(
                            requirement=req.skill,
                            status=EvidenceStatus.MISSING,
                            evidence="",
                            explanation=f"No evidence found for {req.skill}.",
                        )
                    )
        return matches
