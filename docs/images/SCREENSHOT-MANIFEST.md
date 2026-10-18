# UI Screenshot Manifest (v0.9.0)

This manifest records every verified application screenshot captured during the v0.9.0 release preparation.
All screenshots were captured against the live Streamlit application running on `http://localhost:8501` using Playwright Chromium with a standardized desktop viewport (1440 × 1000) and synthetic student profile data (`Alex Chen`, Junior Computer Science, targeting `AI Engineering Intern`).

---

## 📸 Verified Screenshot Inventory

| Filename | Streamlit Page Name | Expected Heading / Element | Actual Heading Verified | Viewport Dimensions | Status | Visual Highlights & Notes |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| `ui-dashboard.png` | Dashboard | Hero: `Agentic Career Lab`, `⚡ Quick Actions` | `Agentic Career Lab` | 1440 × 1000 | ✅ Verified | Hero banner, 3-stage Career Preparation Tracker, 4 functional Quick Actions cards (`Set Up My Profile`, `Find Matching Jobs`, `Compare My Resume`, `Identify Skill Gaps`). |
| `ui-my-profile.png` | My Profile | `👤 My Profile` | `👤 My Profile` | 1440 × 1000 | ✅ Verified | Academic background, graduation year, target career role, location preference, self-reported skills, and demo student profile loader. |
| `ui-job-explorer.png` | Job Explorer | `🎯 Job Explorer` | `🎯 Job Explorer` | 1440 × 1000 | ✅ Verified | Prefilled search parameters from profile, provider mode toggle (Deterministic Mock with `DEMO DATA` badge vs Adzuna API), opportunity results with verifiable requirements. |
| `ui-my-resume.png` | My Resume | `📄 My Resume` | `📄 My Resume` | 1440 × 1000 | ✅ Verified | Synthetic resume (`sample_resume.docx`) upload confirmation, local memory parsing, privacy notice, and local Gemma 4 evidence extraction triggers. |
| `ui-skill-gap-analysis.png` | Skill Gap Analysis | `🔍 Skill Gap Analysis` | `🔍 Skill Gap Analysis` | 1440 × 1000 | ✅ Verified | Transparent 3-category breakdown: Demonstrated Strengths (Verified with Evidence), Mentioned / Partial Skills, and Missing Job Requirements with status explanations. |
| `ui-learning-hub.png` | Learning Hub | `📚 Learning Hub` | `📚 Learning Hub` | 1440 × 1000 | ✅ Verified | Curated 104-resource catalog with compact dark cards, small canonical provider icons (Google Cloud, Hugging Face, etc.), metadata chips, and filter controls. |
| `ui-learning-plan.png` | My Learning Plan | `🗺️ My Learning Plan` | `🗺️ My Learning Plan` | 1440 × 1000 | ✅ Verified | Roadmap duration toggle, uncheck-by-default Cloud AI consent guard, Continue Learning recommendation banner, 4 guided tabs (`WATCH`, `LEARN`, `PRACTICE`, `BUILD`), compact resource cards, and checklist evidence fields. |
| `ui-career-report.png` | Career Report | `📋 Career Action Report` | `📋 Career Action Report` | 1440 × 1000 | ✅ Verified | Comprehensive action report summary showing target role, verified resume status, skill gaps, weekly milestones, capstone project, and Markdown download button. |
| `ui-activity-diagnostics.png` | Activity & Diagnostics | `📊 Activity & Diagnostics` | `📊 Activity & Diagnostics` | 1440 × 1000 | ✅ Verified | Student Milestone Timeline with student-friendly status badges (`Completed`, `Notice`), separate collapsed technical OpenTelemetry diagnostics. |
| `ui-career-journey-tracker.png` | My Resume (Tracker in Journey) | `Career Journey Progress: 33% Complete` | `Career Journey Progress: 33% Complete` | 1440 × 1000 | ✅ Verified | Interactive, clickable 3-stage tracker displaying active progress (`1. Job Selected` complete, `2. Analyze Resume` in progress) and "Continue Journey" navigation button. |

---

## 🔒 Verification & Compliance Notes

1. **No Personal Information (Zero PII)**: All captured views utilize synthetic student data (`Alex Chen`) and public mock company positions (`Example Tech Corp`).
2. **Accurate Page Heading Match**: Every image filename directly maps to its canonical Streamlit view with assertions verifying matching `h1` titles and content before capture.
3. **No Large Thumbnails or Banners**: Resource cards strictly adhere to the compact design specification with 20px provider favicons inside 28×28px wrappers.
4. **Browser Acceptance Parity**: All 10 views reflect the exact workflow traversed by `scripts/test_browser_acceptance.py`.
