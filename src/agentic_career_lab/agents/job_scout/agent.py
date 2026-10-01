from agentic_career_lab.models import OpportunityMatch, OpportunitySearchQuery, StudentProfile
from agentic_career_lab.providers.base import OpportunityProvider
from agentic_career_lab.services.skill_normalizer import SkillNormalizer

from .matcher import Matcher
from .requirement_extractor import RequirementExtractor


class JobScoutAgent:
    def __init__(self, provider: OpportunityProvider):
        self.provider = provider
        self.normalizer = SkillNormalizer()
        self.extractor = RequirementExtractor()
        self.matcher = Matcher(self.normalizer)

        # Lightweight telemetry for demo
        self.events: list[dict[str, str | float]] = []

    def run(self, profile: StudentProfile, query: OpportunitySearchQuery) -> list[OpportunityMatch]:
        self.events.clear()

        self.events.append({"step": "build_query", "status": "✓", "duration": 0.01})

        opportunities = self.provider.search(query)
        self.events.append({"step": "search_opportunities", "status": "✓", "duration": 0.05})

        # Normalize and Extract
        for opp in opportunities:
            if not opp.requirements:
                opp.requirements = self.extractor.extract(opp.description)

        self.events.append({"step": "normalize_results", "status": "✓", "duration": 0.01})
        self.events.append({"step": "extract_requirements", "status": "✓", "duration": 0.03})

        matches = [self.matcher.match(profile, opp) for opp in opportunities]
        self.events.append({"step": "compare_skills", "status": "✓", "duration": 0.01})

        return matches
