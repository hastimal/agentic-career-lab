"""Privacy enforcement, cloud consent checks, and PII payload sanitization."""

import re
from typing import Any

from agentic_career_lab.chat.models import (
    ChatContext,
    ConsentDecision,
)


class ConsentViolationError(RuntimeError):
    """Raised when an operation requiring user consent is attempted without valid consent."""

    pass


class CareerChatPrivacyGuard:
    """Enforces central privacy policies, cloud consent validation, and payload sanitization."""

    # Disallowed sensitive patterns (emails, phone numbers, SSN-like digits)
    _EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    _PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")

    @classmethod
    def verify_cloud_consent(cls, consent: ConsentDecision | None) -> None:
        """Validate that cloud synthesis has explicit, active student consent.

        Raises:
            ConsentViolationError: If consent is False or missing.
        """
        if not consent or not consent.consent_given:
            raise ConsentViolationError(
                "Cloud Gemini synthesis is disabled. Student has not granted explicit cloud consent."
            )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Scrub PII (emails, phone numbers) from any outgoing text."""
        sanitized = cls._EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
        sanitized = cls._PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)
        return sanitized

    @classmethod
    def build_sanitized_cloud_payload(
        cls,
        user_prompt: str,
        context: ChatContext,
    ) -> dict[str, Any]:
        """Construct minimal, strictly allowlisted payload for optional cloud Gemini synthesis.

        Rules:
        - NEVER send raw resume text or raw uploaded documents.
        - NEVER send student phone numbers, email addresses, or home locations.
        - Send ONLY allowlisted non-PII fields: target_role and sanitized_skill_gaps.
        """
        cls.verify_cloud_consent(context.consent)

        sanitized_prompt = cls.sanitize_text(user_prompt)

        return {
            "prompt": sanitized_prompt,
            "target_role": context.target_role or "AI Engineer",
            "sanitized_skill_gaps": list(context.missing_skills[:10]),
            "cloud_consent_active": True,
            "allowed_scope": list(context.consent.scope),
        }

    @classmethod
    def sanitize_telemetry_attributes(cls, attributes: dict[str, Any]) -> dict[str, Any]:
        """Strip raw content, prompts, resume text, and PII from telemetry attributes."""
        sanitized: dict[str, Any] = {}
        disallowed_keys = {
            "prompt",
            "raw_prompt",
            "resume_text",
            "resume_content",
            "user_content",
            "response_text",
            "completion",
            "secret",
            "api_key",
            "token",
        }

        for k, v in attributes.items():
            key_lower = k.lower()
            if any(bad in key_lower for bad in disallowed_keys):
                continue
            if isinstance(v, str):
                sanitized[k] = cls.sanitize_text(v)
            else:
                sanitized[k] = v

        return sanitized
