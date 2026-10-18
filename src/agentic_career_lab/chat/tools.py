"""Reusable tool adapters connecting chat orchestration to existing agents and services."""

from typing import Any

from google.adk import Agent

from agentic_career_lab.agents.job_scout.agent import JobScoutAgent
from agentic_career_lab.chat.models import (
    ChatContext,
    ChatToolRequest,
    ChatToolResult,
    ExecutionRuntime,
)
from agentic_career_lab.coordinator.adk_coordinator import ADKCareerCoordinator
from agentic_career_lab.models import OpportunitySearchQuery, StudentProfile
from agentic_career_lab.providers.mock import MockOpportunityProvider
from agentic_career_lab.services.learning_resources import ResourceCatalog


class CareerChatToolAdapters:
    """Provides grounded, typed tool adapters wrapping existing services and agents."""

    def __init__(
        self,
        job_scout: JobScoutAgent | None = None,
        resource_catalog: ResourceCatalog | None = None,
        adk_coordinator: ADKCareerCoordinator | None = None,
    ) -> None:
        self.job_scout = job_scout or JobScoutAgent(MockOpportunityProvider())
        self.resource_catalog = resource_catalog or ResourceCatalog()
        self.adk_coordinator = adk_coordinator

        # Register Google ADK Chat Tools
        self.adk_job_scout_tool = Agent(
            name="chat_job_scout",
            tools=[self.find_jobs],
            instruction="Execute opportunity search deterministically for conversational requests.",
        )
        self.adk_catalog_tool = Agent(
            name="chat_resource_catalog",
            tools=[self.recommend_resources],
            instruction="Retrieve canonical learning resources from verified catalog.",
        )
        self.adk_gap_tool = Agent(
            name="chat_skill_gap",
            tools=[self.explain_skill_gaps],
            instruction="Analyze skill gaps against selected job requirements.",
        )

    def execute_tool(
        self,
        request: ChatToolRequest,
        context: ChatContext,
    ) -> ChatToolResult:
        """Execute a tool request deterministically using existing services."""
        name = request.tool_name
        params = request.parameters

        if name == "find_jobs":
            return self.find_jobs(request.tool_call_id, params, context)
        elif name == "explain_skill_gaps":
            return self.explain_skill_gaps(request.tool_call_id, context)
        elif name == "recommend_resources":
            return self.recommend_resources(request.tool_call_id, params, context)
        elif name == "explain_learning_plan":
            return self.explain_learning_plan(request.tool_call_id, context)
        elif name == "next_learning_action":
            return self.next_learning_action(request.tool_call_id, context)
        elif name == "summarize_career_status":
            return self.summarize_career_status(request.tool_call_id, context)
        elif name == "resume_guidance":
            return self.resume_guidance(request.tool_call_id, context)
        else:
            return ChatToolResult(
                tool_call_id=request.tool_call_id,
                tool_name=name,
                success=False,
                provenance="CareerChatToolAdapters",
                runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
                error=f"Unknown tool requested: {name}",
                data={},
            )

    def find_jobs(
        self,
        tool_call_id: str,
        params: dict[str, Any],
        context: ChatContext,
    ) -> ChatToolResult:
        """Query JobScoutAgent for relevant career opportunities."""
        query_text = params.get("query") or context.target_role or "AI Engineer"

        profile = StudentProfile(
            student_id=context.student_id,
            name="Student",
            target_role=context.target_role or "AI Engineer",
            skills=context.demonstrated_skills or ["Python"],
            education_level="Undergraduate",
            major="Computer Science",
            interests=[query_text],
        )
        search_query = OpportunitySearchQuery(
            role=context.target_role or "AI Engineer",
            location="Remote",
            internship_only=True,
            keywords=[query_text] if query_text else ["Python"],
        )

        matches = self.job_scout.run(profile, search_query)

        provider_class_name = self.job_scout.provider.__class__.__name__
        is_mock_provider = "Mock" in provider_class_name

        opportunities = [
            {
                "id": m.opportunity.opportunity_id,
                "title": m.opportunity.role,
                "company": (
                    f"Demo Opportunity — {m.opportunity.company}"
                    if (is_mock_provider or getattr(m.opportunity, "is_demo", False))
                    else m.opportunity.company
                ),
                "location": m.opportunity.location,
                "is_demo": is_mock_provider or getattr(m.opportunity, "is_demo", False),
                "source_label": (
                    "Demo / Mock Opportunity"
                    if (is_mock_provider or getattr(m.opportunity, "is_demo", False))
                    else "Live Job Source: Adzuna"
                ),
                "demonstrated_skills": m.demonstrated_skills,
                "missing_skills": m.missing_skills,
                "why_relevant": m.why_relevant,
            }
            for m in matches[:5]
        ]

        runtime = (
            ExecutionRuntime.GOOGLE_ADK
            if self.adk_coordinator is not None
            else ExecutionRuntime.DETERMINISTIC_PYTHON
        )

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="find_jobs",
            success=True,
            provenance="JobScoutAgent (ADK Coordinated)"
            if self.adk_coordinator
            else "JobScoutAgent",
            runtime=runtime,
            data={
                "query": query_text,
                "count": len(opportunities),
                "opportunities": opportunities,
            },
        )

    def explain_skill_gaps(
        self,
        tool_call_id: str,
        context: ChatContext,
    ) -> ChatToolResult:
        """Provide verified skill gap comparison for the selected job."""
        if not context.selected_opportunity_id:
            return ChatToolResult(
                tool_call_id=tool_call_id,
                tool_name="explain_skill_gaps",
                success=False,
                provenance="SkillGapAnalyzer",
                runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
                error="No target job selected. Please select an opportunity first.",
                data={"missing_context": ["selected_opportunity_id"]},
            )

        if not context.resume_analyzed:
            return ChatToolResult(
                tool_call_id=tool_call_id,
                tool_name="explain_skill_gaps",
                success=False,
                provenance="SkillGapAnalyzer",
                runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
                error="Resume has not been analyzed yet. Upload and analyze your resume first.",
                data={"missing_context": ["resume_analyzed"]},
            )

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="explain_skill_gaps",
            success=True,
            provenance="SkillGapAnalyzer",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "job_title": context.selected_opportunity_title or "Target Role",
                "demonstrated_skills": context.demonstrated_skills,
                "partial_skills": context.partial_skills,
                "missing_skills": context.missing_skills,
                "gap_count": len(context.missing_skills),
            },
        )

    def recommend_resources(
        self,
        tool_call_id: str,
        params: dict[str, Any],
        context: ChatContext,
    ) -> ChatToolResult:
        """Look up canonical learning resources from ResourceCatalog."""
        skills = params.get("skills")
        if not skills:
            skills = context.missing_skills or context.demonstrated_skills or ["Python"]
        elif isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

        cat_filter = params.get("category")
        limit = params.get("limit", 6)

        seen_ids = set()
        matched: list[Any] = []
        for s in skills:
            if cat_filter:
                res_list = self.resource_catalog.get_resources_by_category([s], cat_filter)
            else:
                res_list = self.resource_catalog.get_resources_for_skill(s)

            for r in res_list:
                if r.resource_id not in seen_ids:
                    seen_ids.add(r.resource_id)
                    matched.append(r)
                if len(matched) >= limit:
                    break
            if len(matched) >= limit:
                break

        serialized = [
            {
                "id": r.resource_id,
                "title": r.title,
                "provider": r.provider,
                "category": r.category,
                "url": str(r.url) if r.url else None,
                "estimated_duration": r.estimated_duration,
                "relevant_skills": r.relevant_skills,
                "difficulty": r.difficulty,
                "free_or_paid": r.free_or_paid,
            }
            for r in matched
        ]

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="recommend_resources",
            success=True,
            provenance="ResourceCatalog",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "queried_skills": skills,
                "count": len(serialized),
                "resources": serialized,
            },
        )

    def explain_learning_plan(
        self,
        tool_call_id: str,
        context: ChatContext,
    ) -> ChatToolResult:
        """Inspect the active weekly learning plan status."""
        if not context.plan_generated:
            return ChatToolResult(
                tool_call_id=tool_call_id,
                tool_name="explain_learning_plan",
                success=False,
                provenance="SkillBuilderAgent",
                runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
                error="Learning plan has not been generated yet. Generate your plan in My Learning Plan first.",
                data={"missing_context": ["plan_generated"]},
            )

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="explain_learning_plan",
            success=True,
            provenance="SkillBuilderAgent",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "duration_weeks": context.plan_duration_weeks or 4,
                "active_week": context.active_week,
                "target_role": context.target_role or "AI Engineer",
                "focused_skills": context.missing_skills[:4]
                if context.missing_skills
                else ["Core Skills"],
            },
        )

    def next_learning_action(
        self,
        tool_call_id: str,
        context: ChatContext,
    ) -> ChatToolResult:
        """Identify immediate next learning action from the active week and canonical catalog."""
        target_skills = context.missing_skills or ["Python", "FastAPI"]
        actionable_resources = self.resource_catalog.get_resources_by_category(
            target_skills,
            "PRACTICE",
        )
        if not actionable_resources:
            actionable_resources = self.resource_catalog.get_resources_by_category(
                target_skills,
                "WATCH",
            )
        if not actionable_resources:
            actionable_resources = self.resource_catalog.get_resources_for_skill(target_skills[0])

        serialized = [
            {
                "id": r.resource_id,
                "title": r.title,
                "provider": r.provider,
                "category": r.category,
                "url": str(r.url) if r.url else None,
                "estimated_duration": r.estimated_duration,
                "relevant_skills": r.relevant_skills,
            }
            for r in actionable_resources[:2]
        ]

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="next_learning_action",
            success=True,
            provenance="ResourceCatalog",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "active_week": context.active_week,
                "primary_skill": target_skills[0] if target_skills else "General",
                "recommended_actions": serialized,
            },
        )

    def summarize_career_status(
        self,
        tool_call_id: str,
        context: ChatContext,
    ) -> ChatToolResult:
        """Provide non-PII summary of current student preparation status."""
        total_skills = len(context.demonstrated_skills) + len(context.missing_skills)
        readiness_pct = (
            int((len(context.demonstrated_skills) / total_skills) * 100) if total_skills > 0 else 0
        )

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="summarize_career_status",
            success=True,
            provenance="CareerCoordinator",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "target_role": context.target_role or "Unassigned",
                "selected_opportunity": context.selected_opportunity_title or "None selected",
                "resume_analyzed": context.resume_analyzed,
                "plan_generated": context.plan_generated,
                "demonstrated_skill_count": len(context.demonstrated_skills),
                "missing_skill_count": len(context.missing_skills),
                "readiness_estimate_percent": readiness_pct,
            },
        )

    def resume_guidance(
        self,
        tool_call_id: str,
        context: ChatContext,
    ) -> ChatToolResult:
        """Provide guidance for resume strengthening based strictly on missing skills."""
        if not context.resume_analyzed:
            return ChatToolResult(
                tool_call_id=tool_call_id,
                tool_name="resume_guidance",
                success=False,
                provenance="PrivateResumeAgent",
                runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
                error="Please upload and analyze your resume first so guidance can be grounded in actual evidence.",
                data={"missing_context": ["resume_analyzed"]},
            )

        advice_items = []
        for skill in context.missing_skills[:3]:
            advice_items.append(
                f"Add quantifiable project evidence demonstrating hands-on experience with {skill}."
            )

        if not advice_items:
            advice_items.append(
                "Ensure your bullet points quantify outcomes (metrics, performance gains, test coverage)."
            )

        return ChatToolResult(
            tool_call_id=tool_call_id,
            tool_name="resume_guidance",
            success=True,
            provenance="PrivateResumeAgent",
            runtime=ExecutionRuntime.DETERMINISTIC_PYTHON,
            data={
                "target_role": context.target_role or "AI Engineer",
                "recommended_bullet_focus": advice_items,
                "key_missing_skills": context.missing_skills[:4],
            },
        )
