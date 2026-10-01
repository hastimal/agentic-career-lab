from agentic_career_lab.models import OpportunityMatch, OpportunitySearchQuery, StudentProfile
from agentic_career_lab.providers.base import OpportunityProvider
from agentic_career_lab.routing import HybridRouter, RoutingEvent, TaskType
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

        # Opportunity Search Routing
        search_route = HybridRouter.route(TaskType.OPPORTUNITY_SEARCH)
        provider_name = (
            "Mock Provider" if "Mock" in self.provider.__class__.__name__ else "Adzuna API"
        )
        self.events.append(
            RoutingEvent(
                task_type=str(search_route.task_type),
                runtime=f"{search_route.runtime} / {provider_name}",
                reason=search_route.reason,
                privacy_level=str(search_route.privacy_level),
                duration_ms=50.0,
            ).model_dump()
        )

        opportunities = self.provider.search(query)

        # Requirement Interpretation Routing
        extract_route = HybridRouter.route(TaskType.REQUIREMENT_INTERPRETATION)
        self.events.append(
            RoutingEvent(
                task_type=str(extract_route.task_type),
                runtime=str(extract_route.runtime),
                reason=extract_route.reason,
                privacy_level=str(extract_route.privacy_level),
                duration_ms=10.0,
            ).model_dump()
        )

        for opp in opportunities:
            if not opp.requirements:
                opp.requirements = self.extractor.extract(opp.description)

        # Skill Matching Routing
        match_route = HybridRouter.route(TaskType.SKILL_MATCHING)
        self.events.append(
            RoutingEvent(
                task_type=str(match_route.task_type),
                runtime=str(match_route.runtime),
                reason=match_route.reason,
                privacy_level=str(match_route.privacy_level),
                duration_ms=10.0,
            ).model_dump()
        )

        matches = [self.matcher.match(profile, opp) for opp in opportunities]

        return matches
