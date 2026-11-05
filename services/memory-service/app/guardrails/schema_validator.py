import json
import structlog
from typing import Dict, Any, Tuple
from pydantic import ValidationError

logger = structlog.get_logger(__name__)

class SchemaValidator:
    """Enforces strict JSON schema contracts on model output."""

    @staticmethod
    def validate_json_contract(raw_text: str, schema_cls) -> Tuple[bool, Any, str]:
        """Attempts to parse and validate text against a Pydantic schema model."""
        try:
            # Strip markdown code blocks if model wrapped output in ```json
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            validated = schema_cls.model_validate(parsed)
            return True, validated, "VALID"
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warn("schema_validation_failed", error=str(e), sample=raw_text[:100])
            return False, None, str(e)


schema_validator = SchemaValidator()

