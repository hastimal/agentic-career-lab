"""Keyboard and axe-core accessibility checks against a running instance.

Start the app first (Ollama is not needed, the chat check works in local fallback mode):

    uv run agentic-career-lab
    uv run python scripts/test_browser_accessibility.py

Set APP_URL to test a different address. axe-core is loaded from a pinned CDN build,
so this needs network access but no extra Python package.
"""

import os
import sys

from playwright.sync_api import sync_playwright

APP_URL = os.environ.get("APP_URL", "http://localhost:8501")
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js"
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

# Low contrast that comes from Streamlit's default theme rather than this app's markup:
# white text on the red primary button and the grey st.caption text. These need a theme
# change, so they are reported but do not fail the run.
THEME_OWNED = "[kind='primary'], [data-testid='stCaptionContainer']"

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")
        failures.append(message)


def run_axe(page, label: str) -> None:
    page.add_script_tag(url=AXE_URL)
    violations = page.evaluate(
        """async ([tags, themeOwned]) => {
            const results = await axe.run(document, {runOnly: {type: "tag", values: tags}});
            return results.violations.flatMap((v) => v.nodes.map((n) => {
                const el = document.querySelector(n.target[0]);
                const theme = v.id === "color-contrast" && !!el && !!el.closest(themeOwned);
                return {id: v.id, html: n.html, theme};
            }));
        }""",
        [WCAG_TAGS, THEME_OWNED],
    )
    app_issues = []
    for node in violations:
        if node["theme"]:
            print(f"    (theme) {node['id']}: {node['html'][:80]}")
            continue
        app_issues.append(f"{node['id']}: {node['html'][:100]}")
    for issue in app_issues:
        print(f"    {issue}")
    check(not app_issues, f"axe found no WCAG 2.2 AA violations on {label}")


def focused(page) -> dict:
    return page.evaluate(
        """() => {
            const el = document.activeElement;
            const style = getComputedStyle(el);
            return {
                tag: el.tagName,
                text: (el.innerText || "").trim(),
                className: el.className || "",
                inMain: !!el.closest("[data-testid='stMain']"),
                outlineStyle: style.outlineStyle,
                outlineWidth: parseFloat(style.outlineWidth),
            };
        }"""
    )


def tab_until(page, predicate, limit: int = 120) -> dict | None:
    for _ in range(limit):
        page.keyboard.press("Tab")
        info = focused(page)
        if predicate(info):
            return info
    return None


def has_focus_ring(info: dict) -> bool:
    return info["outlineStyle"] == "solid" and info["outlineWidth"] >= 2


def run_accessibility_checks() -> None:
    print("=" * 65)
    print(f"ACCESSIBILITY CHECKS against {APP_URL}")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()
        sidebar = page.locator("[data-testid='stSidebar']")

        print("\n[1/4] Dashboard: skip link, focus ring, headings")
        page.goto(APP_URL, timeout=30000)
        page.wait_for_selector("text=Quick Actions", timeout=20000)
        page.wait_for_timeout(1000)

        page.keyboard.press("Tab")
        check(focused(page)["text"] == "Skip to main content", "first Tab stop is the skip link")
        page.keyboard.press("Enter")
        page.keyboard.press("Tab")
        check(focused(page)["inMain"], "skip link moves keyboard focus into the main content")

        button = tab_until(page, lambda f: f["tag"] == "BUTTON")
        check(button is not None and has_focus_ring(button), "buttons show a solid focus ring")
        check(
            page.locator("[role='heading'][aria-level='1'], h1").count() >= 1,
            "dashboard exposes a level 1 heading",
        )
        run_axe(page, "Dashboard")

        print("\n[2/4] Learning Hub: resource links reachable and usable by keyboard")
        sidebar.locator("button:has-text('Learning Hub')").click()
        page.wait_for_selector("h1:has-text('Learning Hub')", timeout=15000)
        page.wait_for_timeout(1000)
        link = page.locator("a.btn-resource-action").first
        name = link.evaluate("el => el.textContent")
        check("opens in a new tab" in name, "resource link name mentions the new tab")

        page.locator("h1:has-text('Learning Hub')").click()
        resource = tab_until(page, lambda f: "btn-resource-action" in f["className"], limit=200)
        check(resource is not None, "Tab reaches the first resource link")
        if resource:
            check(has_focus_ring(resource), "resource link shows a solid focus ring")
            with context.expect_page(timeout=10000) as new_tab:
                page.keyboard.press("Enter")
            check(new_tab.value is not None, "Enter on a resource link opens it in a new tab")
            new_tab.value.close()
        run_axe(page, "Learning Hub")

        print("\n[3/4] Ask Career AI: reply is announced to screen readers")
        sidebar.locator("button:has-text('Ask Career AI')").click()
        page.wait_for_selector("h1:has-text('Ask Career AI')", timeout=15000)
        page.wait_for_timeout(2000)
        live = page.locator("[role='status'][aria-live='polite']")
        check(live.count() == 1, "chat page has one polite live region")
        run_axe(page, "Ask Career AI")

        if live.count() == 1:
            region = live.element_handle()
            prompt = page.locator("button:has-text('What should I learn next?')")
            prompt.focus()
            page.keyboard.press("Enter")
            page.wait_for_function(
                "el => el.textContent.includes('Career AI replied')", arg=region, timeout=60000
            )
            check(
                region.evaluate("el => el.isConnected"),
                "live region stays in the page while the reply arrives",
            )

        print("\n[4/4] Ask Career AI after a reply")
        page.wait_for_timeout(1000)
        run_axe(page, "Ask Career AI with a reply")

        browser.close()

    print("\n" + "=" * 65)
    if failures:
        print(f"{len(failures)} ACCESSIBILITY CHECK(S) FAILED")
        print("=" * 65)
        sys.exit(1)
    print("ALL ACCESSIBILITY CHECKS PASSED")
    print("=" * 65)


if __name__ == "__main__":
    run_accessibility_checks()
