import os

import httpx

from agentic_career_lab.models import Opportunity
from agentic_career_lab.providers.base import OpportunityProvider, OpportunitySearchQuery


class ProviderError(Exception):
    pass


class ProviderUnavailableError(ProviderError):
    pass


class ProviderAuthenticationError(ProviderError):
    pass


class ProviderResponseError(ProviderError):
    pass


class AdzunaOpportunityProvider(OpportunityProvider):
    def __init__(self):
        self.app_id = os.environ.get("ADZUNA_APP_ID")
        self.app_key = os.environ.get("ADZUNA_APP_KEY")
        self.country = os.environ.get("ADZUNA_COUNTRY", "us")
        self.base_url = "https://api.adzuna.com/v1/api"

        if not self.app_id or not self.app_key:
            raise ProviderUnavailableError(
                "Live job search is not configured. Add Adzuna credentials or use Demo Data."
            )

    def search(self, query: OpportunitySearchQuery) -> list[Opportunity]:
        url = f"{self.base_url}/jobs/{self.country}/search/1"

        # Build search terms
        what = query.role
        if query.internship_only:
            what = f"{what} intern internship"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": what,
            "where": query.location,
            "results_per_page": 10,
        }

        try:
            r = httpx.get(url, params=params, timeout=10.0)
        except httpx.TimeoutException as e:
            raise ProviderUnavailableError(
                "Live job search is temporarily unavailable. Timeout occurred."
            ) from e
        except Exception as e:
            raise ProviderUnavailableError("Live job search is temporarily unavailable.") from e

        if r.status_code in (401, 403):
            raise ProviderAuthenticationError(
                "Adzuna authentication failed. Please check your credentials."
            )
        if r.status_code == 429:
            raise ProviderUnavailableError(
                "Live job search is temporarily unavailable. Rate limit exceeded."
            )
        if r.status_code != 200:
            raise ProviderResponseError(
                f"Live job search is temporarily unavailable. Status: {r.status_code}"
            )

        data = r.json()
        results = data.get("results", [])

        opportunities = []
        seen_keys = set()

        for job in results:
            # Source URL must be present
            redirect_url = job.get("redirect_url")
            if not redirect_url:
                continue

            job_id = job.get("id") or str(hash(redirect_url))
            title = job.get("title", "")
            company = job.get("company", {}).get("display_name", "Unknown Company")

            dedup_key = f"{job_id}-{title}-{company}"
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            locations = job.get("location", {}).get("display_name", "")
            description = job.get("description", "")

            # Since Adzuna doesn't give us structured requirements directly in this endpoint,
            # we populate description and leave requirements empty for the extraction layer to process
            opp = Opportunity(
                opportunity_id=str(job_id),
                role=title,
                company=company,
                location=locations,
                source_url=redirect_url,
                description=description,
                is_demo=False,
                requirements=[],
                why_relevant="",
            )
            opportunities.append(opp)

        return opportunities
