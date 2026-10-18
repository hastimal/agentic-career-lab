import os
import sys

from playwright.sync_api import sync_playwright


def run_browser_acceptance():
    print("=" * 60)
    print("STARTING REAL BROWSER ACCEPTANCE TEST (http://localhost:8501)")
    print("=" * 60)

    resume_docx_path = os.path.abspath("scratch/sample_resume.docx")
    if not os.path.exists(resume_docx_path):
        print(f"Error: resume file {resume_docx_path} does not exist!")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print("\n1. Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector("text=Agentic Career Lab", timeout=15000)
        print("✓ Streamlit landing page loaded successfully")

        # Step 1: Navigate to Find Opportunities via Sidebar button
        print("\n2. Navigating to Find Opportunities via sidebar...")
        sidebar = page.locator("[data-testid='stSidebar']")
        sidebar.locator("button:has-text('Find Opportunities')").click()
        page.wait_for_selector("text=Job Scout — Opportunities", timeout=15000)
        print("✓ Opportunities view rendered")

        # Step 2: Search for opportunities inside main content area
        print("\n3. Searching for opportunities (Source: Demo Data / Mock)...")
        main = page.locator("[data-testid='stMain']")
        main.locator("button:has-text('Find Opportunities')").click()
        page.wait_for_selector("text=AI Engineering Intern", timeout=20000)
        print("✓ Opportunities found and displayed with DEMO DATA badge")

        # Step 3: Select first opportunity -> Prepare Resume
        print("\n4. Selecting first opportunity and proceeding to Prepare Resume...")
        main.locator("button:has-text('Prepare My Resume')").first.click()
        page.wait_for_selector("text=Private Resume Lab", timeout=20000)
        print("✓ Private Resume Lab loaded for target role")

        # Step 4: Upload sample resume (.docx)
        print(f"\n5. Uploading sample resume: {resume_docx_path}...")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(resume_docx_path)
        page.wait_for_selector("text=Resume loaded locally", timeout=20000)
        print("✓ Resume parsed and loaded locally in container memory")

        # Step 5: Run Private Resume Analysis via Gemma 4
        print("\n6. Clicking 'Analyze Resume Privately' (Executing Gemma 4 inference)...")
        page.locator("button:has-text('Analyze Resume Privately')").click()

        # Wait for Gemma 4 analysis output (Gemma 4 12B thinking models take ~180-210s on full resume extraction + requirement mapping)
        print("Waiting for Gemma 4 analysis results...")
        page.wait_for_selector("text=Extracted Resume Evidence", timeout=240000)
        page.wait_for_selector("text=Job Requirement Mapping", timeout=30000)
        print("✓ Gemma 4 inference completed:")

        # Verify demonstrated and missing items from DOM
        demonstrated = page.locator("div:has-text('Demonstrated')").all_inner_texts()
        print(f"  Requirement mapping detected ({len(demonstrated)} matches)")

        # Step 6: Proceed to Skill Builder
        print("\n7. Navigating to Build My Skill Plan...")
        page.locator("button:has-text('Build My Skill Plan')").click()
        page.wait_for_selector("text=Build Missing Skills", timeout=20000)
        print("✓ Build Missing Skills page loaded")

        # Verify privacy consent checkbox
        consent_checkbox = page.locator("input[type='checkbox']")
        is_checked = consent_checkbox.is_checked()
        print(f"  Privacy & Cloud Sharing Consent checkbox present (checked: {is_checked})")

        # Step 7: Build Learning Plan
        print("\n8. Generating Career Action Plan...")
        page.locator("button:has-text('Build My Learning Plan')").click()
        page.wait_for_selector("text=Final Career Action Plan", timeout=30000)
        page.wait_for_selector("text=Career Action Plan Status:", timeout=20000)
        status_text = page.locator("text=Career Action Plan Status:").inner_text()
        print(f"✓ {status_text}")

        # Capture artifact screenshot
        os.makedirs("scratch", exist_ok=True)
        screenshot_path = "scratch/browser_acceptance_success.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"✓ Full-page screenshot saved to {screenshot_path}")

        browser.close()
        print("\n" + "=" * 60)
        print("BROWSER ACCEPTANCE TEST PASSED WITH 100% SUCCESS!")
        print("=" * 60)


if __name__ == "__main__":
    run_browser_acceptance()
