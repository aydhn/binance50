from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.indicators.models import IndicatorFrameMetadata, IndicatorRunResult
from binance50.indicators.quality import IndicatorQualityReport
from binance50.indicators.registry import IndicatorRegistry


def build_indicator_run_summary(result: IndicatorRunResult) -> dict[str, Any]:
    if not result.success:
         return {"success": False, "error": result.error}

    return {
        "success": True,
        "symbol": result.metadata.symbol,
        "row_count": result.metadata.row_count,
        "indicator_count": result.metadata.indicator_count,
        "quality_status": result.quality_report.status if result.quality_report else "unknown",
        "warmup_rows": result.metadata.warmup_rows,
        "valid_rows": result.metadata.valid_rows
    }

def build_indicator_column_report(metadata: IndicatorFrameMetadata, quality: IndicatorQualityReport) -> dict[str, Any]:
    # Combines metadata and quality per column
    return {
        "total_columns": metadata.indicator_count,
        "nan_ratios": quality.nan_ratio_by_column,
        "inf_columns": quality.inf_columns,
        "issues_count": len(quality.issues)
    }

def build_indicator_registry_report(registry: IndicatorRegistry) -> dict[str, Any]:
    specs = registry.list_specs()

    group_counts = {}
    for s in specs:
        group_counts[s.group.value] = group_counts.get(s.group.value, 0) + 1

    return {
        "total_specs": len(specs),
        "group_counts": group_counts,
        "max_allowed": registry.config.indicators.max_indicator_specs_per_run
    }

def build_indicator_backend_report(config: AppConfig) -> dict[str, Any]:
    # Need to check instances
    from binance50.indicators.adapters.native import NativeIndicatorAdapter
    from binance50.indicators.adapters.pandas_ta_adapter import PandasTaIndicatorAdapter
    from binance50.indicators.adapters.talib_adapter import TalibIndicatorAdapter
    from binance50.indicators.registry import IndicatorRegistry

    reg = IndicatorRegistry(config)
    native = NativeIndicatorAdapter(reg)
    talib = TalibIndicatorAdapter()
    pta = PandasTaIndicatorAdapter()

    return {
        "native": native.availability_report(),
        "talib_optional": talib.availability_report(),
        "pandas_ta_optional": pta.availability_report()
    }

def build_indicator_health_report(config: AppConfig) -> dict[str, Any]:
    backends = build_indicator_backend_report(config)
    registry = IndicatorRegistry(config)
    reg_report = build_indicator_registry_report(registry)

    from binance50.safety.indicator_guard import build_indicator_safety_report
    safety = build_indicator_safety_report(config)

    return {
        "status": "healthy" if safety["status"] == "safe" else "warning",
        "backends": backends,
        "registry": reg_report,
        "safety": safety
    }

def format_indicator_preview(df: pd.DataFrame, rows: int = 5) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []

    # Just return top N and bottom N
    head = df.head(rows).to_dict(orient="records")
    tail = df.tail(rows).to_dict(orient="records")
    return {"head": head, "tail": tail}
