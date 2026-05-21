from datetime import timedelta
from enum import StrEnum

from binance50.config.models import AppConfig
from binance50.core.exceptions import UnsupportedIntervalError


class KlineInterval(StrEnum):
    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    SIX_HOURS = "6h"
    EIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


_INTERVAL_MS = {
    "1m": 60 * 1000,
    "3m": 3 * 60 * 1000,
    "5m": 5 * 60 * 1000,
    "15m": 15 * 60 * 1000,
    "30m": 30 * 60 * 1000,
    "1h": 60 * 60 * 1000,
    "2h": 2 * 60 * 60 * 1000,
    "4h": 4 * 60 * 60 * 1000,
    "6h": 6 * 60 * 60 * 1000,
    "8h": 8 * 60 * 60 * 1000,
    "12h": 12 * 60 * 60 * 1000,
    "1d": 24 * 60 * 60 * 1000,
    "3d": 3 * 24 * 60 * 60 * 1000,
    "1w": 7 * 24 * 60 * 60 * 1000,
    "1M": 30 * 24 * 60 * 60 * 1000,  # Approximate
}


def validate_interval(interval: str, config: AppConfig | None = None) -> None:
    try:
        KlineInterval(interval)
    except ValueError:
        raise UnsupportedIntervalError(f"Interval {interval} is not a valid KlineInterval")

    if config is not None and interval not in config.market_data.allowed_intervals:
        raise UnsupportedIntervalError(f"Interval {interval} is not in allowed_intervals config")


def interval_to_milliseconds(interval: str) -> int:
    ms = _INTERVAL_MS.get(interval)
    if ms is None:
        raise UnsupportedIntervalError(f"Unknown interval {interval}")
    return ms


def interval_to_timedelta(interval: str) -> timedelta:
    ms = interval_to_milliseconds(interval)
    return timedelta(milliseconds=ms)


def floor_timestamp_to_interval(timestamp_ms: int, interval: str) -> int:
    ms = interval_to_milliseconds(interval)
    return (timestamp_ms // ms) * ms


def ceil_timestamp_to_interval(timestamp_ms: int, interval: str) -> int:
    ms = interval_to_milliseconds(interval)
    floored = floor_timestamp_to_interval(timestamp_ms, interval)
    if floored == timestamp_ms:
        return floored
    return floored + ms


def expected_next_open_time(open_time_ms: int, interval: str) -> int:
    ms = interval_to_milliseconds(interval)
    return open_time_ms + ms


def is_candle_closed(
    open_time_ms: int, close_time_ms: int, interval: str, now_ms: int | None = None
) -> bool:
    if now_ms is None:
        import time

        now_ms = int(time.time() * 1000)
    return now_ms > close_time_ms


def get_default_history_start(end_time_ms: int, interval: str, config: AppConfig) -> int:
    days = config.market_data.default_history_days.get(interval)
    if days is None:
        raise UnsupportedIntervalError(f"No default_history_days configured for {interval}")
    ms_to_subtract = days * 24 * 60 * 60 * 1000
    start_ms = end_time_ms - ms_to_subtract
    return floor_timestamp_to_interval(start_ms, interval)
