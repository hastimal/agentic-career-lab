# Feature Specification: Resume Studio (AI Resume Builder + Career Progress Tracker)

> **Status:** Planned Feature (Roadmap post-M7/M8 stabilization, targeted for pre-v1.0.0)  
> **Module Scope:** `agentic_career_lab.agents.resume_studio`  
> **Privacy Classification:** 100% Local Privacy Boundary (Local Gemma 4 on Ollama; no raw resume or personal telemetry sent to cloud)

---

## 1. Overview & Vision

**Resume Studio** closes the loop on student career development:
1. A student uploads an existing resume and matches against real job opportunities.
2. The system identifies missing skills and generates an evidence-grounded 2-to-4 week learning roadmap.
3. As the student completes coursework, builds portfolio applications, or implements projects, they return to the **Resume Studio**.
4. An interactive conversational assistant powered by local Gemma 4 queries the student about what they built and inspects supporting evidence (code, repo links, artifacts).
5. The system tracks skills through a formalized state lifecycle (`NOT_STARTED` -> `LEARNING` -> `COMPLETED` -> `DEMONSTRATED`).
6. Upon validating evidence, the assistant proposes precise bullet/section updates formatted as side-by-side diffs.
7. With explicit student approval, updates are applied to a versioned resume model, recalculating readiness scores and rendering clean, ATS-compliant DOCX and PDF deliverables.

---

## 2. Core Functional Requirements

### 2.1 State & Lifecycle Management
- **Skill Progression Model**: Track every tracked skill through explicit transitions:
  - `NOT_STARTED`: Identified in a target job posting but absent from the student's background.
  - `LEARNING`: In progress via courses, tutorials, or study plans.
  - `COMPLETED`: Theoretical or coursework completion reported by the user.
  - `DEMONSTRATED`: Backed by verifiable evidence (working repo, deployed project, verifiable artifact).
- **Evidence Separation**: Strict distinction between:
  - *Self-reported claims* (e.g., "I learned Kubernetes last weekend").
  - *Independently verified evidence* (e.g., GitHub repository commit history, deployment manifest, Dockerfile, or project demo).

### 2.2 Local Conversational Evidence Gathering
- Multi-turn conversation powered locally by **Gemma 4 on Ollama**.
- The assistant probes:
  - What specific problem was solved?
  - What tools/libraries were used and what was the student's individual contribution?
  - What evidence or repository confirms this implementation?
- **Anti-Hallucination Guardrail**: The system will *never* automatically inject an unverified skill, metric, certification, or employer claim into a resume profile without documented evidence and explicit user confirmation.

### 2.3 Proposed Changes & Visual Diff Review
- Propose before-and-after diffs for resume bullet points.
- Highlight:
  - Action verb enhancement.
  - Context and technologies integrated.
  - Verifiable outcomes and deliverables.
- Explicit `Approve`, `Edit`, or `Reject` controls for each suggested bullet.

### 2.4 Version Control & Rollback
- Immutable resume version snapshots (`v1`, `v2`, etc.).
- Full rollback capability to any previous version.
- Audit trail logging which evidence justified each update.

### 2.5 Clean ATS-Friendly Export
- Output clean, standard single-column, ATS-parseable:
  - Microsoft Word (`.docx`) utilizing semantic heading styles and standard fonts.
  - Vector PDF (`.pdf`) generated with proper structural tagging.

### 2.6 Dynamic Gap Recalculation
- Immediately update target job match matrices upon applying resume revisions.
- Recalculate demonstrated vs. missing skill tallies and update the student's career action plan.

---

## 3. Data Models

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SkillStatus(str, Enum):
    NOT_STARTED = "not_started"
    LEARNING = "learning"
    COMPLETED = "completed"
    DEMONSTRATED = "demonstrated"


class EvidenceType(str, Enum):
    SELF_REPORTED = "self_reported"
    GITHUB_REPO = "github_repo"
    CODE_SNIPPET = "code_snippet"
    DEPLOYMENT_URL = "deployment_url"
    COURSE_CERTIFICATE = "course_certificate"


class SkillEvidence(BaseModel):
    evidence_id: str
    skill_name: str
    evidence_type: EvidenceType
    description: str
    source_url: Optional[str] = None
    verification_notes: str = ""
    is_verified: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TrackedSkill(BaseModel):
    skill_name: str
    status: SkillStatus = SkillStatus.NOT_STARTED
    target_role: Optional[str] = None
    evidence: List[SkillEvidence] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ResumeBulletDiff(BaseModel):
    bullet_id: str
    section: str  # e.g., "Experience", "Projects"
    original_text: str
    proposed_text: str
    skills_demonstrated: List[str]
    supporting_evidence_ids: List[str]
    user_approved: bool = False


class ResumeVersion(BaseModel):
    version_number: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    structured_content: dict  # Full profile (education, experience, projects, skills)
    bullets_changed: List[ResumeBulletDiff] = Field(default_factory=list)
    change_summary: str = ""
```

---

## 4. Service & Agent Interfaces

```python
from abc import ABC, abstractmethod
from typing import List, Tuple


class ResumeStudioService(ABC):
    """Core local service interface for Resume Studio operations."""

    @abstractmethod
    def record_learning_progress(
        self, skill_name: str, new_status: SkillStatus, evidence: Optional[SkillEvidence] = None
    ) -> TrackedSkill:
        """Update skill progress with optional supporting evidence."""
        ...

    @abstractmethod
    def evaluate_evidence(
        self, student_statement: str, repo_url: Optional[str] = None
    ) -> Tuple[bool, str, List[str]]:
        """Run local Gemma 4 evaluation to verify if evidence supports target skills."""
        ...

    @abstractmethod
    def generate_proposed_diffs(
        self, current_version: ResumeVersion, newly_demonstrated_skills: List[str]
    ) -> List[ResumeBulletDiff]:
        """Propose grounded bullet improvements based strictly on verified evidence."""
        ...

    @abstractmethod
    def apply_approved_changes(
        self, current_version: ResumeVersion, approved_diffs: List[ResumeBulletDiff]
    ) -> ResumeVersion:
        """Create a new immutable resume version snapshot from approved diffs."""
        ...

    @abstractmethod
    def export_ats_document(
        self,
        version: ResumeVersion,
        format: str,  # "docx" | "pdf"
    ) -> bytes:
        """Export clean ATS-friendly document bytes."""
        ...
```

---

## 5. Privacy Boundary & Threat Model

1. **Local Isolation**: All resume text, bullet diffs, student chat transcripts, and evidence snippets are processed strictly by the local Gemma 4 runtime via Ollama (`http://localhost:11434` or `http://host.docker.internal:11434`).
2. **No Cloud Leakage**: Neither raw resume drafts nor GitHub code snippets are sent to Gemini or Vertex AI.
3. **Optional Cloud Consent**: If the student desires a high-level industry learning roadmap for a newly added skill, only sanitized skill names (e.g. `["Kubernetes", "FastAPI"]`) may be shared with Cloud Gemini upon explicit user consent.
4. **Local Version Storage**: All version history is stored in local JSON/SQLite files on the student's machine.

---

## 6. Acceptance Criteria

- [ ] **AC-1 (State Transitions)**: Skills cleanly advance from `NOT_STARTED` -> `LEARNING` -> `COMPLETED` -> `DEMONSTRATED`, blocking `DEMONSTRATED` unless verified evidence is attached.
- [ ] **AC-2 (Evidence Separation)**: Self-reported claims are explicitly tagged and cannot trigger `DEMONSTRATED` status without artifact verification.
- [ ] **AC-3 (Anti-Hallucination)**: Gemma 4 bullet suggestions only utilize skills and project outcomes directly present in approved evidence.
- [ ] **AC-4 (Diff & Approval)**: UI presents side-by-side readable diffs. No change is committed without student approval.
- [ ] **AC-5 (ATS Export)**: Generated DOCX and PDF parse accurately in standard ATS parsers without header/footer table traps or unrecognized glyphs.
- [ ] **AC-6 (Version History)**: Users can view previous resume versions and revert to any prior state.
- [ ] **AC-7 (Readiness Recalculation)**: Updating the resume automatically triggers a Job Scout requirement re-check, reflecting updated demonstrated/missing metrics.
- [ ] **AC-8 (Automated Test Suite)**: Unit and integration tests covering:
  - Skill status state machines.
  - Evidence validation rules.
  - Diff calculation and application.
  - Resume parser roundtrip fidelity.
  - Strict absence of PII or resume text in cloud transmission logs.
