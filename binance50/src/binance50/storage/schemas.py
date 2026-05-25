from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import pandas as pd

from binance50.core.exceptions import StorageSchemaError


class DatasetKind(StrEnum):
    RISK_ASSESSMENTS = "risk_assessments"
    STRATEGY_CANDIDATES = "strategy_candidates"
    SCORED_SIGNAL_CANDIDATES = "scored_signal_candidates"
    MARKET_REGIMES = "market_regimes"
    OHLCV = "ohlcv"
    INDICATORS = "indicators"
    INDICATOR_FEATURES_V2 = "indicator_features_v2"
    UNIVERSE_SELECTION = "universe_selection"
    STREAM_EVENTS = "stream_events"
    QUALITY_REPORTS = "quality_reports"
    FEATURE_STORE_FUTURE = "feature_store_future"
    BACKTEST_RESULTS_FUTURE = "backtest_results_future"

    BACKTEST_REPORT_PACKS = "backtest_report_packs"
    BACKTEST_ADVANCED_METRICS = "backtest_advanced_metrics"
    BACKTEST_ROLLING_METRICS = "backtest_rolling_metrics"
    BACKTEST_PERIODIC_RETURNS = "backtest_periodic_returns"
    BACKTEST_BENCHMARK_COMPARISONS = "backtest_benchmark_comparisons"
    BACKTEST_DRAWDOWN_REPORTS = "backtest_drawdown_reports"
    BACKTEST_TRADE_DISTRIBUTION_REPORTS = "backtest_trade_distribution_reports"


@dataclass
class ColumnSchema:
    name: str
    dtype: str
    nullable: bool = True
    is_primary_key: bool = False
    description: str = ""


@dataclass
class DatasetSchema:
    dataset_name: str
    dataset_kind: DatasetKind
    version: int
    columns: list[ColumnSchema]
    primary_keys: list[str] = field(default_factory=list)
    partition_columns: list[str] = field(default_factory=list)
    timestamp_column: str | None = None
    created_at_utc: str = ""
    dynamic_columns_allowed: bool = False
    dynamic_column_prefixes: list[str] = field(default_factory=list)
    disallowed_column_names: list[str] = field(default_factory=list)


def get_ohlcv_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ohlcv",
        dataset_kind=DatasetKind.OHLCV,
        version=1,
        columns=[
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("open", "float64", nullable=False),
            ColumnSchema("high", "float64", nullable=False),
            ColumnSchema("low", "float64", nullable=False),
            ColumnSchema("close", "float64", nullable=False),
            ColumnSchema("volume", "float64", nullable=False),
            ColumnSchema("close_time", "int64", nullable=False),
            ColumnSchema("quote_asset_volume", "float64", nullable=False),
            ColumnSchema("number_of_trades", "int64", nullable=False),
            ColumnSchema("taker_buy_base_asset_volume", "float64", nullable=False),
            ColumnSchema("taker_buy_quote_asset_volume", "float64", nullable=False),
        ],
        primary_keys=["market_scope", "symbol", "interval", "open_time"],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
    )


def get_universe_selection_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="universe_selection",
        dataset_kind=DatasetKind.UNIVERSE_SELECTION,
        version=1,
        columns=[
            ColumnSchema("selection_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("market_scope", "string", nullable=False),
            ColumnSchema("generated_at_ms", "int64", nullable=False),
            ColumnSchema("base_asset", "string", nullable=False),
            ColumnSchema("quote_asset", "string", nullable=False),
            ColumnSchema("volume_24h", "float64"),
            ColumnSchema("quote_volume_24h", "float64"),
            ColumnSchema("trade_count_24h", "int64"),
            ColumnSchema("spread_bps", "float64"),
            ColumnSchema("bid_qty", "float64"),
            ColumnSchema("ask_qty", "float64"),
        ],
        primary_keys=["selection_id", "symbol"],
        partition_columns=["market_scope"],
        timestamp_column="generated_at_ms",
    )


def get_stream_events_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="stream_events",
        dataset_kind=DatasetKind.STREAM_EVENTS,
        version=1,
        columns=[
            ColumnSchema("event_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("stream_type", "string", nullable=False),
            ColumnSchema("symbol", "string", nullable=False),
            ColumnSchema("event_time_ms", "int64", nullable=False),
            ColumnSchema("payload", "string", nullable=False),  # JSON payload
        ],
        primary_keys=["event_id"],
        partition_columns=["stream_type", "symbol"],
        timestamp_column="event_time_ms",
    )


def get_quality_reports_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="quality_reports",
        dataset_kind=DatasetKind.QUALITY_REPORTS,
        version=1,
        columns=[
            ColumnSchema("report_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("dataset_name", "string", nullable=False),
            ColumnSchema("symbol", "string", nullable=False),
            ColumnSchema("interval", "string", nullable=False),
            ColumnSchema("issue_type", "string", nullable=False),
            ColumnSchema("severity", "string", nullable=False),
            ColumnSchema("issue_count", "int64", nullable=False),
            ColumnSchema("created_at_ms", "int64", nullable=False),
        ],
        primary_keys=["report_id"],
        partition_columns=["dataset_name"],
        timestamp_column="created_at_ms",
    )


def get_strategy_candidates_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="strategy_candidates",
        dataset_kind=DatasetKind.STRATEGY_CANDIDATES,
        version=1,
        columns=[
            ColumnSchema("candidate_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("plugin_name", "string", nullable=False, is_primary_key=True),
            ColumnSchema("close_time", "int64", nullable=True),
            ColumnSchema("plugin_type", "string", nullable=False),
            ColumnSchema("direction", "string", nullable=False),
            ColumnSchema("strength", "string", nullable=False),
            ColumnSchema("confidence", "float64", nullable=False),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("intent", "string", nullable=False),
            ColumnSchema("expiry_bars", "int64", nullable=False),
            ColumnSchema("explanation_summary", "string", nullable=False),
            ColumnSchema("used_features_json", "string", nullable=False),
            ColumnSchema("rejection_reasons_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
            ColumnSchema("created_at_utc", "int64", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
        ],
        primary_keys=[
            "market_scope",
            "symbol",
            "interval",
            "open_time",
            "plugin_name",
            "candidate_id",
        ],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
        disallowed_column_names=[
            "order_id",
            "quantity",
            "leverage",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
        ],
    )


def get_scored_signal_candidates_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="scored_signal_candidates",
        dataset_kind=DatasetKind.SCORED_SIGNAL_CANDIDATES,
        version=1,
        columns=[
            ColumnSchema("scored_signal_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("source_candidate_id", "string", nullable=False),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("close_time", "int64", nullable=True),
            ColumnSchema("direction", "string", nullable=False),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("intent", "string", nullable=False),
            ColumnSchema("score", "float64", nullable=False),
            ColumnSchema("score_tier", "string", nullable=False),
            ColumnSchema("confidence", "float64", nullable=False),
            ColumnSchema("plugin_name", "string", nullable=False),
            ColumnSchema("plugin_type", "string", nullable=False),
            ColumnSchema("strategy_strength", "string", nullable=False),
            ColumnSchema("confluence_group_id", "string", nullable=True),
            ColumnSchema("conflicted", "bool", nullable=False),
            ColumnSchema("expired", "bool", nullable=False),
            ColumnSchema("conflict_reasons_json", "string", nullable=False),
            ColumnSchema("score_breakdown_json", "string", nullable=False),
            ColumnSchema("explanation_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
            ColumnSchema("created_at_utc", "int64", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
        ],
        primary_keys=[
            "market_scope",
            "symbol",
            "interval",
            "open_time",
            "scored_signal_id",
        ],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
        disallowed_column_names=[
            "order_id",
            "quantity",
            "qty",
            "leverage",
            "margin",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "order_type",
            "position_side",
        ],
    )


def get_market_regimes_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="market_regimes",
        dataset_kind=DatasetKind.MARKET_REGIMES,
        version=1,
        columns=[
            ColumnSchema("regime_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("close_time", "int64", nullable=True),
            ColumnSchema("regime", "string", nullable=False),
            ColumnSchema("family", "string", nullable=False),
            ColumnSchema("method", "string", nullable=False),
            ColumnSchema("confidence", "float64", nullable=False),
            ColumnSchema("stability_score", "float64", nullable=True),
            ColumnSchema("risk_context", "string", nullable=False),
            ColumnSchema("is_transition", "bool", nullable=False),
            ColumnSchema("explanation_json", "string", nullable=False),
            ColumnSchema("feature_snapshot_json", "string", nullable=False),
            ColumnSchema("warnings_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
            ColumnSchema("created_at_utc", "int64", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
        ],
        primary_keys=[
            "market_scope",
            "symbol",
            "interval",
            "open_time",
            "regime_id",
        ],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
        disallowed_column_names=[
            "order_id",
            "quantity",
            "leverage",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
        ],
    )


def get_risk_assessments_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="risk_assessments",
        dataset_kind=DatasetKind.RISK_ASSESSMENTS,
        version=1,
        columns=[
            ColumnSchema("assessment_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("source_scored_signal_id", "string", nullable=False),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("close_time", "int64", nullable=True),
            ColumnSchema("direction", "string", nullable=False),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("intent", "string", nullable=False),
            ColumnSchema("final_risk_score", "float64", nullable=False),
            ColumnSchema("risk_tier", "string", nullable=False),
            ColumnSchema("approved", "bool", nullable=False),
            ColumnSchema("blocked", "bool", nullable=False),
            ColumnSchema("needs_review", "bool", nullable=False),
            ColumnSchema("explanation_json", "string", nullable=False),
            ColumnSchema("breakdown_json", "string", nullable=False),
            ColumnSchema("regime_context_json", "string", nullable=False),
            ColumnSchema("signal_snapshot_json", "string", nullable=False),
            ColumnSchema("hypothetical_notional_usdt", "float64", nullable=True),
            ColumnSchema("hypothetical_risk_pct", "float64", nullable=True),
            ColumnSchema("metadata_json", "string", nullable=False),
            ColumnSchema("created_at_utc", "int64", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
        ],
        primary_keys=[
            "market_scope",
            "symbol",
            "interval",
            "open_time",
            "assessment_id",
        ],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
        disallowed_column_names=[
            "order_id",
            "quantity",
            "qty",
            "leverage_to_set",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "order_type",
            "side",
        ],
    )


def get_optimization_runs_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="optimization_runs",
        dataset_kind=DatasetKind.OPTIMIZATION_RUNS,
        version=1,
        columns=[
            ColumnSchema("run_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("symbol", "string", nullable=False),
            ColumnSchema("market_scope", "string", nullable=False),
            ColumnSchema("interval", "string", nullable=False),
            ColumnSchema("method", "string", nullable=False),
            ColumnSchema("trial_count", "int64", nullable=False),
            ColumnSchema("completed_trial_count", "int64", nullable=False),
            ColumnSchema("failed_trial_count", "int64", nullable=False),
            ColumnSchema("rejected_trial_count", "int64", nullable=False),
            ColumnSchema("input_hash", "string", nullable=False),
            ColumnSchema("search_space_hash", "string", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
            ColumnSchema("output_hash", "string", nullable=False),
            ColumnSchema("generated_at_utc", "int64", nullable=False),
            ColumnSchema("warnings_json", "string", nullable=False),
            ColumnSchema("best_trial_id", "string", nullable=True),
        ],
        primary_keys=["run_id"],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="generated_at_utc",
        disallowed_column_names=[
            "api_key",
            "secret",
            "signature",
            "order_id",
            "client_order_id",
            "exchange_order_id",
            "live_order",
            "testnet_order",
            "paper_order",
            "real_order",
            "execution_gateway",
        ],
    )


def get_optimization_trials_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="optimization_trials",
        dataset_kind=DatasetKind.OPTIMIZATION_TRIALS,
        version=1,
        columns=[
            ColumnSchema("trial_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("run_id", "string", nullable=False),
            ColumnSchema("method", "string", nullable=False),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("objective_score", "float64", nullable=True),
            ColumnSchema("robust_score", "float64", nullable=True),
            ColumnSchema("started_at_utc", "int64", nullable=False),
            ColumnSchema("finished_at_utc", "int64", nullable=True),
            ColumnSchema("error_message", "string", nullable=True),
            ColumnSchema("parameter_set_json", "string", nullable=False),
            ColumnSchema("train_result_json", "string", nullable=True),
            ColumnSchema("validation_result_json", "string", nullable=True),
            ColumnSchema("test_result_json", "string", nullable=True),
            ColumnSchema("overfit_report_json", "string", nullable=True),
            ColumnSchema("robustness_report_json", "string", nullable=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["trial_id"],
        partition_columns=["run_id"],
        timestamp_column="started_at_utc",
        disallowed_column_names=[
            "api_key",
            "secret",
            "signature",
            "order_id",
            "client_order_id",
            "exchange_order_id",
            "live_order",
            "testnet_order",
            "paper_order",
            "real_order",
            "execution_gateway",
        ],
    )


def get_optimization_overfit_reports_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="optimization_overfit_reports",
        dataset_kind=DatasetKind.OPTIMIZATION_OVERFIT_REPORTS,
        version=1,
        columns=[
            ColumnSchema("trial_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("train_score", "float64", nullable=True),
            ColumnSchema("validation_score", "float64", nullable=True),
            ColumnSchema("test_score", "float64", nullable=True),
            ColumnSchema("train_validation_gap", "float64", nullable=True),
            ColumnSchema("train_validation_sharpe_gap", "float64", nullable=True),
            ColumnSchema("validation_test_gap", "float64", nullable=True),
            ColumnSchema("parameter_complexity", "float64", nullable=False),
            ColumnSchema("low_trade_count_penalty", "float64", nullable=False),
            ColumnSchema("high_drawdown_penalty", "float64", nullable=False),
            ColumnSchema("cost_drag_penalty", "float64", nullable=False),
            ColumnSchema("overfit_risk_level", "string", nullable=False),
            ColumnSchema("rejected", "bool", nullable=False),
            ColumnSchema("warnings_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["trial_id"],
        disallowed_column_names=[
            "api_key",
            "secret",
            "signature",
            "order_id",
            "client_order_id",
            "exchange_order_id",
            "live_order",
            "testnet_order",
            "paper_order",
            "real_order",
            "execution_gateway",
        ],
    )


def get_optimization_robustness_reports_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="optimization_robustness_reports",
        dataset_kind=DatasetKind.OPTIMIZATION_ROBUSTNESS_REPORTS,
        version=1,
        columns=[
            ColumnSchema("trial_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("rank_stability_score", "float64", nullable=True),
            ColumnSchema("metric_dispersion_score", "float64", nullable=True),
            ColumnSchema("neighbor_sensitivity_score", "float64", nullable=True),
            ColumnSchema("robustness_score", "float64", nullable=True),
            ColumnSchema("fragile_optimum_warning", "bool", nullable=False),
            ColumnSchema("comparable_neighbor_count", "int64", nullable=False),
            ColumnSchema("warnings_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["trial_id"],
        disallowed_column_names=[
            "api_key",
            "secret",
            "signature",
            "order_id",
            "client_order_id",
            "exchange_order_id",
            "live_order",
            "testnet_order",
            "paper_order",
            "real_order",
            "execution_gateway",
        ],
    )


def get_optimization_search_spaces_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="optimization_search_spaces",
        dataset_kind=DatasetKind.OPTIMIZATION_SEARCH_SPACES,
        version=1,
        columns=[
            ColumnSchema("search_space_hash", "string", nullable=False, is_primary_key=True),
            ColumnSchema("specs_json", "string", nullable=False),
            ColumnSchema("total_parameters", "int64", nullable=False),
            ColumnSchema("estimated_combinations", "int64", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["search_space_hash"],
        disallowed_column_names=[
            "api_key",
            "secret",
            "signature",
            "order_id",
            "client_order_id",
            "exchange_order_id",
            "live_order",
            "testnet_order",
            "paper_order",
            "real_order",
            "execution_gateway",
        ],
    )


def get_schema_registry() -> dict[str, DatasetSchema]:
    return {
        "ohlcv": get_ohlcv_schema(),
        "universe_selection": get_universe_selection_schema(),
        "stream_events": get_stream_events_schema(),
        "quality_reports": get_quality_reports_schema(),
        "strategy_candidates": get_strategy_candidates_schema(),
        "scored_signal_candidates": get_scored_signal_candidates_schema(),
        "market_regimes": get_market_regimes_schema(),
        "risk_assessments": get_risk_assessments_schema(),
        "optimization_runs": get_optimization_runs_schema(),
        "optimization_trials": get_optimization_trials_schema(),
        "optimization_overfit_reports": get_optimization_overfit_reports_schema(),
        "optimization_robustness_reports": get_optimization_robustness_reports_schema(),
        "optimization_search_spaces": get_optimization_search_spaces_schema(),
    }


def validate_dataframe_schema(df: pd.DataFrame, schema: DatasetSchema) -> None:
    drift = detect_schema_drift(df, schema)
    if drift["missing_required_columns"]:
        raise StorageSchemaError(f"Missing required columns: {drift['missing_required_columns']}")
    if drift["extra_columns"]:
        # We can either warn or error based on config, but core validation fails here
        raise StorageSchemaError(f"Extra columns detected: {drift['extra_columns']}")


def detect_schema_drift(df: pd.DataFrame, schema: DatasetSchema) -> dict[str, Any]:
    expected_cols = {c.name for c in schema.columns}
    actual_cols = set(df.columns)

    missing = list(expected_cols - actual_cols)
    extra = list(actual_cols - expected_cols)

    if schema.dynamic_columns_allowed:
        allowed_extra = []
        for col in extra:
            if any(col.startswith(p) for p in schema.dynamic_column_prefixes):
                allowed_extra.append(col)

        # Check disallowed
        for col in extra:
            if col in schema.disallowed_column_names:
                raise StorageSchemaError(f"Disallowed column name detected: {col}")

        extra = [c for c in extra if c not in allowed_extra]

    # Check for secret-like column names
    secret_words = ["api_key", "secret", "token", "signature", "password"]
    for col in actual_cols:
        col_lower = col.lower()
        if any(secret in col_lower for secret in secret_words):
            raise StorageSchemaError(f"Secret-like column name detected: {col}")

    # Note: we could do deeper dtype checks here, but leaving simple for now

    return {
        "missing_required_columns": [
            c for c in missing if not next(s for s in schema.columns if s.name == c).nullable
        ],
        "missing_optional_columns": [
            c for c in missing if next(s for s in schema.columns if s.name == c).nullable
        ],
        "extra_columns": extra,
        "is_drifted": len(missing) > 0 or len(extra) > 0,
    }


def schema_to_sql_columns(schema: DatasetSchema) -> list[str]:
    type_map = {"string": "TEXT", "int64": "INTEGER", "float64": "REAL", "bool": "INTEGER"}
    sql_cols = []
    for c in schema.columns:
        sql_type = type_map.get(c.dtype, "TEXT")
        nullable = "" if c.nullable else " NOT NULL"
        pk = " PRIMARY KEY" if c.is_primary_key and len(schema.primary_keys) == 1 else ""
        sql_cols.append(f"{c.name} {sql_type}{nullable}{pk}")

    if len(schema.primary_keys) > 1:
        sql_cols.append(f"PRIMARY KEY ({', '.join(schema.primary_keys)})")

    return sql_cols


def schema_to_pyarrow(schema: DatasetSchema) -> Any:
    import pyarrow as pa

    type_map = {
        "string": pa.string(),
        "int64": pa.int64(),
        "float64": pa.float64(),
        "bool": pa.bool_(),
    }

    fields = []
    for c in schema.columns:
        fields.append(pa.field(c.name, type_map.get(c.dtype, pa.string()), nullable=c.nullable))

    return pa.schema(fields)


INDICATOR_V2_SCHEMA = DatasetSchema(
    dataset_name="indicator_features_v2",
    dataset_kind=DatasetKind.INDICATOR_FEATURES_V2,
    version=1,
    partition_columns=["market_scope", "symbol"],
    columns=[
        ColumnSchema("market_scope", "str", False, True, "Market scope (e.g. spot, usdm)"),
        ColumnSchema("symbol", "str", False, True, "Trading pair symbol"),
        ColumnSchema("interval", "str", False, True, "Timeframe interval"),
        ColumnSchema("open_time", "datetime64[ns, UTC]", False, True, "Candle open time"),
        ColumnSchema(
            "feature_set_id", "str", False, True, "Unique ID of the feature set definition"
        ),
        ColumnSchema("close_time", "datetime64[ns, UTC]", False, False, "Candle close time"),
        ColumnSchema("feature_config_hash", "str", False, False, "Hash of the indicator v2 config"),
        ColumnSchema("is_warmup", "bool", False, False, "Whether row is in warmup period"),
        ColumnSchema(
            "generated_at_utc", "datetime64[ns, UTC]", False, False, "When features were computed"
        ),
    ],
    dynamic_columns_allowed=True,
    dynamic_column_prefixes=["div_", "mtf_", "pat_", "trend_", "mom_", "vol_", "volu_", "tr_"],
    disallowed_column_names=["target", "label", "future_return", "next_close"],
)
