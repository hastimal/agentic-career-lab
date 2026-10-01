from agentic_career_lab.models import Opportunity, OpportunityRequirement, RequirementType

from .base import OpportunityProvider, OpportunitySearchQuery


class MockOpportunityProvider(OpportunityProvider):
    def search(self, query: OpportunitySearchQuery) -> list[Opportunity]:
        return [
            Opportunity(
                opportunity_id="mock-1",
                role="AI Engineering Intern",
                company="Example Tech Corp",
                location="Texas",
                source_url="https://example.com/jobs/ai-engineering-intern",  # type: ignore[arg-type]
                description="Join our team to build scalable AI systems using Python, Docker, and Google Cloud.",
                requirements=[
                    OpportunityRequirement(
                        skill="Python", req_type=RequirementType.REQUIRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="Docker", req_type=RequirementType.REQUIRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="Google Cloud", req_type=RequirementType.REQUIRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="Vertex AI", req_type=RequirementType.PREFERRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="Kubernetes", req_type=RequirementType.PREFERRED, context=""
                    ),
                ],
                why_relevant="Demo data role",
            ),
            Opportunity(
                opportunity_id="mock-2",
                role="Cloud Engineering Intern",
                company="Demo Systems Inc",
                location="Remote",
                source_url="https://example.com/jobs/cloud-engineering-intern",  # type: ignore[arg-type]
                description="We need a cloud engineer intern to help deploy backend services.",
                requirements=[
                    OpportunityRequirement(
                        skill="Python", req_type=RequirementType.REQUIRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="Google Cloud", req_type=RequirementType.REQUIRED, context=""
                    ),
                    OpportunityRequirement(
                        skill="SQL", req_type=RequirementType.PREFERRED, context=""
                    ),
                ],
                why_relevant="Demo data role",
            ),
        ]
