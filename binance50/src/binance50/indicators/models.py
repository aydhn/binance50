from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import pandas as pd

from binance50.core.enums import MarketScope


class IndicatorGroup(StrEnum):
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    TRANSFORM = "transform"


class IndicatorBackend(StrEnum):
    NATIVE = "native"
    TALIB_OPTIONAL = "talib_optional"
    PANDAS_TA_OPTIONAL = "pandas_ta_optional"


class IndicatorOutputStatus(StrEnum):
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


class IndicatorWarmupStatus(StrEnum):
    WARMUP = "warmup"
    VALID = "valid"
    INSUFFICIENT_HISTORY = "insufficient_history"


@dataclass
class IndicatorSpec:
    name: str
    group: IndicatorGroup
    backend: IndicatorBackend
    parameters: dict[str, Any]
    input_columns: list[str]
    output_columns: list[str]
    min_lookback: int
    description: str = ""
    version: int = 1

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "name": self.name,
            "group": self.group.value,
            "backend": self.backend.value,
            "parameters": self.parameters,
            "input_columns": self.input_columns,
            "output_columns": self.output_columns,
            "min_lookback": self.min_lookback,
            "description": self.description,
            "version": self.version,
        }


@dataclass
class IndicatorRunRequest:
    symbol: str
    market_scope: MarketScope
    interval: str
    input_dataset_name: str
    backend: str
    indicator_specs: list[IndicatorSpec]
    start_time_ms: int | None = None
    end_time_ms: int | None = None
    include_input_columns: bool = True
    request_id: str = ""
    correlation_id: str = ""

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "market_scope": self.market_scope.value,
            "interval": self.interval,
            "input_dataset_name": self.input_dataset_name,
            "backend": self.backend,
            "indicator_specs_count": len(self.indicator_specs),
            "start_time_ms": self.start_time_ms,
            "end_time_ms": self.end_time_ms,
            "include_input_columns": self.include_input_columns,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
        }


@dataclass
class IndicatorFrameMetadata:
    symbol: str
    market_scope: MarketScope
    interval: str
    backend: str
    row_count: int
    input_row_count: int
    indicator_count: int
    start_open_time: int
    end_open_time: int
    max_lookback: int
    warmup_rows: int
    valid_rows: int
    generated_at_utc: str
    input_hash: str
    output_hash: str
    config_hash: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "market_scope": self.market_scope.value,
            "interval": self.interval,
            "backend": self.backend,
            "row_count": self.row_count,
            "input_row_count": self.input_row_count,
            "indicator_count": self.indicator_count,
            "start_open_time": self.start_open_time,
            "end_open_time": self.end_open_time,
            "max_lookback": self.max_lookback,
            "warmup_rows": self.warmup_rows,
            "valid_rows": self.valid_rows,
            "generated_at_utc": self.generated_at_utc,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "config_hash": self.config_hash,
            "warnings": self.warnings,
        }


@dataclass
class IndicatorColumnMetadata:
    column_name: str
    indicator_name: str
    group: IndicatorGroup
    parameters: dict[str, Any]
    min_lookback: int
    nan_count: int
    valid_count: int
    first_valid_open_time: int | None
    last_valid_open_time: int | None
    status: IndicatorOutputStatus
    warnings: list[str] = field(default_factory=list)

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "column_name": self.column_name,
            "indicator_name": self.indicator_name,
            "group": self.group.value,
            "parameters": self.parameters,
            "min_lookback": self.min_lookback,
            "nan_count": self.nan_count,
            "valid_count": self.valid_count,
            "first_valid_open_time": self.first_valid_open_time,
            "last_valid_open_time": self.last_valid_open_time,
            "status": self.status.value,
            "warnings": self.warnings,
        }


@dataclass
class IndicatorRunResult:
    request: IndicatorRunRequest
    output_df: pd.DataFrame
    metadata: IndicatorFrameMetadata
    quality_report: Any = None  # Will be defined in quality.py
    success: bool = True
    error: str | None = None

    def to_dict(self, redacted: bool = True) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(redacted),
            "metadata": self.metadata.to_dict(redacted) if self.metadata else None,
            "success": self.success,
            "error": self.error,
            "row_count": len(self.output_df) if self.output_df is not None else 0,
        }
