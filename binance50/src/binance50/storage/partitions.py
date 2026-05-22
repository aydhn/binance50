from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.storage.paths import build_dataset_partition_path


@dataclass(frozen=True)
class PartitionSpec:
    dataset_name: str
    market_scope: str | None
    symbol: str | None
    interval: str | None
    year: str | None
    month: str | None
    day: str | None
    path: Path

def build_partition_spec(row_or_metadata: dict[str, Any], config: AppConfig, dataset_name: str) -> PartitionSpec:
    ms = str(row_or_metadata.get("market_scope", "")) if row_or_metadata.get("market_scope") else None
    sym = str(row_or_metadata.get("symbol", "")) if row_or_metadata.get("symbol") else None
    inv = str(row_or_metadata.get("interval", "")) if row_or_metadata.get("interval") else None

    y = None
    m = None
    d = None

    # Try to derive date from various timestamp fields
    ts = None
    for field in ["open_time", "generated_at_ms", "event_time_ms"]:
        if field in row_or_metadata:
             ts = row_or_metadata[field]
             break

    if ts is not None:
         dt = datetime.fromtimestamp(int(ts) / 1000, tz=UTC)
         y = str(dt.year)
         m = str(dt.month).zfill(2)
         d = str(dt.day).zfill(2)

    path = build_dataset_partition_path(config, dataset_name, ms, sym, inv, y, m, d)

    return PartitionSpec(
        dataset_name=dataset_name,
        market_scope=ms,
        symbol=sym,
        interval=inv,
        year=y,
        month=m,
        day=d,
        path=path
    )

def extract_partition_values_from_path(path: Path) -> dict[str, str]:
    values = {}
    for part in path.parts:
        if "=" in part:
            k, v = part.split("=", 1)
            values[k] = v
    return values

def group_dataframe_by_partitions(df: pd.DataFrame, config: AppConfig, dataset_name: str) -> dict[PartitionSpec, pd.DataFrame]:
    groups = {}
    # Find partition columns present in DataFrame
    p_cols = []
    for col in ["market_scope", "symbol", "interval"]:
        if config.storage.partitioning.__dict__.get(f"by_{col}") and col in df.columns:
            p_cols.append(col)

    # For time partitioning, we might need to derive temporary columns
    derive_time = config.storage.partitioning.by_year or config.storage.partitioning.by_month or config.storage.partitioning.by_day
    temp_cols = []
    if derive_time:
        ts_col = next((c for c in ["open_time", "generated_at_ms", "event_time_ms"] if c in df.columns), None)
        if ts_col:
            dt_series = pd.to_datetime(df[ts_col], unit='ms', utc=True)
            if config.storage.partitioning.by_year:
                df['_temp_year'] = dt_series.dt.year.astype(str)
                p_cols.append('_temp_year')
                temp_cols.append('_temp_year')
            if config.storage.partitioning.by_month:
                df['_temp_month'] = dt_series.dt.month.astype(str).str.zfill(2)
                p_cols.append('_temp_month')
                temp_cols.append('_temp_month')
            if config.storage.partitioning.by_day:
                df['_temp_day'] = dt_series.dt.day.astype(str).str.zfill(2)
                p_cols.append('_temp_day')
                temp_cols.append('_temp_day')

    if not p_cols:
         # No partitioning needed based on config and data
         spec = build_partition_spec({}, config, dataset_name)
         groups[spec] = df
    else:
        for name, group in df.groupby(p_cols):
             # name can be tuple or scalar
             vals = {}
             if isinstance(name, tuple):
                 for i, c in enumerate(p_cols):
                     vals[c.replace('_temp_', '')] = name[i]
             else:
                 vals[p_cols[0].replace('_temp_', '')] = name

             spec = build_partition_spec(vals, config, dataset_name)
             groups[spec] = group.drop(columns=temp_cols) # Don't save temp columns

    # Clean up temp columns if we added them
    if temp_cols:
        df.drop(columns=temp_cols, inplace=True)

    return groups

def partition_filter_to_pyarrow(filters: dict[str, Any]) -> list[tuple]:
    """Convert dict of exact matches to pyarrow DNF filters"""
    pa_filters = []
    for k, v in filters.items():
        if isinstance(v, list):
             # Simple IN clause equivalent using multiple ORs is complex in PA DNF,
             # but PA dataset.dataset supports [('col', 'in', ['A', 'B'])]
             pa_filters.append((k, "in", v))
        else:
             pa_filters.append((k, "==", v))
    return pa_filters
