import re
from typing import Any, Dict

SENSITIVE_KEYS = {"api_key", "secret", "token", "password", "chat_id"}


def redact_value(value: str) -> str:
    """Mask sensitive value."""
    if not isinstance(value, str):
        value = str(value)
    if len(value) <= 4:
        return "***"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def redact_mapping(mapping: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive keys in a mapping."""
    result: Dict[str, Any] = {}
    for key, value in mapping.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            if isinstance(value, str) and value:
                result[key] = redact_value(value)
            else:
                result[key] = "***"
        elif isinstance(value, dict):
            result[key] = redact_mapping(value) # type: ignore
        else:
            result[key] = value
    return result


def redact_text(text: str) -> str:
    """Redact potential secrets in plain text."""
    if not text:
        return text

    for key in SENSITIVE_KEYS:
        # Match key=value
        pattern_eq = re.compile(rf"({key}[-_]?\w*)\s*=\s*([^\s,;&]+)", re.IGNORECASE)
        text = pattern_eq.sub(lambda m: f"{m.group(1)}=***", text)

        # Match "key":"value" - catch all variations of quotes and spaces
        # Match something like "API_SECRET": "mysecret" or API_SECRET : "mysecret"
        # We look for the sensitive key, followed by optional word chars, followed by quotes and colons, then a quoted value
        # re.sub with a function to only replace the value part

        # This handles: "SECRET": "value", 'SECRET': 'value', SECRET: "value"
        pattern_json = re.compile(rf"([\"']?{key}[-_]?\w*[\"']?\s*:\s*[\"'])([^\"']+)([\"'])", re.IGNORECASE)
        text = pattern_json.sub(lambda m: f"{m.group(1)}***{m.group(3)}", text)

    return text
