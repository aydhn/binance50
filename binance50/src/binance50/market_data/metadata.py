from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from binance50.core.enums import MarketScope
from binance50.market_data.cache import compute_dataframe_hash
from binance50.market_data.ohlcv_models import (
    OHLCVFrameMetadata,
    OHLCVSource,
    OHLCVValidationStatus,
)
from binance50.market_data.quality import OHLCVQualityReport


def build_frame_metadata(
    df: pd.DataFrame,
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    source: OHLCVSource,
    cache_path: Path | None,
    quality_report: OHLCVQualityReport | None,
) -> OHLCVFrameMetadata:

    if df.empty:
        return OHLCVFrameMetadata(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            source=source,
            row_count=0,
            start_open_time=0,
            end_open_time=0,
            generated_at_utc=datetime.now(UTC).isoformat(),
            last_complete_open_time=None,
            contains_incomplete_last_candle=False,
            cache_path=str(cache_path) if cache_path else None,
            data_hash=compute_dataframe_hash(df),
            quality_status=OHLCVValidationStatus.INVALID,
            warnings=["Empty DataFrame"],
        )

    # Sort to ensure accurate start/end
    sorted_df = df.sort_values(by="open_time")
    start_open_time = int(sorted_df["open_time"].iloc[0])
    end_open_time = int(sorted_df["open_time"].iloc[-1])

    # Calculate last complete
    from binance50.market_data.incremental import find_last_complete_candle

    last_complete = find_last_complete_candle(sorted_df, interval)

    status = quality_report.status if quality_report else OHLCVValidationStatus.UNKNOWN
    if status == OHLCVValidationStatus.UNKNOWN and quality_report is None:
        status = (
            OHLCVValidationStatus.VALID
        )  # Assumed valid if no report, better practice is to always pass a report

    contains_incomplete = quality_report.incomplete_last_candle if quality_report else False

    warnings = []
    if quality_report and quality_report.issues:
        for issue in quality_report.issues:
            if issue.severity == OHLCVValidationStatus.WARNING:
                warnings.append(issue.message)

    return OHLCVFrameMetadata(
        symbol=symbol,
        market_scope=market_scope,
        interval=interval,
        source=source,
        row_count=len(df),
        start_open_time=start_open_time,
        end_open_time=end_open_time,
        generated_at_utc=datetime.now(UTC).isoformat(),
        last_complete_open_time=last_complete,
        contains_incomplete_last_candle=contains_incomplete,
        cache_path=str(cache_path) if cache_path else None,
        data_hash=compute_dataframe_hash(df),
        quality_status=status,
        warnings=warnings,
    )


def metadata_to_dict(metadata: OHLCVFrameMetadata) -> dict[str, Any]:
    return metadata.dict_redacted()


def metadata_from_dict(payload: dict[str, Any]) -> OHLCVFrameMetadata:
    return OHLCVFrameMetadata(**payload)


def compare_metadata(old: OHLCVFrameMetadata | None, new: OHLCVFrameMetadata) -> dict[str, Any]:
    if not old:
        return {"status": "new", "changes": ["Created new metadata"]}

    changes = []
    if old.row_count != new.row_count:
        changes.append(f"Row count changed: {old.row_count} -> {new.row_count}")
    if old.start_open_time != new.start_open_time:
        changes.append(f"Start time changed: {old.start_open_time} -> {new.start_open_time}")
    if old.end_open_time != new.end_open_time:
        changes.append(f"End time changed: {old.end_open_time} -> {new.end_open_time}")
    if old.data_hash != new.data_hash:
        changes.append("Data hash changed")

    return {"status": "modified" if changes else "unchanged", "changes": changes}
