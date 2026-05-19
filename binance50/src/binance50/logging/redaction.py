import re
from collections.abc import Mapping, Sequence
from typing import Any

from binance50.core.exceptions import SecretLeakError

# Expanded list of sensitive keys
SENSITIVE_KEYS = {
    "api_key",
    "apisecret",
    "secret",
    "signature",
    "token",
    "authorization",
    "x-mbx-apikey",
    "telegram_bot_token",
    "telegram_chat_id",
    "listen_key",
    "listenkey",
    "private_key",
    "password",
    "chat_id",
}

# Regex for finding things that look like secrets even without keys
# E.g., very long alphanumeric strings that might be tokens or keys (Binance keys are typically 64 chars)
SECRET_PATTERNS = [
    re.compile(r"([A-Za-z0-9_-]{64,})"),  # Binance keys
    re.compile(r"(Bearer\s+[A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE),  # Bearer tokens
    re.compile(r"([0-9]{8,10}:[a-zA-Z0-9_-]{35,})"),  # Telegram bot tokens
]


def normalize_sensitive_key(key: str) -> str:
    """Normalize a key for checking against sensitive list."""
    return key.lower().replace("-", "_")


def is_sensitive_key(key: str) -> bool:
    """Check if a key is considered sensitive."""
    norm_key = normalize_sensitive_key(key)
    return any(sensitive in norm_key for sensitive in SENSITIVE_KEYS)


def contains_potential_secret(text: str) -> bool:
    """Check if text contains anything that looks like a secret."""
    if not isinstance(text, str):
        return False

    # Check for direct key matches
    norm_text = text.lower()
    for key in SENSITIVE_KEYS:
        if (
            f"{key}=" in norm_text
            or f"'{key}':" in norm_text
            or f'"{key}":' in norm_text
            or f"{key}:" in norm_text
        ):
            return True

    # Check patterns
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return True

    return False


def assert_no_secret_leak(text: str) -> None:
    """Raise SecretLeakError if text contains a potential secret."""
    if contains_potential_secret(str(text)):
        raise SecretLeakError("Potential secret leak detected in text")


def redact_value(value: Any, mask: str = "***REDACTED***") -> str:
    """Mask sensitive value."""
    if not value:
        return mask
    val_str = str(value)
    if len(val_str) <= 8:
        return mask
    # Show first 2 and last 2 characters, mask the rest
    return f"{val_str[:2]}{mask}{val_str[-2:]}"


def redact_text(text: str, mask: str = "***REDACTED***") -> str:
    """Redact potential secrets in plain text."""
    if not text or not isinstance(text, str):
        return str(text)

    # Redact query string like `signature=...`
    for key in SENSITIVE_KEYS:
        # Match key=value (URL params)
        pattern_eq = re.compile(rf"({key}[-_]?\w*)\s*=\s*([^\s,;&]+)", re.IGNORECASE)
        text = pattern_eq.sub(lambda m: f"{m.group(1)}={mask}", text)

        # Match JSON or dict "key":"value", 'key': 'value'
        pattern_json = re.compile(
            rf"([\"']?{key}[-_]?\w*[\"']?\s*:\s*[\"']?)([^\"',\s]+)([\"']?)", re.IGNORECASE
        )
        text = pattern_json.sub(lambda m: f"{m.group(1)}{mask}{m.group(3)}", text)

        # Match HTTP headers like X-MBX-APIKEY: value
        pattern_header = re.compile(rf"({key}[-_]?\w*)\s*:\s*([^\s,;&]+)", re.IGNORECASE)
        text = pattern_header.sub(lambda m: f"{m.group(1)}: {mask}", text)

    # Redact raw patterns (like tokens)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(mask, text)

    return text


def redact_mapping(mapping: Mapping[str, Any], mask: str = "***REDACTED***") -> dict[str, Any]:
    """Redact sensitive keys in a mapping recursively."""
    if not isinstance(mapping, Mapping):
        return mapping

    result: dict[str, Any] = {}
    for key, value in mapping.items():
        if is_sensitive_key(str(key)):
            result[key] = redact_value(value, mask)
        elif isinstance(value, Mapping):
            result[key] = redact_mapping(value, mask)
        elif isinstance(value, str):
            result[key] = redact_text(value, mask)
        elif isinstance(value, (list, tuple, set)):
            result[key] = redact_sequence(value, mask)
        else:
            result[key] = value
    return result


def redact_sequence(values: Any, mask: str = "***REDACTED***") -> list[Any]:
    """Redact sensitive values in a sequence recursively."""
    if not isinstance(values, Sequence) or isinstance(values, str):
        return values  # type: ignore

    result: list[Any] = []
    for item in values:
        if isinstance(item, Mapping):
            result.append(redact_mapping(item, mask))
        elif isinstance(item, str):
            result.append(redact_text(str(item), mask))
        elif isinstance(item, Sequence) and not isinstance(item, str):
            result.append(redact_sequence(list(item), mask))
        else:
            result.append(item)
    return result
