from agentic_career_lab.models.schemas import LearningResource


class ResourceCatalog:
    def __init__(self):
        self.catalog = {
            "Vertex AI": [
                LearningResource(
                    title="Google Cloud Vertex AI learning resources",
                    provider="Google Cloud",
                    resource_type="Documentation",
                    url="https://cloud.google.com/vertex-ai/docs",
                    skill="Vertex AI",
                    reason="Build foundational understanding of Vertex AI.",
                ),
                LearningResource(
                    title="Google Cloud Skills Boost: Vertex AI",
                    provider="Google Cloud Skills Boost",
                    resource_type="Lab / Course",
                    url="https://www.cloudskillsboost.google/paths/11",
                    skill="Vertex AI",
                    reason="Gain practical experience.",
                ),
                LearningResource(
                    title="Google Cloud Tech",
                    provider="Google Cloud Tech",
                    resource_type="YouTube",
                    url=None,  # Generic video search
                    skill="Vertex AI",
                    reason="See practical walkthroughs.",
                ),
            ],
            "Kubernetes": [
                LearningResource(
                    title="Kubernetes Basics",
                    provider="Kubernetes.io",
                    resource_type="Documentation",
                    url="https://kubernetes.io/docs/tutorials/kubernetes-basics/",
                    skill="Kubernetes",
                    reason="Official tutorial for learning Kubernetes fundamentals.",
                )
            ],
        }

    def get_resources_for_skill(self, skill: str) -> list[LearningResource]:
        return self.catalog.get(
            skill,
            [
                LearningResource(
                    title=f"Search for {skill} beginner tutorial",
                    provider="Web Search",
                    resource_type="General",
                    url=None,
                    skill=skill,
                    reason="Find a beginner tutorial.",
                )
            ],
        )
