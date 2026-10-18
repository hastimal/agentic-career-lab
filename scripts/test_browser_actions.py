import os

from playwright.sync_api import sync_playwright


def run_chat_actions_browser_tests():
    print("=" * 65)
    print("STARTING ASK CAREER AI INTERACTIVE ACTIONS BROWSER SUITE")
    print("=" * 65)

    os.makedirs("docs/images", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        # -------------------------------------------------------------
        # FLOW A: Ask Career AI -> Find matching jobs -> Select This Job -> Verify My Resume
        # -------------------------------------------------------------
        print("\n[FLOW A] Testing FIND_JOBS and SELECT_JOB action...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector("text=Agentic Career Lab", timeout=20000)

        sidebar = page.locator("[data-testid='stSidebar']")
        sidebar.locator("button:has-text('Ask Career AI')").click()
        page.wait_for_selector("h1:has-text('Ask Career AI')", timeout=15000)

        # Submit query: "Find jobs matching my profile."
        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        chat_input.click()
        chat_input.fill("Find jobs matching my profile.")
        page.keyboard.press("Enter")

        # Wait for assistant response and Select button to appear
        print("  Waiting for Job Scout results and SELECT_JOB action button...")
        select_btn = page.locator("button:has-text('Select:')").first
        select_btn.wait_for(state="visible", timeout=150000)

        # Capture screenshot for FLOW A
        page.screenshot(path="docs/images/ui-agent-chat-job-action.png")
        print("  ✓ Captured docs/images/ui-agent-chat-job-action.png")

        # Click the action button
        print("  Clicking SELECT_JOB action...")
        select_btn.click()
        page.wait_for_timeout(3000)

        # Verify navigation to My Resume with target role displayed
        try:
            page.wait_for_selector("text=My Resume", timeout=15000)
            page.wait_for_selector("text=Target Role:", timeout=15000)
            print("  ✓ FLOW A Passed: Opportunity selected and navigated to My Resume")
        except Exception as e:
            page.screenshot(path="scratch/flow_a_fail.png")
            print(f"  ✗ FLOW A Failed. Current text: {page.locator('body').inner_text()[:300]}")
            raise e

        # -------------------------------------------------------------
        # FLOW B: Recommend Docker resources -> Open Resource -> Verify Link
        # -------------------------------------------------------------
        print("\n[FLOW B] Testing RECOMMEND_RESOURCES and OPEN_LEARNING_RESOURCE action...")
        sidebar.locator("button:has-text('Ask Career AI')").click()
        page.wait_for_selector("h1:has-text('Ask Career AI')", timeout=15000)

        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        chat_input.click()
        chat_input.fill("Recommend free Docker courses.")
        page.keyboard.press("Enter")

        print("  Waiting for ResourceCatalog results and OPEN_LEARNING_RESOURCE link...")
        # Link button starts with 🔗 Open: or has link to https
        open_link = page.locator("a:has-text('Open:')").first
        open_link.wait_for(state="visible", timeout=150000)
        href = open_link.get_attribute("href")
        print(f"  ✓ Verified canonical target link: {href}")
        assert href and href.startswith("https://"), f"Invalid resource href: {href}"

        page.screenshot(path="docs/images/ui-agent-chat-resource-action.png")
        print("  ✓ Captured docs/images/ui-agent-chat-resource-action.png")
        print("  ✓ FLOW B Passed: Canonical safe HTTPS resource link verified")

        # -------------------------------------------------------------
        # FLOW C: Learning Plan -> Complete one task -> What should I learn next? -> Continue Learning
        # -------------------------------------------------------------
        print("\n[FLOW C] Testing NEXT_LEARNING_ACTION and CONTINUE_LEARNING action...")
        # First ensure a plan is generated in My Learning Plan
        sidebar.locator("button:has-text('My Learning Plan')").click()
        page.wait_for_selector("h1:has-text('My Learning Plan')", timeout=20000)

        # In My Resume / Plan, let's make sure we have a plan generated
        gen_plan_btn = page.locator("button:has-text('Generate Learning Plan')")
        if gen_plan_btn.is_visible():
            print("  Generating learning plan...")
            gen_plan_btn.click()
            page.wait_for_selector("text=Roadmap Milestones", timeout=45000)
            print("  ✓ Learning plan generated")

        # Find checklist item if available or navigate to chat
        sidebar.locator("button:has-text('Ask Career AI')").click()
        page.wait_for_selector("h1:has-text('Ask Career AI')", timeout=20000)

        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        chat_input.click()
        chat_input.fill("What should I learn next?")
        page.keyboard.press("Enter")

        print("  Waiting for CONTINUE_LEARNING action button...")
        cont_btn = page.locator(
            "button:has-text('Continue Learning'), button:has-text('Create Learning Plan')"
        ).first
        cont_btn.wait_for(state="visible", timeout=150000)

        page.screenshot(path="docs/images/ui-agent-chat-continue-learning.png")
        print("  ✓ Captured docs/images/ui-agent-chat-continue-learning.png")

        # Click Continue Learning and verify navigation to My Learning Plan
        cont_btn.click()
        page.wait_for_selector("h1:has-text('My Learning Plan')", timeout=20000)
        print("  ✓ FLOW C Passed: Navigated to My Learning Plan via Continue Learning")

        # -------------------------------------------------------------
        # FLOW D: Show my career report -> View Career Report
        # -------------------------------------------------------------
        print("\n[FLOW D] Testing SUMMARIZE_CAREER_STATUS and VIEW_CAREER_REPORT action...")
        sidebar.locator("button:has-text('Ask Career AI')").click()
        page.wait_for_selector("h1:has-text('Ask Career AI')", timeout=20000)

        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        chat_input.click()
        chat_input.fill("Show my career report.")
        page.keyboard.press("Enter")

        print("  Waiting for VIEW_CAREER_REPORT or Prerequisite action button...")
        report_action_btn = page.locator(
            "button:has-text('View Career Report'), button:has-text('Analyze My Resume'), button:has-text('Generate Learning Plan'), button:has-text('Choose a Job')"
        ).first
        report_action_btn.wait_for(state="visible", timeout=150000)

        page.screenshot(path="docs/images/ui-agent-chat-report-action.png")
        print("  ✓ Captured docs/images/ui-agent-chat-report-action.png")
        print(
            f"  ✓ FLOW D Passed: Action button '{report_action_btn.inner_text()}' rendered correctly with prerequisites check"
        )

        # -------------------------------------------------------------
        # FLOW E: Skill gap regression test
        # -------------------------------------------------------------
        print("\n[FLOW E] Testing regression on evidence-based Skill Gap Analysis action...")
        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        chat_input.click()
        chat_input.fill("What skills am I missing?")
        page.keyboard.press("Enter")

        gap_btn = page.locator(
            "button:has-text('View My Skill Gap Analysis'), button:has-text('Analyze My Resume'), button:has-text('Choose a Job')"
        ).first
        gap_btn.wait_for(state="visible", timeout=150000)
        print(
            f"  ✓ FLOW E Passed: Skill gap action button '{gap_btn.inner_text()}' rendered safely"
        )

        browser.close()

    print("\n" + "=" * 65)
    print("ALL 5 BROWSER ACCEPTANCE FLOWS (A-E) COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_chat_actions_browser_tests()
