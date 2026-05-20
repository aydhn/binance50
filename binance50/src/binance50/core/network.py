import time
from enum import StrEnum


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class NetworkStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class ConnectionState(StrEnum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    RECONNECTING = "reconnecting"


def is_https_url(url: str) -> bool:
    return url.startswith("https://")


def is_wss_url(url: str) -> bool:
    return url.startswith("wss://")


def sanitize_url_for_log(url: str) -> str:
    # Phase 5: we just strip query params if any. If signature is there, we want to strip it.
    if "?" in url:
        base, query = url.split("?", 1)
        # Redact potentially sensitive parameters like signature
        # Simplified redaction for log URLs:
        if "signature=" in query:
            return f"{base}?REDACTED"
        return url
    return url


def parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def monotonic_ms() -> int:
    return int(time.monotonic() * 1000)
