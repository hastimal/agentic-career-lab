from unittest.mock import patch

import pytest

from agentic_career_lab.providers.adzuna import (
    AdzunaOpportunityProvider,
    ProviderAuthenticationError,
    ProviderUnavailableError,
)
from agentic_career_lab.providers.base import OpportunitySearchQuery


@pytest.fixture
def adzuna_env(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "test_id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test_key")


def test_missing_credentials(monkeypatch):
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)
    with pytest.raises(ProviderUnavailableError, match="not configured"):
        AdzunaOpportunityProvider()


def test_search_success(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(
        role="AI Engineer", location="Texas", internship_only=False, keywords=[]
    )

    mock_response_data = {
        "results": [
            {
                "id": "123",
                "title": "AI Engineer",
                "company": {"display_name": "TestCorp"},
                "location": {"display_name": "Texas"},
                "description": "A great job",
                "redirect_url": "https://example.com",
            }
        ]
    }

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_response_data

    with patch("httpx.get", return_value=MockResponse()):
        results = provider.search(query)
        assert len(results) == 1
        assert results[0].role == "AI Engineer"
        assert results[0].company == "TestCorp"
        assert results[0].location == "Texas"
        assert str(results[0].source_url) == "https://example.com/"
        assert results[0].is_demo is False


def test_internship_only_query(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(
        role="Software", location="Remote", internship_only=True, keywords=[]
    )

    class MockResponse:
        status_code = 200

        def json(self):
            return {"results": []}

    with patch("httpx.get", return_value=MockResponse()) as mock_get:
        provider.search(query)
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "intern" in kwargs["params"]["what"].lower()


def test_auth_error(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(role="SWE", location="", internship_only=False, keywords=[])

    class MockResponse:
        status_code = 401

    with patch("httpx.get", return_value=MockResponse()):
        with pytest.raises(ProviderAuthenticationError):
            provider.search(query)


def test_rate_limit_error(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(role="SWE", location="", internship_only=False, keywords=[])

    class MockResponse:
        status_code = 429

    with patch("httpx.get", return_value=MockResponse()):
        with pytest.raises(ProviderUnavailableError, match="Rate limit"):
            provider.search(query)


def test_deduplication(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(role="SWE", location="", internship_only=False, keywords=[])

    mock_response_data = {
        "results": [
            {
                "id": "1",
                "title": "SWE",
                "company": {"display_name": "TestCorp"},
                "redirect_url": "https://example.com/1",
            },
            {
                "id": "1",
                "title": "SWE",
                "company": {"display_name": "TestCorp"},
                "redirect_url": "https://example.com/1",
            },
        ]
    }

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_response_data

    with patch("httpx.get", return_value=MockResponse()):
        results = provider.search(query)
        assert len(results) == 1


def test_missing_url_skipped(adzuna_env):
    provider = AdzunaOpportunityProvider()
    query = OpportunitySearchQuery(role="SWE", location="", internship_only=False, keywords=[])

    mock_response_data = {
        "results": [
            {
                "id": "1",
                "title": "SWE",
                "company": {"display_name": "TestCorp"},
                # no redirect_url
            },
            {
                "id": "2",
                "title": "SWE 2",
                "company": {"display_name": "TestCorp"},
                "redirect_url": "https://example.com",
            },
        ]
    }

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_response_data

    with patch("httpx.get", return_value=MockResponse()):
        results = provider.search(query)
        assert len(results) == 1
        assert results[0].opportunity_id == "2"
