import time
from datetime import UTC, datetime


def get_current_time_ms() -> int:
    """Get current time in milliseconds."""
    return int(time.time() * 1000)


def get_utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)
