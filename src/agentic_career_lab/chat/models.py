"""Chat domain models and schema definitions for AI Career Agent."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ChatRole(StrEnum):
    """Role classification for chat messages."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class ChatIntent(StrEnum):
    """Categorized conversational intents supported by the AI Career Agent."""

    FIND_JOBS = "FIND_JOBS"
    EXPLAIN_SKILL_GAPS = "EXPLAIN_SKILL_GAPS"
    RECOMMEND_RESOURCES = "RECOMMEND_RESOURCES"
    EXPLAIN_LEARNING_PLAN = "EXPLAIN_LEARNING_PLAN"
    NEXT_LEARNING_ACTION = "NEXT_LEARNING_ACTION"
    SUMMARIZE_CAREER_STATUS = "SUMMARIZE_CAREER_STATUS"
    RESUME_GUIDANCE = "RESUME_GUIDANCE"
    GENERAL_CAREER_QUESTION = "GENERAL_CAREER_QUESTION"


class ChatActionType(StrEnum):
    """Supported interactive application actions that can be triggered from chat."""

    OPEN_SKILL_GAP_ANALYSIS = "OPEN_SKILL_GAP_ANALYSIS"
    NAVIGATE_JOB_EXPLORER = "NAVIGATE_JOB_EXPLORER"
    NAVIGATE_MY_RESUME = "NAVIGATE_MY_RESUME"
    NAVIGATE_LEARNING_PLAN = "NAVIGATE_LEARNING_PLAN"
    SELECT_JOB = "SELECT_JOB"
    OPEN_LEARNING_RESOURCE = "OPEN_LEARNING_RESOURCE"
    CONTINUE_LEARNING = "CONTINUE_LEARNING"
    VIEW_CAREER_REPORT = "VIEW_CAREER_REPORT"


class ChatAction(BaseModel):
    """Structured, typed application action presented to students in chat."""

    action_id: str = Field(
        default_factory=lambda: f"act_{uuid.uuid4().hex[:8]}",
        description="Unique identifier for the action",
    )
    action_type: ChatActionType = Field(
        ...,
        description="Supported action category",
    )
    label: str = Field(
        ...,
        description="User-facing button label",
    )
    enabled: bool = Field(
        default=True,
        description="Whether action can be executed in current context",
    )
    disabled_reason: str | None = Field(
        default=None,
        description="Explanation when action is disabled",
    )
    target_page: str = Field(
        ...,
        description="Canonical target page destination",
    )
    selected_opportunity_id: str | None = Field(
        default=None,
        description="Opportunity ID associated with action execution",
    )
    opportunity_id: str | None = Field(
        default=None,
        description="Target opportunity ID for SELECT_JOB actions",
    )
    resource_id: str | None = Field(
        default=None,
        description="Target canonical ResourceCatalog resource ID",
    )
    learning_week: int | None = Field(
        default=None,
        description="Target week number for CONTINUE_LEARNING actions",
    )
    learning_task_id: str | None = Field(
        default=None,
        description="Target activity ID for CONTINUE_LEARNING actions",
    )
    required_context: list[str] = Field(
        default_factory=list,
        description="Prerequisite context keys required for execution",
    )


class ExecutionRuntime(StrEnum):
    """Runtime execution environment for conversational responses and tools."""

    LOCAL_GEMMA = "LOCAL_GEMMA"
    DETERMINISTIC_PYTHON = "DETERMINISTIC_PYTHON"
    GOOGLE_ADK = "GOOGLE_ADK"
    CLOUD_GEMINI = "CLOUD_GEMINI"


class ConsentDecision(BaseModel):
    """Explicit privacy consent decision for cloud AI synthesis."""

    consent_given: bool = Field(
        default=False,
        description="Whether student has explicitly opted into cloud AI reasoning",
    )
    granted_at: datetime | None = Field(
        default=None,
        description="Timestamp when consent was granted, if applicable",
    )
    scope: list[str] = Field(
        default_factory=lambda: ["sanitized_skill_gaps", "target_role"],
        description="Explicit allowlisted fields permitted for cloud synthesis",
    )


class ChatToolRequest(BaseModel):
    """Structured request to execute an internal career tool."""

    tool_call_id: str = Field(
        default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}",
        description="Unique identifier for this tool call",
    )
    tool_name: str = Field(..., description="Canonical name of the tool to invoke")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters passed to the tool",
    )
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when tool was requested",
    )


class ChatToolResult(BaseModel):
    """Structured result returned from tool execution with strict provenance."""

    tool_call_id: str = Field(..., description="Matching tool call identifier")
    tool_name: str = Field(..., description="Canonical name of executed tool")
    success: bool = Field(default=True, description="Whether tool executed successfully")
    provenance: str = Field(
        ...,
        description="System or agent component that produced this result (e.g. 'JobScoutAgent', 'ResourceCatalog')",
    )
    runtime: ExecutionRuntime = Field(
        default=ExecutionRuntime.DETERMINISTIC_PYTHON,
        description="Runtime environment that executed the tool",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured tool output data (sanitized, zero raw resume text)",
    )
    error: str | None = Field(
        default=None,
        description="Error description if execution failed",
    )
    executed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when tool finished execution",
    )


class ChatMessage(BaseModel):
    """Individual conversational message within a chat session."""

    message_id: str = Field(
        default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}",
        description="Unique message identifier",
    )
    role: ChatRole = Field(..., description="Role of message author")
    content: str = Field(..., description="Text content of the message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of message creation",
    )
    intent: ChatIntent | None = Field(
        default=None,
        description="Detected intent if message is from user or analyzed by agent",
    )
    runtime: ExecutionRuntime = Field(
        default=ExecutionRuntime.LOCAL_GEMMA,
        description="Runtime that produced this message",
    )
    tool_calls: list[ChatToolRequest] = Field(
        default_factory=list,
        description="Tool calls requested during message generation",
    )
    tool_results: list[ChatToolResult] = Field(
        default_factory=list,
        description="Tool execution results associated with this turn",
    )
    actions: list[ChatAction] = Field(
        default_factory=list,
        description="Structured interactive actions available to the user for this turn",
    )
    referenced_context_ids: dict[str, str] = Field(
        default_factory=dict,
        description="References to active context (e.g. {'opportunity_id': '...'}), zero raw resume data",
    )


class ChatContext(BaseModel):
    """Non-PII context references passed into the conversational orchestrator."""

    student_id: str = Field(default="student-demo", description="Unique student ID")
    target_role: str | None = Field(default=None, description="Current target career track")
    selected_opportunity_id: str | None = Field(default=None, description="Active opportunity ID")
    selected_opportunity_title: str | None = Field(
        default=None, description="Role title and company for active opportunity"
    )
    resume_analyzed: bool = Field(
        default=False, description="Whether resume has been analyzed locally"
    )
    demonstrated_skills: list[str] = Field(
        default_factory=list, description="Verified demonstrated skills"
    )
    partial_skills: list[str] = Field(
        default_factory=list, description="Mentioned or coursework-only skills"
    )
    missing_skills: list[str] = Field(
        default_factory=list, description="Missing job requirement skills"
    )
    plan_generated: bool = Field(default=False, description="Whether weekly learning plan exists")
    plan_duration_weeks: int | None = Field(
        default=None, description="Roadmap duration (2 or 4 weeks)"
    )
    active_week: int = Field(default=1, description="Active or next roadmap week")
    consent: ConsentDecision = Field(
        default_factory=ConsentDecision, description="Cloud AI consent status"
    )


class ChatResponse(BaseModel):
    """Final unified response returned by the chat orchestrator."""

    message: ChatMessage = Field(..., description="Assistant response message")
    intent: ChatIntent = Field(..., description="Primary resolved intent")
    runtime: ExecutionRuntime = Field(
        default=ExecutionRuntime.LOCAL_GEMMA,
        description="Primary execution runtime used",
    )
    tool_results: list[ChatToolResult] = Field(
        default_factory=list,
        description="Structured tool results backing this response",
    )
    missing_context: list[str] = Field(
        default_factory=list,
        description="Prerequisite context items missing to answer completely",
    )
    actions: list[ChatAction] = Field(
        default_factory=list,
        description="Structured interactive actions available on this response",
    )


class ChatSession(BaseModel):
    """Session-scoped container for conversation history."""

    session_id: str = Field(
        default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}",
        description="Unique session identifier",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when session was initialized",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of last interaction",
    )
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="Ordered sequence of conversation messages",
    )
    associated_opportunity_id: str | None = Field(
        default=None,
        description="Opportunity ID when this conversation was conducted; changes invalidate stale reasoning",
    )
    max_history_turns: int = Field(
        default=20,
        description="Maximum turns retained in memory before older context is truncated",
    )

    def add_message(self, message: ChatMessage) -> None:
        """Add message and enforce bounded conversation history."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
        if len(self.messages) > self.max_history_turns:
            self.messages = self.messages[-self.max_history_turns :]

    def clear(self) -> None:
        """Reset conversation messages while preserving session ID and metadata."""
        self.messages.clear()
        self.updated_at = datetime.now(UTC)
