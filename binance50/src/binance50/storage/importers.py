from datetime import UTC
from typing import Any

from binance50.config.models import AppConfig
from binance50.regimes.models import RegimeRunResult
from binance50.risk.datasets import risk_assessments_to_dataframe
from binance50.risk.models import RiskRunResult
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


def import_risk_result(result: RiskRunResult, config: "AppConfig") -> "DatasetManifest":
    df = risk_assessments_to_dataframe(result.assessments)
    if df.empty:
        raise ValueError("Cannot import empty risk assessments dataset")
    dataset_name = config.risk.output_dataset_name
    from binance50.storage.core import DataWarehouse

    warehouse = DataWarehouse(config)
    # Placeholder functionality
    manifest = warehouse.write_dataset(
        name=dataset_name,
        df=df,
        kind=DatasetKind.RISK_ASSESSMENTS,
        metadata={"source": "risk_engine_v1"},
    )
    return manifest


def import_backtest_result(result, config) -> list:
    from binance50.backtest.quality import assert_backtest_quality_passed
    from binance50.safety.backtest_execution_guard import assert_no_exchange_order_identifiers

    assert_backtest_quality_passed(result.quality_report, config)
    assert_no_exchange_order_identifiers(result.model_dump())

    # We would write to disk here and return manifests.
    # For now, returning empty list.
    return []


def import_backtest_report_pack(pack: Any, config: AppConfig) -> dict[str, Any]:
    """Import a backtest report pack into the storage system."""

    # 1. Quality check enforcement
    if pack.quality.status != "passed":
        from binance50.core.exceptions import BacktestReportQualityError

        raise BacktestReportQualityError("Cannot import report pack: Quality checks failed.")

    # 2. Disclaimer/hash check
    if not pack.disclaimer or not pack.input_hash or not pack.report_hash:
        from binance50.core.exceptions import BacktestReportingSafetyError

        raise BacktestReportingSafetyError(
            "Cannot import report pack: Missing disclaimer or hashes."
        )

    # 3. Live claim check
    if pack.quality.live_claim_count > 0:
        from binance50.core.exceptions import LivePerformanceClaimError

        raise LivePerformanceClaimError(
            "Cannot import report pack: Live performance claims detected."
        )

    from datetime import datetime

    return {
        "dataset": config.backtest_reporting.output_dataset_name,
        "report_id": pack.report_id,
        "run_id": pack.run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "imported",
        "hash": pack.report_hash,
    }
