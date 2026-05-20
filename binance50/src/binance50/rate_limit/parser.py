import contextlib
from collections.abc import Mapping
from datetime import UTC, datetime

from binance50.rate_limit.models import RateLimitHeaderSnapshot


def normalize_header_key(key: str) -> str:
    return key.lower().strip()


def parse_retry_after(headers: Mapping[str, str]) -> float | None:
    for k, v in headers.items():
        if normalize_header_key(k) == "retry-after":
            try:
                return float(v)
            except ValueError:
                return None
    return None


def extract_interval_from_mbx_header(header_name: str) -> tuple[int, str] | None:
    """Extracts (1, 'M') from X-MBX-USED-WEIGHT-1M"""
    parts = header_name.split("-")
    if len(parts) >= 5:
        interval_str = parts[-1]
        try:
            val = int(interval_str[:-1])
            unit = interval_str[-1].upper()
            return val, unit
        except ValueError:
            pass
    return None


def parse_used_weight_headers(headers: Mapping[str, str]) -> dict[str, int]:
    result = {}
    for k, v in headers.items():
        k_lower = normalize_header_key(k)
        if k_lower.startswith("x-mbx-used-weight"):
            with contextlib.suppress(ValueError):
                result[k_lower] = int(v)
    return result


def parse_order_count_headers(headers: Mapping[str, str]) -> dict[str, int]:
    result = {}
    for k, v in headers.items():
        k_lower = normalize_header_key(k)
        if k_lower.startswith("x-mbx-order-count"):
            with contextlib.suppress(ValueError):
                result[k_lower] = int(v)
    return result


def parse_rate_limit_headers(headers: Mapping[str, str]) -> RateLimitHeaderSnapshot:
    used_weight = parse_used_weight_headers(headers)
    order_count = parse_order_count_headers(headers)

    snapshot = RateLimitHeaderSnapshot(
        used_weight_1m=used_weight.get("x-mbx-used-weight-1m")
        or used_weight.get("x-mbx-used-weight"),
        used_weight_5m=used_weight.get("x-mbx-used-weight-5m"),
        used_weight_1h=used_weight.get("x-mbx-used-weight-1h"),
        order_count_10s=order_count.get("x-mbx-order-count-10s"),
        order_count_1m=order_count.get("x-mbx-order-count-1m"),
        retry_after_seconds=parse_retry_after(headers),
        raw_headers={
            k: v
            for k, v in headers.items()
            if k.lower().startswith("x-mbx") or k.lower() == "retry-after"
        },
        parsed_at_utc=datetime.now(UTC),
    )
    return snapshot
