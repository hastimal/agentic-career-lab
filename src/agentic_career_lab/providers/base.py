from typing import Protocol
from agentic_career_lab.models import Opportunity


class OpportunitySearchQuery:
    def __init__(self, role: str, location: str, internship_only: bool, keywords: list[str]):
        self.role = role
        self.location = location
        self.internship_only = internship_only
        self.keywords = keywords


class OpportunityProvider(Protocol):
    def search(self, query: OpportunitySearchQuery) -> list[Opportunity]: ...
