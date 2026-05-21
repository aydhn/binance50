from datetime import UTC, datetime
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.market_data.fetch_plan import OHLCVFetchPlan
from binance50.market_data.incremental import IncrementalUpdatePlan
from binance50.market_data.ohlcv_models import OHLCVFrameMetadata
from binance50.market_data.quality import OHLCVQualityReport
from binance50.market_data.store import OHLCVStore


def build_ohlcv_summary(
    df: pd.DataFrame, metadata: OHLCVFrameMetadata | None = None
) -> dict[str, Any]:
    if df.empty:
        return {"status": "empty", "row_count": 0}

    summary = {
        "status": "loaded",
        "row_count": len(df),
        "start_time": int(df["open_time"].min()),
        "end_time": int(df["open_time"].max()),
        "columns": list(df.columns),
    }

    if metadata:
        summary["metadata"] = metadata.dict_redacted()

    return summary


def build_ohlcv_quality_summary(report: OHLCVQualityReport) -> dict[str, Any]:
    return {
        "symbol": report.symbol,
        "market_scope": report.market_scope.value,
        "interval": report.interval,
        "status": report.status.value,
        "row_count": report.row_count,
        "duplicate_count": report.duplicate_count,
        "gap_count": report.gap_count,
        "out_of_order_count": report.out_of_order_count,
        "incomplete_last_candle": report.incomplete_last_candle,
        "issue_count": len(report.issues),
        "issues": [i.model_dump() for i in report.issues],
    }


def build_fetch_plan_report(plan: OHLCVFetchPlan) -> dict[str, Any]:
    return {
        "plan_id": plan.plan_id,
        "symbol": plan.symbol,
        "market_scope": plan.market_scope.value,
        "interval": plan.interval,
        "requested_start_ms": plan.requested_start_ms,
        "requested_end_ms": plan.requested_end_ms,
        "chunk_count": len(plan.chunks),
        "total_expected_requests": plan.total_expected_requests,
        "max_limit_per_request": plan.max_limit,
        "endpoint_path": plan.endpoint_path,
        "estimated_weight": plan.estimated_weight,
        "warnings": plan.warnings,
    }


def build_incremental_update_report(plan: IncrementalUpdatePlan) -> dict[str, Any]:
    return {
        "symbol": plan.symbol,
        "market_scope": plan.market_scope.value,
        "interval": plan.interval,
        "existing_start": plan.existing_start_open_time,
        "existing_end": plan.existing_end_open_time,
        "last_complete": plan.last_complete_open_time,
        "next_start": plan.next_start_time_ms,
        "requested_end": plan.requested_end_time_ms,
        "overlap_candles": plan.overlap_candles,
        "needs_update": plan.needs_update,
        "reason": plan.reason,
        "warnings": plan.warnings,
    }


def build_market_data_health_report(
    config: AppConfig, store: OHLCVStore | None = None
) -> dict[str, Any]:
    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": {
            "enabled": config.market_data.enabled,
            "real_fetch_enabled": config.market_data.real_fetch_enabled,
            "cache_enabled": config.market_data.cache_enabled,
            "incremental_enabled": config.market_data.incremental_enabled,
            "allowed_intervals_count": len(config.market_data.allowed_intervals),
        },
        "safety_status": (
            "safe" if not config.market_data.real_fetch_enabled else "warning_real_fetch_enabled"
        ),
        "cache": {"available_items": 0, "items": []},
    }

    if store:
        available = store.list_available()
        report["cache"]["available_items"] = len(available)
        report["cache"]["items"] = available

    return report


def format_ohlcv_table_preview(df: pd.DataFrame, rows: int = 5) -> list[dict[str, Any]]:
    if df.empty:
        return []

    head = df.head(rows).to_dict("records")
    tail = df.tail(rows).to_dict("records") if len(df) > rows else []

    # Merge and deduplicate
    preview = []
    seen = set()

    for row in head + tail:
        ot = row["open_time"]
        if ot not in seen:
            seen.add(ot)
            preview.append(row)

    return sorted(preview, key=lambda x: x["open_time"])
