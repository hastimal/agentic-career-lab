from agentic_career_lab.models import OpportunityRequirement, RequirementType


class RequirementExtractor:
    def extract(self, description: str) -> list[OpportunityRequirement]:
        # Minimal deterministic extraction for milestone 2
        reqs = []
        lower_desc = description.lower()
        if "python" in lower_desc:
            reqs.append(
                OpportunityRequirement(
                    skill="Python", req_type=RequirementType.REQUIRED, context=""
                )
            )
        if "docker" in lower_desc:
            reqs.append(
                OpportunityRequirement(
                    skill="Docker", req_type=RequirementType.REQUIRED, context=""
                )
            )
        if "google cloud" in lower_desc or "gcp" in lower_desc:
            reqs.append(
                OpportunityRequirement(
                    skill="Google Cloud", req_type=RequirementType.REQUIRED, context=""
                )
            )
        if "kubernetes" in lower_desc or "k8s" in lower_desc:
            reqs.append(
                OpportunityRequirement(
                    skill="Kubernetes", req_type=RequirementType.PREFERRED, context=""
                )
            )
        if "vertex ai" in lower_desc:
            reqs.append(
                OpportunityRequirement(
                    skill="Vertex AI", req_type=RequirementType.PREFERRED, context=""
                )
            )
        return reqs
