import uuid
from datetime import UTC, datetime

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import FetchPlanError
from binance50.market_data.intervals import interval_to_milliseconds, validate_interval
from binance50.market_data.ohlcv_models import OHLCVFetchChunk, OHLCVFetchPlan


def get_kline_endpoint_path(market_scope: MarketScope, config: AppConfig) -> str:
    if market_scope == MarketScope.SPOT:
        return config.market_data.spot_klines_path
    elif market_scope == MarketScope.USDM_FUTURES:
        return config.market_data.usdm_klines_path
    raise FetchPlanError(f"Unsupported market scope for fetching: {market_scope}")


def get_kline_max_limit(market_scope: MarketScope, config: AppConfig) -> int:
    if market_scope == MarketScope.SPOT:
        return min(config.market_data.spot_max_limit, 1000)
    elif market_scope == MarketScope.USDM_FUTURES:
        return min(config.market_data.usdm_max_limit, 1500)
    raise FetchPlanError(f"Unsupported market scope for limits: {market_scope}")


def build_ohlcv_fetch_plan(
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    start_time_ms: int,
    end_time_ms: int,
    config: AppConfig,
) -> OHLCVFetchPlan:
    validate_interval(interval, config)

    if start_time_ms >= end_time_ms:
        raise FetchPlanError(f"Start time ({start_time_ms}) must be < end time ({end_time_ms})")

    endpoint_path = get_kline_endpoint_path(market_scope, config)
    max_limit = get_kline_max_limit(market_scope, config)

    chunks = split_time_range_into_kline_chunks(
        symbol=symbol,
        interval=interval,
        start_time_ms=start_time_ms,
        end_time_ms=end_time_ms,
        max_limit=max_limit,
        endpoint_path=endpoint_path,
    )

    plan = OHLCVFetchPlan(
        plan_id=str(uuid.uuid4()),
        symbol=symbol.upper(),
        market_scope=market_scope,
        interval=interval,
        requested_start_ms=start_time_ms,
        requested_end_ms=end_time_ms,
        chunks=chunks,
        total_expected_requests=len(chunks),
        max_limit=max_limit,
        endpoint_path=endpoint_path,
        estimated_weight=0,
        created_at_utc=datetime.now(UTC).isoformat(),
        warnings=[],
    )

    plan.estimated_weight = estimate_fetch_weight(plan)
    validate_fetch_plan(plan, config)
    return plan


def split_time_range_into_kline_chunks(
    symbol: str,
    interval: str,
    start_time_ms: int,
    end_time_ms: int,
    max_limit: int,
    endpoint_path: str,
) -> list[OHLCVFetchChunk]:
    chunks = []
    current_start = start_time_ms
    ms_per_candle = interval_to_milliseconds(interval)
    max_ms_per_chunk = ms_per_candle * max_limit

    while current_start < end_time_ms:
        current_end = (
            current_start + max_ms_per_chunk - 1
        )  # -1 ms to not overlap exact boundary if necessary
        if current_end >= end_time_ms:
            current_end = end_time_ms

        limit = estimate_kline_request_count(current_start, current_end, interval)

        chunk = OHLCVFetchChunk(
            chunk_id=str(uuid.uuid4()),
            symbol=symbol.upper(),
            interval=interval,
            start_time_ms=current_start,
            end_time_ms=current_end,
            limit=limit,
            endpoint_path=endpoint_path,
            estimated_weight=1,
            reason="time_split",
        )
        chunks.append(chunk)
        current_start = current_end + 1

    return chunks


def estimate_kline_request_count(start_time_ms: int, end_time_ms: int, interval: str) -> int:
    ms_per_candle = interval_to_milliseconds(interval)
    diff = end_time_ms - start_time_ms
    count = int(diff // ms_per_candle)
    if diff % ms_per_candle != 0:
        count += 1
    return max(1, count)


def estimate_fetch_weight(plan: OHLCVFetchPlan) -> int:
    # Most public klines endpoint costs 1 weight per request.
    # Spot /api/v3/klines is 1
    # USDM /fapi/v1/klines is 1
    # We can refine this later if weight logic becomes dynamic
    total = 0
    for chunk in plan.chunks:
        total += chunk.estimated_weight
    return total


def validate_fetch_plan(plan: OHLCVFetchPlan, config: AppConfig) -> None:
    if plan.total_expected_requests > 100:
        plan.warnings.append(
            f"Fetch plan requires {plan.total_expected_requests} requests. This might take a long time."
        )
