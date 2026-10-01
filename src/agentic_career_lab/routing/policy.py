from .models import PrivacyLevel, RoutingDecision, RuntimeType, TaskType


class HybridRouter:
    @staticmethod
    def route(task_type: TaskType) -> RoutingDecision:
        if task_type == TaskType.OPPORTUNITY_SEARCH:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Live jobs are retrieved from Adzuna or mock provider.",
                privacy_level=PrivacyLevel.PUBLIC,
                cloud_allowed=True,
                fallback_allowed=True,
            )
        elif task_type == TaskType.REQUIREMENT_INTERPRETATION:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Semantic interpretation optional; default to deterministic parsing.",
                privacy_level=PrivacyLevel.PUBLIC,
                cloud_allowed=True,
                fallback_allowed=True,
            )
        elif task_type == TaskType.RESUME_ANALYSIS:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.GEMMA_OLLAMA,
                reason="Private resume understanding must be local.",
                privacy_level=PrivacyLevel.PRIVATE,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        elif task_type == TaskType.RESUME_REWRITE:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.GEMMA_OLLAMA,
                reason="Private resume rewriting must be local.",
                privacy_level=PrivacyLevel.PRIVATE,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        elif task_type == TaskType.SKILL_MATCHING:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Exact evidence comparison is deterministic.",
                privacy_level=PrivacyLevel.STRUCTURED,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        elif task_type == TaskType.GAP_ANALYSIS:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Gap analysis is deterministic.",
                privacy_level=PrivacyLevel.STRUCTURED,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        elif task_type == TaskType.LEARNING_PLAN:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.GEMINI_VERTEX,
                reason="Learning-plan synthesis requires cloud reasoning.",
                privacy_level=PrivacyLevel.STRUCTURED,
                cloud_allowed=True,
                fallback_allowed=True,
            )
        elif task_type == TaskType.RESOURCE_LOOKUP:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Curated resource catalog.",
                privacy_level=PrivacyLevel.PUBLIC,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        elif task_type == TaskType.PORTFOLIO_PROJECT:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.GEMINI_VERTEX,
                reason="Project generation uses structured gaps.",
                privacy_level=PrivacyLevel.STRUCTURED,
                cloud_allowed=True,
                fallback_allowed=True,
            )
        elif task_type == TaskType.CLAIM_VALIDATION:
            return RoutingDecision(
                task_type=task_type,
                runtime=RuntimeType.PYTHON,
                reason="Validation is deterministic.",
                privacy_level=PrivacyLevel.STRUCTURED,
                cloud_allowed=False,
                fallback_allowed=False,
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")
