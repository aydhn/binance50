from datetime import UTC
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

    from datetime import datetime

    return {
        "dataset_name": config.signals.output_dataset_name,
        "symbol": result.metadata.symbol,
        "interval": result.metadata.interval,
        "row_count": len(df),
        "config_hash": result.metadata.config_hash,
        "output_hash": result.metadata.output_hash,
        "confluence_groups_summary": f"Imported {result.metadata.confluence_group_count} groups",
        "imported_at": int(datetime.now(UTC).timestamp() * 1000),
    }


from binance50.regimes.models import RegimeRunResult


def import_regime_result(result: RegimeRunResult, config: AppConfig) -> dict[str, Any]:
    """Import a regime classification result into the storage system."""
    if result.quality_report and result.quality_report.status != "passed":
        from binance50.core.exceptions import RegimeQualityError

        raise RegimeQualityError("Cannot import regime classifications: Quality checks failed.")

    from binance50.regimes.datasets import regime_classifications_to_dataframe

    df = regime_classifications_to_dataframe(result.classifications)

    invalid_cols = [
        "order_id",
        "quantity",
        "leverage",
        "entry_price",
        "exit_price",
        "stop_loss",
        "take_profit",
    ]
    for col in invalid_cols:
        if col in df.columns:
            from binance50.core.exceptions import RegimeLeakageError

            raise RegimeLeakageError(
                f"Cannot import regime classifications: Execution column {col} blocked."
            )

    return {
        "dataset_name": config.regimes.output_dataset_name,
        "symbol": result.metadata.symbol,
        "interval": result.metadata.interval,
        "row_count": len(df),
        "config_hash": result.metadata.config_hash,
        "output_hash": result.metadata.output_hash,
        "transition_count": result.metadata.transition_count,
        "method": result.metadata.method,
    }
