from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import pandas as pd

from binance50.core.exceptions import StorageSchemaError


class DatasetKind(StrEnum):
    OHLCV = "ohlcv"
    INDICATORS = "indicators"
    INDICATOR_FEATURES_V2 = "indicator_features_v2"
    UNIVERSE_SELECTION = "universe_selection"
    STREAM_EVENTS = "stream_events"
    QUALITY_REPORTS = "quality_reports"
    FEATURE_STORE_FUTURE = "feature_store_future"
    BACKTEST_RESULTS_FUTURE = "backtest_results_future"

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
        timestamp_column="open_time"
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
            ColumnSchema("ask_qty", "float64")
        ],
        primary_keys=["selection_id", "symbol"],
        partition_columns=["market_scope"],
        timestamp_column="generated_at_ms"
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
            ColumnSchema("payload", "string", nullable=False), # JSON payload
        ],
        primary_keys=["event_id"],
        partition_columns=["stream_type", "symbol"],
        timestamp_column="event_time_ms"
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
            ColumnSchema("created_at_ms", "int64", nullable=False)
        ],
        primary_keys=["report_id"],
        partition_columns=["dataset_name"],
        timestamp_column="created_at_ms"
    )

def get_schema_registry() -> dict[str, DatasetSchema]:
    return {
        "ohlcv": get_ohlcv_schema(),
        "universe_selection": get_universe_selection_schema(),
        "stream_events": get_stream_events_schema(),
        "quality_reports": get_quality_reports_schema()
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
        "missing_required_columns": [c for c in missing if not next(s for s in schema.columns if s.name == c).nullable],
        "missing_optional_columns": [c for c in missing if next(s for s in schema.columns if s.name == c).nullable],
        "extra_columns": extra,
        "is_drifted": len(missing) > 0 or len(extra) > 0
    }

def schema_to_sql_columns(schema: DatasetSchema) -> list[str]:
    type_map = {
        "string": "TEXT",
        "int64": "INTEGER",
        "float64": "REAL",
        "bool": "INTEGER"
    }
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
        "bool": pa.bool_()
    }

    fields = []
    for c in schema.columns:
        fields.append(pa.field(c.name, type_map.get(c.dtype, pa.string()), nullable=c.nullable))

    return pa.schema(fields)


INDICATOR_V2_SCHEMA = DatasetSchema(
    dataset_name="indicator_features_v2",
    dataset_kind=DatasetKind.INDICATOR_FEATURES_V2,
    version=1, partition_columns=["market_scope", "symbol"],
    columns=[
        ColumnSchema("market_scope", "str", False, True, "Market scope (e.g. spot, usdm)"),
        ColumnSchema("symbol", "str", False, True, "Trading pair symbol"),
        ColumnSchema("interval", "str", False, True, "Timeframe interval"),
        ColumnSchema("open_time", "datetime64[ns, UTC]", False, True, "Candle open time"),
        ColumnSchema("feature_set_id", "str", False, True, "Unique ID of the feature set definition"),

        ColumnSchema("close_time", "datetime64[ns, UTC]", False, False, "Candle close time"),
        ColumnSchema("feature_config_hash", "str", False, False, "Hash of the indicator v2 config"),
        ColumnSchema("is_warmup", "bool", False, False, "Whether row is in warmup period"),
        ColumnSchema("generated_at_utc", "datetime64[ns, UTC]", False, False, "When features were computed"),
    ],
    dynamic_columns_allowed=True,
    dynamic_column_prefixes=["div_", "mtf_", "pat_", "trend_", "mom_", "vol_", "volu_", "tr_"],
    disallowed_column_names=["target", "label", "future_return", "next_close"]
)
