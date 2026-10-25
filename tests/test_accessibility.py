"""Accessibility regression tests for keyboard and screen reader support (issue #12)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from agentic_career_lab.ui_helpers import ASK_CAREER_AI, live_region_html, new_tab_link_html

APP_PATH = str(Path(__file__).resolve().parents[1] / "src" / "agentic_career_lab" / "app.py")


@pytest.fixture
def offline_app(monkeypatch):
    # Point Ollama at a closed port so the chat runs in local fallback mode.
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:9")
    return AppTest.from_file(APP_PATH, default_timeout=60)


def _live_regions(at: AppTest) -> list[str]:
    return [m.value for m in at.markdown if "aria-live" in m.value]


def test_new_tab_link_keeps_visible_label_and_announces_new_tab():
    html = new_tab_link_html(
        "https://example.com/course?a=1&b=2",
        "Start Course ↗",
        css_class="btn-resource-action",
        context="Kubernetes Basics",
    )

    assert "target='_blank'" in html
    assert "rel='noopener noreferrer'" in html
    assert "href='https://example.com/course?a=1&amp;b=2'" in html
    assert ">Start Course<span aria-hidden='true'> ↗</span>" in html
    assert "<span class='sr-only'>: Kubernetes Basics (opens in a new tab)</span>" in html


def test_new_tab_link_escapes_text_and_skips_missing_arrow():
    html = new_tab_link_html("https://example.com", "Tom's <Guide>")

    assert "Tom&#x27;s &lt;Guide&gt;" in html
    assert "aria-hidden" not in html
    assert "class=" not in html.split(">")[0]


def test_live_region_is_polite_and_escaped():
    html = live_region_html("<b>done</b>")

    assert "role='status'" in html
    assert "aria-live='polite'" in html
    assert "&lt;b&gt;done&lt;/b&gt;" in html


def test_dashboard_has_heading_and_focus_styles(offline_app):
    offline_app.run()
    assert not offline_app.exception

    page_html = "\n".join(m.value for m in offline_app.markdown)
    assert ":focus-visible" in page_html
    assert 'role="heading" aria-level="1"' in page_html


def test_chat_reply_is_announced_in_live_region(offline_app):
    offline_app.session_state["nav"] = ASK_CAREER_AI
    offline_app.run()
    assert not offline_app.exception

    regions = _live_regions(offline_app)
    assert len(regions) == 1
    assert "Career AI replied" not in regions[0]

    prompt = next(b for b in offline_app.button if "What should I learn next?" in b.label)
    prompt.click().run()
    assert not offline_app.exception

    regions = _live_regions(offline_app)
    assert len(regions) == 1
    assert "Career AI replied" in regions[0]
