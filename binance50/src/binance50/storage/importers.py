from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.datasets import scored_candidates_to_dataframe
from binance50.signals.models import SignalScoringResult


def import_signal_scoring_result(result: SignalScoringResult, config: AppConfig) -> dict[str, Any]:
    """Import a signal scoring result into the storage system."""

    # 1. Quality check enforcement
    if result.quality_report and result.quality_report.status != "passed":
        from binance50.core.exceptions import SignalQualityError
        raise SignalQualityError("Cannot import scored signals: Quality checks failed.")

    # 2. DataFrame conversion and execution field blocking
    df = scored_candidates_to_dataframe(result.scored_candidates)

    # In a real impl, we would use the actual Storage Engine
    # For now, we return a mock manifest reflecting the intended metadata

    from datetime import datetime, timezone

    return {
        "dataset_name": config.signals.output_dataset_name,
        "symbol": result.metadata.symbol,
        "interval": result.metadata.interval,
        "row_count": len(df),
        "config_hash": result.metadata.config_hash,
        "output_hash": result.metadata.output_hash,
        "confluence_groups_summary": f"Imported {result.metadata.confluence_group_count} groups",
        "imported_at": int(datetime.now(timezone.utc).timestamp() * 1000)
    }
