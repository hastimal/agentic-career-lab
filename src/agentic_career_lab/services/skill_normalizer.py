class SkillNormalizer:
    def __init__(self):
        self.aliases = {
            "gcp": "Google Cloud",
            "google cloud platform": "Google Cloud",
            "k8s": "Kubernetes",
            "aws": "Amazon Web Services",
            "azure": "Microsoft Azure",
            "docker": "Docker",
            "postgres": "PostgreSQL",
            "rest": "REST APIs",
        }

    def normalize(self, skill: str) -> str:
        lower_skill = skill.lower().strip()
        return self.aliases.get(lower_skill, skill.strip())
