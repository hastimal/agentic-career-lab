"""Navigation constants and workflow progression helpers for Agentic Career Lab."""

from html import escape
from typing import Any

# Canonical student-centric page constants
DASHBOARD = "Dashboard"
MY_PROFILE = "My Profile"
MY_RESUME = "My Resume"
JOB_EXPLORER = "Job Explorer"
SKILL_GAP_ANALYSIS = "Skill Gap Analysis"
LEARNING_HUB = "Learning Hub"
MY_LEARNING_PLAN = "My Learning Plan"
CAREER_REPORT = "Career Report"
ACTIVITY_DIAGNOSTICS = "Activity & Diagnostics"
RESUME_STUDIO = "Resume Studio"
ASK_CAREER_AI = "Ask Career AI"

# Keep original string constants for backward compatibility with tests and bookmarks
HOME = "Home"
OPPORTUNITIES = "Find Opportunities"
RESUME = "Prepare Resume"
SKILLS = "Build Skills"
ACTIVITY = "Agent Activity"

CANONICAL_PAGES = [
    DASHBOARD,
    MY_PROFILE,
    ASK_CAREER_AI,
    JOB_EXPLORER,
    MY_RESUME,
    SKILL_GAP_ANALYSIS,
    LEARNING_HUB,
    MY_LEARNING_PLAN,
    CAREER_REPORT,
    ACTIVITY_DIAGNOSTICS,
    RESUME_STUDIO,
]

LEGACY_PAGES = [
    HOME,
    OPPORTUNITIES,
    RESUME,
    SKILLS,
    ACTIVITY,
]

VALID_PAGES = set(CANONICAL_PAGES).union(set(LEGACY_PAGES))


def normalize_navigation(page: str | None) -> str:
    """Normalize input navigation string to valid page identifier."""
    if not page:
        return HOME
    if page in VALID_PAGES:
        return page
    if page == "Overview":
        return HOME
    return HOME


def get_workflow_progress(
    selected_opportunity: Any | None,
    resume_analysis: Any | None,
    skill_builder_plan: Any | None,
) -> dict[str, Any]:
    """Calculate guided student workflow progression."""
    opportunity_selected = selected_opportunity is not None
    resume_analyzed = resume_analysis is not None
    skill_plan_built = skill_builder_plan is not None

    if not opportunity_selected:
        next_step = OPPORTUNITIES
        canonical_next_step = JOB_EXPLORER
    elif not resume_analyzed:
        next_step = RESUME
        canonical_next_step = MY_RESUME
    elif not skill_plan_built:
        next_step = SKILLS
        canonical_next_step = MY_LEARNING_PLAN
    else:
        next_step = None
        canonical_next_step = CAREER_REPORT

    steps_done = sum([opportunity_selected, resume_analyzed, skill_plan_built])
    # Exact step milestones: 0%, 33%, 67%, 100%
    percent_map = {0: 0, 1: 33, 2: 67, 3: 100}
    percent_complete = percent_map[steps_done]

    return {
        "opportunity_selected": opportunity_selected,
        "resume_analyzed": resume_analyzed,
        "skill_plan_built": skill_plan_built,
        "next_step": next_step,
        "canonical_next_step": canonical_next_step,
        "percent_complete": percent_complete,
    }


# Canonical Provider Icon Mapping (Phase 2 & Phase 3)
# Explicit provider-to-domain mapping preventing unverified derivation or personal info leakage
PROVIDER_ICON_MAP = {
    # Video & Streaming Platforms
    "YouTube": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    # Major Cloud Platforms
    "Google Cloud": "https://www.gstatic.com/cgc/supercloud_favicon.ico",
    "Google Cloud Tech": "https://www.gstatic.com/cgc/supercloud_favicon.ico",
    "Google Cloud Skills": "https://www.cloudskillsboost.google/favicon.ico",
    "Google Cloud Skills Boost": "https://www.cloudskillsboost.google/favicon.ico",
    "Google (GitHub)": "https://github.githubassets.com/favicons/favicon.svg",
    "Google Cloud (GitHub)": "https://github.githubassets.com/favicons/favicon.svg",
    "AWS": "https://a0.awsstatic.com/libra-css/images/site/fav/favicon.ico",
    "Amazon Web Services (AWS)": "https://a0.awsstatic.com/libra-css/images/site/fav/favicon.ico",
    "Microsoft Learn": "https://learn.microsoft.com/favicon.ico",
    # DevOps, Containers & Kubernetes
    "Docker Inc.": "https://docs.docker.com/favicons/docs@2x.ico",
    "Docker": "https://docs.docker.com/favicons/docs@2x.ico",
    "Kubernetes": "https://kubernetes.io/images/favicon.png",
    "Kubernetes.io": "https://kubernetes.io/images/favicon.png",
    "Kubernetes / CNCF": "https://kubernetes.io/images/favicon.png",
    "Kubernetes (GitHub)": "https://github.githubassets.com/favicons/favicon.svg",
    "CNCF": "https://kubernetes.io/images/favicon.png",
    "CNCF (Cloud Native Computing Foundation)": "https://kubernetes.io/images/favicon.png",
    "Killercoda": "https://killercoda.com/favicon.ico",
    "HashiCorp Developer": "https://developer.hashicorp.com/favicon.ico",
    "TechWorld with Nana": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "KodeKloud": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "KodeKloud / Mumshad Mannambeth": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "NetworkChuck": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    # AI & Machine Learning
    "Hugging Face": "https://huggingface.co/favicon.ico",
    "Linux Foundation / PyTorch": "https://pytorch.org/assets/images/favicon.ico",
    "The Linux Foundation": "https://pytorch.org/assets/images/favicon.ico",
    "The Full Stack": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "Andrej Karpathy": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "DeepLearningAI": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "LlamaIndex": "https://github.githubassets.com/favicons/favicon.svg",
    "LangChain": "https://github.githubassets.com/favicons/favicon.svg",
    # MOOCs & Course Platforms
    "Coursera": "https://www.coursera.org/favicon.ico",
    "edX": "https://www.edx.org/favicon.ico",
    # Open Source & Developer Communities
    "freeCodeCamp": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "freeCodeCamp.org": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "Python Software Foundation": "https://docs.python.org/3/_static/py.svg",
    "FastAPI / Tiangolo": "https://fastapi.tiangolo.com/img/favicon.png",
    "pytest-dev": "https://docs.pytest.org/en/stable/_static/favicon.svg",
    "PostgreSQL Global Development Group": "https://www.postgresql.org/favicon.ico",
    "PGExercises": "https://pgexercises.com/favicon.ico",
    "Exercism.org": "https://exercism.org/favicon.ico",
    "Apache Software Foundation": "https://spark.apache.org/images/spark-logo-trademark.png",
    "Git SCM": "https://git-scm.com/favicon.ico",
    "GitHub": "https://github.githubassets.com/favicons/favicon.svg",
    "OpenTelemetry": "https://opentelemetry.io/favicons/favicon.ico",
    "Prometheus Authors": "https://prometheus.io/assets/favicons/favicon.ico",
    "Grafana Labs": "https://grafana.com/static/assets/img/favicons/favicon.ico",
    "OWASP Foundation": "https://owasp.org/assets/images/favicon.ico",
    "Fireship": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "Corey Schafer": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "ArjanCodes": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "Traversy Media": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
    "Programming with Mosh": "https://www.youtube.com/s/desktop/f2a4bc08/img/favicon_32x32.png",
}

FALLBACK_EMOJI_ICON = "🔖"


def get_provider_icon_url(provider: str, url: str | None = None) -> str | None:
    """Return canonical provider icon URL or fallback if not specifically mapped."""
    if not provider:
        return None

    # Check direct canonical mapping
    if provider in PROVIDER_ICON_MAP:
        return PROVIDER_ICON_MAP[provider]

    # Partial match for educator collaborations (e.g. 'freeCodeCamp.org / Krish Naik')
    for prov_key, icon_url in PROVIDER_ICON_MAP.items():
        if prov_key.lower() in provider.lower():
            return icon_url

    # Check if URL itself is YouTube or GitHub
    if url:
        if "youtube.com" in url or "youtu.be" in url:
            return PROVIDER_ICON_MAP["YouTube"]
        if "github.com" in url:
            return PROVIDER_ICON_MAP["GitHub"]
        if "google.com" in url or "cloudskillsboost.google" in url:
            return PROVIDER_ICON_MAP["Google Cloud"]

    return None


def new_tab_link_html(url: str, label: str, css_class: str = "", context: str = "") -> str:
    """Return an HTML link that opens in a new tab and says so to screen reader users.

    The visible label stays at the start of the accessible name (WCAG 2.5.3), a trailing
    "↗" is hidden from screen readers because it is decorative, and a visually hidden
    suffix names the resource and warns about the new tab (WCAG 2.4.4).
    """
    text = label.strip()
    arrow = ""
    if text.endswith("↗"):
        text = text.removesuffix("↗").strip()
        arrow = "<span aria-hidden='true'> ↗</span>"
    hidden = f": {context}" if context else ""
    class_attr = f" class='{css_class}'" if css_class else ""
    return (
        f"<a href='{escape(url, quote=True)}' target='_blank' rel='noopener noreferrer'"
        f"{class_attr}>{escape(text)}{arrow}"
        f"<span class='sr-only'>{escape(hidden)} (opens in a new tab)</span></a>"
    )


def live_region_html(message: str = "") -> str:
    """Return a visually hidden polite live region (WCAG 4.1.3 Status Messages).

    Screen readers announce changes to its text without moving focus. Keep the element
    rendered at a stable position and only change the message, otherwise nothing is read.
    """
    return (
        "<div class='sr-only live-region' role='status' aria-live='polite' aria-atomic='true'>"
        f"{escape(message)}</div>"
    )
