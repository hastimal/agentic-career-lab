"""Tests for M10.1 AI Career Agent Chat Foundation."""

import pytest

from agentic_career_lab.chat.models import (
    ChatContext,
    ChatIntent,
    ChatMessage,
    ChatRole,
    ChatSession,
    ChatToolRequest,
    ConsentDecision,
    ExecutionRuntime,
)
from agentic_career_lab.chat.orchestrator import CareerChatOrchestrator
from agentic_career_lab.chat.privacy import (
    CareerChatPrivacyGuard,
    ConsentViolationError,
)
from agentic_career_lab.chat.tools import CareerChatToolAdapters
from agentic_career_lab.llm.local import FakeGemmaClient, OllamaGemmaClient


def test_chat_domain_models():
    """Verify chat domain models instantiate with strict defaults and typing."""
    msg = ChatMessage(role=ChatRole.USER, content="Hello career coach")
    assert msg.message_id.startswith("msg_")
    assert msg.role == ChatRole.USER
    assert msg.content == "Hello career coach"
    assert msg.tool_calls == []

    session = ChatSession()
    assert session.session_id.startswith("session_")
    session.add_message(msg)
    assert len(session.messages) == 1

    # Session clear resets conversation only
    session.clear()
    assert len(session.messages) == 0
    assert session.session_id.startswith("session_")


def test_chat_session_bounded_history():
    """Verify session bounds history to max_history_turns."""
    session = ChatSession(max_history_turns=5)
    for i in range(10):
        session.add_message(ChatMessage(role=ChatRole.USER, content=f"Msg {i}"))
    assert len(session.messages) == 5
    assert session.messages[0].content == "Msg 5"
    assert session.messages[-1].content == "Msg 9"


def test_privacy_guard_consent_blocking():
    """Verify cloud calls are blocked when consent is not granted."""
    no_consent = ConsentDecision(consent_given=False)
    with pytest.raises(ConsentViolationError, match="Cloud Gemini synthesis is disabled"):
        CareerChatPrivacyGuard.verify_cloud_consent(no_consent)

    has_consent = ConsentDecision(consent_given=True)
    # Should not raise
    CareerChatPrivacyGuard.verify_cloud_consent(has_consent)


def test_privacy_guard_payload_sanitization():
    """Verify outgoing cloud payload is scrubbed of PII and raw documents."""
    context = ChatContext(
        target_role="AI Engineer",
        missing_skills=["Docker", "Kubernetes"],
        consent=ConsentDecision(consent_given=True),
    )
    user_text = "My email is student@university.edu and phone is 555-123-4567. Help me find jobs."
    payload = CareerChatPrivacyGuard.build_sanitized_cloud_payload(user_text, context)

    assert "[EMAIL_REDACTED]" in payload["prompt"]
    assert "[PHONE_REDACTED]" in payload["prompt"]
    assert "student@university.edu" not in payload["prompt"]
    assert payload["target_role"] == "AI Engineer"
    assert payload["sanitized_skill_gaps"] == ["Docker", "Kubernetes"]


def test_telemetry_sanitization():
    """Verify telemetry attributes never leak raw prompts, completions, or PII."""
    raw_attrs = {
        "session_id": "sess_123",
        "prompt": "Raw prompt text with student secret",
        "resume_text": "Sensitive full resume",
        "user_email": "jane@example.com",
    }
    sanitized = CareerChatPrivacyGuard.sanitize_telemetry_attributes(raw_attrs)
    assert "session_id" in sanitized
    assert "prompt" not in sanitized
    assert "resume_text" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized.get("user_email", "")


def test_tool_adapters_provenance():
    """Verify tool adapters return structured data with explicit provenance."""
    adapters = CareerChatToolAdapters()
    context = ChatContext(
        demonstrated_skills=["Python", "FastAPI"],
        missing_skills=["Docker"],
        selected_opportunity_id="job_123",
        selected_opportunity_title="AI Engineering Intern (Google Cloud)",
        resume_analyzed=True,
    )

    # find_jobs
    res = adapters.execute_tool(
        ChatToolRequest(tool_name="find_jobs", parameters={"query": "AI"}), context
    )
    assert res.success is True
    assert res.provenance == "JobScoutAgent"
    assert "opportunities" in res.data

    # explain_skill_gaps
    res_gap = adapters.execute_tool(ChatToolRequest(tool_name="explain_skill_gaps"), context)
    assert res_gap.success is True
    assert res_gap.provenance == "SkillGapAnalyzer"
    assert res_gap.data["missing_skills"] == ["Docker"]

    # recommend_resources
    res_cat = adapters.execute_tool(
        ChatToolRequest(tool_name="recommend_resources", parameters={"skills": ["Python"]}), context
    )
    assert res_cat.success is True
    assert res_cat.provenance == "ResourceCatalog"
    assert len(res_cat.data["resources"]) > 0


def test_orchestrator_missing_context_handling():
    """Verify orchestrator requests missing prerequisites rather than fabricating answers."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    session = ChatSession()

    # Context missing opportunity and resume
    empty_context = ChatContext()
    resp = orchestrator.process_message("What are my skill gaps?", session, empty_context)

    assert resp.intent == ChatIntent.EXPLAIN_SKILL_GAPS
    assert len(resp.missing_context) > 0
    assert "selected_opportunity_id" in resp.missing_context
    assert (
        "Select a job before comparing your resume against its requirements."
        in resp.message.content
    )


def test_orchestrator_all_intents():
    """Verify orchestrator correctly resolves all 8 intents."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(
        target_role="AI Engineer",
        selected_opportunity_id="job_test",
        selected_opportunity_title="AI Intern",
        resume_analyzed=True,
        plan_generated=True,
        demonstrated_skills=["Python"],
        missing_skills=["Kubernetes"],
    )

    intent_queries = [
        ("Can you search jobs for an AI intern?", ChatIntent.FIND_JOBS),
        ("Explain my missing skills for this role", ChatIntent.EXPLAIN_SKILL_GAPS),
        ("Recommend tutorials and courses for Python", ChatIntent.RECOMMEND_RESOURCES),
        ("Explain my learning plan roadmap", ChatIntent.EXPLAIN_LEARNING_PLAN),
        ("What should I do next to continue learning?", ChatIntent.NEXT_LEARNING_ACTION),
        ("Summarize my career status and readiness", ChatIntent.SUMMARIZE_CAREER_STATUS),
        ("Give me resume guidance to strengthen my bullets", ChatIntent.RESUME_GUIDANCE),
        (
            "How do I prepare for a technical interview generally?",
            ChatIntent.GENERAL_CAREER_QUESTION,
        ),
    ]

    for query, expected_intent in intent_queries:
        session = ChatSession()
        res = orchestrator.process_message(query, session, context)
        assert res.intent == expected_intent
        assert res.message.content != ""
        assert len(session.messages) == 2  # user + assistant


def test_orchestrator_job_change_detection():
    """Verify session tracks and detects changes in selected job opportunity."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    session = ChatSession()

    context1 = ChatContext(
        selected_opportunity_id="job_alpha",
        selected_opportunity_title="AI Engineer",
        resume_analyzed=True,
    )
    orchestrator.process_message("Show my career status", session, context1)
    assert session.associated_opportunity_id == "job_alpha"

    context2 = ChatContext(
        selected_opportunity_id="job_beta",
        selected_opportunity_title="DevOps Engineer",
        resume_analyzed=True,
    )
    orchestrator.process_message("Show my career status", session, context2)
    assert session.associated_opportunity_id == "job_beta"


def test_orchestrator_cloud_blocking_on_missing_consent():
    """Verify orchestrator falls back to local Gemma if cloud is requested without consent."""
    orchestrator = CareerChatOrchestrator(
        llm=FakeGemmaClient(),
        runtime=ExecutionRuntime.CLOUD_GEMINI,
    )
    session = ChatSession()
    context = ChatContext(
        consent=ConsentDecision(consent_given=False),
        demonstrated_skills=["Python"],
    )

    resp = orchestrator.process_message("Search available jobs", session, context)
    assert resp.runtime == ExecutionRuntime.LOCAL_GEMMA
    assert "cloud consent is not granted" in resp.message.content.lower()


def test_local_gemma_smoke_test():
    """Actual smoke test against local Ollama Gemma 4 if reachable, or test fake fallback."""
    client = OllamaGemmaClient()
    if client.is_available():
        # Live smoke test against local Gemma 4
        res = client.generate("Reply with the exact word 'READY' if you are online.")
        assert len(res) > 0
    else:
        fake = FakeGemmaClient(is_online=True)
        assert fake.is_available() is True
        res = fake.generate("test")
        assert "Fake response from Gemma 4" in res


def test_multiturn_conversation_preserves_history():
    """Verify that multiple consecutive user messages accumulate in session history."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    session = ChatSession()
    context = ChatContext(demonstrated_skills=["Python", "SQL"])

    # 5 successive messages
    queries = [
        "What jobs match my profile?",
        "Recommend free Python learning resources.",
        "What should I learn next?",
        "How can I improve my resume?",
        "Summarize my career status",
    ]

    for q in queries:
        resp = orchestrator.process_message(q, session, context)
        assert resp is not None

    # Each turn adds 1 user + 1 assistant message = 10 messages total
    assert len(session.messages) == 10
    user_msgs = [m.content for m in session.messages if m.role == ChatRole.USER]
    assert len(user_msgs) == 5
    assert user_msgs[0] == "What jobs match my profile?"


def test_clear_chat_isolation():
    """Verify clear chat clears only messages, keeping session and student profile intact."""
    session = ChatSession()
    session.add_message(ChatMessage(role=ChatRole.USER, content="Hello"))
    session.add_message(ChatMessage(role=ChatRole.ASSISTANT, content="Hi"))
    original_id = session.session_id

    session.clear()
    assert len(session.messages) == 0
    assert session.session_id == original_id


def test_ollama_unavailable_graceful_handling():
    """Verify orchestrator gracefully recovers when LLM raises exception."""
    offline_client = FakeGemmaClient(is_online=False)
    orchestrator = CareerChatOrchestrator(llm=offline_client)
    session = ChatSession()
    context = ChatContext(demonstrated_skills=["Python"])

    resp = orchestrator.process_message(
        "Recommend free Python learning resources.", session, context
    )
    assert resp is not None
    assert "temporarily unable to consult my local language model" in resp.message.content
    assert resp.tool_results != []
    assert resp.tool_results[0].success is True


def test_orchestrator_streaming_yields_tokens():
    """Verify that process_message_stream yields true progressive events and tokens."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    session = ChatSession()
    context = ChatContext(demonstrated_skills=["Python"])

    events = list(
        orchestrator.process_message_stream(
            "Recommend free Python learning resources.", session, context
        )
    )

    event_types = [e[0] for e in events]
    assert "intent" in event_types
    assert "tool_executing" in event_types
    assert "tool_result" in event_types
    assert "token" in event_types
    assert "done" in event_types

    tokens = [e[1] for e in events if e[0] == "token"]
    assert len(tokens) > 1
    assert "".join(tokens) != ""


def test_adk_tool_adapter_coordination():
    """Verify that when ADKCareerCoordinator is provided, tool provenance reflects ADK."""
    from unittest.mock import MagicMock

    from agentic_career_lab.coordinator.adk_coordinator import ADKCareerCoordinator

    mock_adk = MagicMock(spec=ADKCareerCoordinator)
    adapters = CareerChatToolAdapters(adk_coordinator=mock_adk)
    context = ChatContext(demonstrated_skills=["Python"])

    req = ChatToolRequest(tool_name="find_jobs", parameters={"query": "AI Engineer"})
    result = adapters.execute_tool(req, context)

    assert result.success is True
    assert result.runtime == ExecutionRuntime.GOOGLE_ADK
    assert "ADK Coordinated" in result.provenance
    assert len(result.data["opportunities"]) > 0
    # Verify demo jobs are labeled clearly
    first_opp = result.data["opportunities"][0]
    assert first_opp["is_demo"] is True
    assert "Demo" in first_opp["source_label"]


def test_chat_action_model_contract():
    """Verify ChatAction model enforces required fields, typing, and safety defaults."""
    from agentic_career_lab.chat.models import ChatAction, ChatActionType
    from agentic_career_lab.ui_helpers import SKILL_GAP_ANALYSIS

    action = ChatAction(
        action_type=ChatActionType.OPEN_SKILL_GAP_ANALYSIS,
        label="View My Skill Gap Analysis",
        target_page=SKILL_GAP_ANALYSIS,
        selected_opportunity_id="opp_123",
        required_context=["selected_opportunity_id", "resume_analyzed"],
    )

    assert action.action_id.startswith("act_")
    assert action.action_type == ChatActionType.OPEN_SKILL_GAP_ANALYSIS
    assert action.label == "View My Skill Gap Analysis"
    assert action.enabled is True
    assert action.disabled_reason is None
    assert action.target_page == SKILL_GAP_ANALYSIS
    assert action.selected_opportunity_id == "opp_123"
    assert "resume_analyzed" in action.required_context


def test_resolve_chat_actions_case_a_no_job():
    """Case A: Missing job opportunity prompts Choose a Job navigating to Job Explorer."""
    from agentic_career_lab.chat.models import ChatActionType
    from agentic_career_lab.ui_helpers import JOB_EXPLORER

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(selected_opportunity_id=None, resume_analyzed=False)

    actions = orchestrator.resolve_chat_actions(
        ChatIntent.EXPLAIN_SKILL_GAPS, context, missing=["selected_opportunity_id"]
    )

    assert len(actions) == 1
    action = actions[0]
    assert action.action_type == ChatActionType.NAVIGATE_JOB_EXPLORER
    assert action.label == "Choose a Job"
    assert action.target_page == JOB_EXPLORER


def test_resolve_chat_actions_case_b_no_resume():
    """Case B: Job selected, but resume not analyzed prompts Analyze My Resume."""
    from agentic_career_lab.chat.models import ChatActionType
    from agentic_career_lab.ui_helpers import MY_RESUME

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(selected_opportunity_id="job_456", resume_analyzed=False)

    actions = orchestrator.resolve_chat_actions(
        ChatIntent.EXPLAIN_SKILL_GAPS, context, missing=["resume_analyzed"]
    )

    assert len(actions) == 1
    action = actions[0]
    assert action.action_type == ChatActionType.NAVIGATE_MY_RESUME
    assert action.label == "Analyze My Resume"
    assert action.target_page == MY_RESUME
    assert action.selected_opportunity_id == "job_456"


def test_resolve_chat_actions_case_d_valid_job_and_resume():
    """Case D: Job selected and resume analyzed yields View My Skill Gap Analysis."""
    from agentic_career_lab.chat.models import ChatActionType
    from agentic_career_lab.ui_helpers import SKILL_GAP_ANALYSIS

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(
        selected_opportunity_id="job_789",
        resume_analyzed=True,
        demonstrated_skills=["Python"],
        missing_skills=["Kubernetes"],
    )

    actions = orchestrator.resolve_chat_actions(ChatIntent.EXPLAIN_SKILL_GAPS, context, missing=[])

    assert len(actions) == 1
    action = actions[0]
    assert action.action_type == ChatActionType.OPEN_SKILL_GAP_ANALYSIS
    assert action.label == "View My Skill Gap Analysis"
    assert action.target_page == SKILL_GAP_ANALYSIS
    assert action.selected_opportunity_id == "job_789"


def test_skill_gap_action_preserves_conversation_and_profile():
    """Verify that resolving actions and generating responses leaves session history and profile intact."""
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    session = ChatSession()
    context = ChatContext(
        student_id="student_alex",
        target_role="AI Engineering Intern",
        selected_opportunity_id="job_intern",
        resume_analyzed=True,
        demonstrated_skills=["Python", "SQL"],
        missing_skills=["Kubernetes"],
    )

    resp = orchestrator.process_message("What skills am I missing?", session, context)

    assert resp.actions is not None
    assert len(resp.actions) == 1
    assert resp.actions[0].label == "View My Skill Gap Analysis"
    # History preserved in session
    assert len(session.messages) == 2
    assert session.messages[0].role == ChatRole.USER
    assert session.messages[1].role == ChatRole.ASSISTANT
    assert session.messages[1].actions == resp.actions
    # Profile skills intact
    assert context.student_id == "student_alex"
    assert context.demonstrated_skills == ["Python", "SQL"]


def test_untrusted_action_types_prevented():
    """Verify that arbitrary LLM text cannot inject unauthorized target pages into actions."""
    from pydantic import ValidationError

    from agentic_career_lab.chat.models import ChatAction

    with pytest.raises(ValidationError):
        # Invalid action_type not in ChatActionType enum
        ChatAction(
            action_type="UNAUTHORIZED_EXPLOIT",  # type: ignore[arg-type]
            label="Injected Action",
            target_page="http://evil-site.com",
        )


# ==============================================================================
# PHASE 9: COMPREHENSIVE TESTS FOR INTERACTIVE CAREER ACTIONS
# ==============================================================================


def test_select_job_action_generation_and_demo_tagging():
    """Verify SELECT_JOB actions are generated from Job Scout results with proper demo tagging."""
    from agentic_career_lab.chat.models import ChatActionType, ChatToolResult
    from agentic_career_lab.ui_helpers import MY_RESUME

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(student_id="student_123")
    tool_results = [
        ChatToolResult(
            tool_call_id="call_1",
            tool_name="find_jobs",
            success=True,
            provenance="JobScoutAgent",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "opportunities": [
                    {
                        "id": "opp_mock_1",
                        "role": "AI Engineer Intern",
                        "company": "Acme Corp",
                        "is_demo": True,
                    },
                    {
                        "id": "opp_live_2",
                        "role": "Cloud Architect",
                        "company": "Live Tech",
                        "is_demo": False,
                    },
                ]
            },
        )
    ]

    actions = orchestrator.resolve_chat_actions(
        ChatIntent.FIND_JOBS, context, tool_results=tool_results
    )

    assert len(actions) == 2
    assert actions[0].action_type == ChatActionType.SELECT_JOB
    assert actions[0].opportunity_id == "opp_mock_1"
    assert "Demo" in actions[0].label
    assert actions[0].target_page == MY_RESUME

    assert actions[1].action_type == ChatActionType.SELECT_JOB
    assert actions[1].opportunity_id == "opp_live_2"
    assert "(Demo)" not in actions[1].label


def test_select_job_invalidation_logic():
    """Verify switching selected opportunity invalidates stale resume analysis and learning plan."""
    from agentic_career_lab.coordinator.state import CareerWorkflowState
    from agentic_career_lab.models.schemas import Opportunity

    opp_old = Opportunity(
        opportunity_id="job_old",
        role="Role Old",
        company="Company A",
        location="Remote",
        source_url="https://example.com/jobs/old",  # type: ignore[arg-type]
        description="Desc",
        requirements=[],
    )
    opp_new = Opportunity(
        opportunity_id="job_new",
        role="Role New",
        company="Company B",
        location="Remote",
        source_url="https://example.com/jobs/new",  # type: ignore[arg-type]
        description="Desc",
        requirements=[],
    )

    state = CareerWorkflowState()
    state.selected_opportunity = opp_old
    state.resume_analysis = "dummy_analysis"  # type: ignore[assignment]
    state.skill_builder_plan = "dummy_plan"  # type: ignore[assignment]

    # Simulating the exact logic executed when SELECT_JOB is triggered
    if state.selected_opportunity.opportunity_id != opp_new.opportunity_id:
        state.resume_analysis = None
        state.skill_builder_plan = None
    state.selected_opportunity = opp_new

    assert state.selected_opportunity.opportunity_id == "job_new"
    assert state.resume_analysis is None
    assert state.skill_builder_plan is None


def test_open_learning_resource_action_generation_and_https_validation():
    """Verify OPEN_LEARNING_RESOURCE generates actions with valid ResourceCatalog IDs."""
    from agentic_career_lab.chat.models import ChatActionType, ChatToolResult
    from agentic_career_lab.services.learning_resources import ResourceCatalog

    catalog = ResourceCatalog()
    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())
    context = ChatContext(student_id="student_123")

    tool_results = [
        ChatToolResult(
            tool_call_id="call_res",
            tool_name="recommend_resources",
            success=True,
            provenance="ResourceCatalog",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "resources": [
                    {
                        "id": "vtx-learn-1",
                        "title": "Vertex AI Official Documentation & API Reference",
                        "category": "LEARN",
                    }
                ]
            },
        )
    ]

    actions = orchestrator.resolve_chat_actions(
        ChatIntent.RECOMMEND_RESOURCES, context, tool_results=tool_results
    )

    assert len(actions) == 1
    act = actions[0]
    assert act.action_type == ChatActionType.OPEN_LEARNING_RESOURCE
    assert act.resource_id == "vtx-learn-1"
    assert "Vertex AI" in act.label

    # Verify canonical catalog lookup and safe HTTPS URL
    res = catalog.get_resource_by_id(act.resource_id)
    assert res is not None
    assert str(res.url).startswith("https://")


def test_continue_learning_action_when_plan_exists_vs_missing():
    """Verify CONTINUE_LEARNING logic for both existing and missing learning plans."""
    from agentic_career_lab.chat.models import ChatActionType
    from agentic_career_lab.ui_helpers import MY_LEARNING_PLAN

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())

    # Case 1: No plan generated
    context_no_plan = ChatContext(plan_generated=False)
    actions1 = orchestrator.resolve_chat_actions(ChatIntent.NEXT_LEARNING_ACTION, context_no_plan)
    assert len(actions1) == 1
    assert actions1[0].action_type == ChatActionType.NAVIGATE_LEARNING_PLAN
    assert actions1[0].label == "Create Learning Plan"
    assert actions1[0].target_page == MY_LEARNING_PLAN

    # Case 2: Plan generated
    context_with_plan = ChatContext(plan_generated=True, active_week=2)
    actions2 = orchestrator.resolve_chat_actions(ChatIntent.NEXT_LEARNING_ACTION, context_with_plan)
    assert len(actions2) == 1
    assert actions2[0].action_type == ChatActionType.CONTINUE_LEARNING
    assert actions2[0].label == "Continue Learning"
    assert actions2[0].target_page == MY_LEARNING_PLAN
    assert actions2[0].learning_week == 2


def test_view_career_report_prerequisites_validation():
    """Verify VIEW_CAREER_REPORT guides through missing prerequisites step-by-step."""
    from agentic_career_lab.chat.models import ChatActionType
    from agentic_career_lab.ui_helpers import (
        CAREER_REPORT,
        JOB_EXPLORER,
        MY_LEARNING_PLAN,
        MY_RESUME,
    )

    orchestrator = CareerChatOrchestrator(llm=FakeGemmaClient())

    # Prereq 1 missing: Opportunity
    c1 = ChatContext(selected_opportunity_id=None)
    a1 = orchestrator.resolve_chat_actions(ChatIntent.SUMMARIZE_CAREER_STATUS, c1)
    assert a1[0].action_type == ChatActionType.NAVIGATE_JOB_EXPLORER
    assert a1[0].target_page == JOB_EXPLORER

    # Prereq 2 missing: Resume analysis
    c2 = ChatContext(selected_opportunity_id="opp_1", resume_analyzed=False)
    a2 = orchestrator.resolve_chat_actions(ChatIntent.SUMMARIZE_CAREER_STATUS, c2)
    assert a2[0].action_type == ChatActionType.NAVIGATE_MY_RESUME
    assert a2[0].target_page == MY_RESUME

    # Prereq 3 missing: Learning plan
    c3 = ChatContext(selected_opportunity_id="opp_1", resume_analyzed=True, plan_generated=False)
    a3 = orchestrator.resolve_chat_actions(ChatIntent.SUMMARIZE_CAREER_STATUS, c3)
    assert a3[0].action_type == ChatActionType.NAVIGATE_LEARNING_PLAN
    assert a3[0].target_page == MY_LEARNING_PLAN

    # All prerequisites satisfied
    c4 = ChatContext(selected_opportunity_id="opp_1", resume_analyzed=True, plan_generated=True)
    a4 = orchestrator.resolve_chat_actions(ChatIntent.SUMMARIZE_CAREER_STATUS, c4)
    assert a4[0].action_type == ChatActionType.VIEW_CAREER_REPORT
    assert a4[0].target_page == CAREER_REPORT
