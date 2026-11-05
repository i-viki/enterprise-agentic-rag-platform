import re
import structlog

logger = structlog.get_logger(__name__)

class EgressLeakageFilter:
    """Sanitizes outgoing LLM responses to ensure system prompts or delimiters do not leak."""

    FORBIDDEN_TAGS = [
        r"<\/?context>",
        r"<\/?working_memory>",
        r"<\/?system>",
        r"<\/?system_instructions>",
        r"<\/?rules>",
        r"<\/?query>",
        r"###\s*System:",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
    ]

    SECRET_PATTERNS = [
        r"(?i)(?:api[_-]?key|secret|password|bearer\s+[a-z0-9_\-\.]+)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-\.]{12,}['\"]?",
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        sanitized = text

        # Strip XML/Markdown system envelopes
        for pattern in cls.FORBIDDEN_TAGS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        # Mask potential leaked internal secrets
        for pattern in cls.SECRET_PATTERNS:
            sanitized = re.sub(pattern, "[CONFIDENTIAL_CREDENTIAL_REDACTED]", sanitized)

        return sanitized.strip()


egress_leakage_filter = EgressLeakageFilter()

