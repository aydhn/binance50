import json
from pathlib import Path
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorCacheError
from binance50.indicators.models import (
    IndicatorFrameMetadata,
    IndicatorRunRequest,
    IndicatorRunResult,
)


def build_indicator_cache_path(config: AppConfig, symbol: str, market_scope: str, interval: str, backend: str, config_hash: str) -> Path:
    cache_dir = Path(config.indicators.cache_dir)
    safe_symbol = "".join(c for c in symbol if c.isalnum()).lower()
    safe_scope = "".join(c for c in market_scope if c.isalnum()).lower()
    safe_interval = "".join(c for c in interval if c.isalnum()).lower()
    safe_backend = "".join(c for c in backend if c.isalnum()).lower()

    filename = f"{safe_scope}_{safe_symbol}_{safe_interval}_{safe_backend}_{config_hash}.parquet"
    return cache_dir / filename

def save_indicator_result(result: IndicatorRunResult, config: AppConfig) -> Path:
    if not config.indicators.cache_enabled:
        return Path("")

    if not result.success or result.output_df is None:
        raise IndicatorCacheError("Cannot cache failed or empty result")

    meta = result.metadata
    p = build_indicator_cache_path(config, meta.symbol, meta.market_scope.value, meta.interval, meta.backend, meta.config_hash)

    p.parent.mkdir(parents=True, exist_ok=True)

    # Save parquet
    result.output_df.to_parquet(p)

    # Save metadata
    meta_path = p.with_suffix(".json")
    with open(meta_path, "w") as f:
        json.dump(result.to_dict(redacted=True), f, indent=2)

    return p

def load_indicator_result(path: Path) -> IndicatorRunResult | None:
    if not path.exists():
        return None

    meta_path = path.with_suffix(".json")
    if not meta_path.exists():
        return None

    try:
        df = pd.read_parquet(path)
        with open(meta_path) as f:
             data = json.load(f)

        # Just reconstruct basic structure for loaded cache
        # Proper deserialization would map the dictionaries back to models
        # For Phase 11 cache loads, we'll return raw for now or minimal result

        # Let's reconstruct request and metadata partially if possible, or just pass dict
        from binance50.core.enums import MarketScope
        req_d = data["request"]
        req = IndicatorRunRequest(
            req_d["symbol"],
            MarketScope(req_d["market_scope"]),
            req_d["interval"],
            req_d["input_dataset_name"],
            req_d["backend"],
            [] # specs omitted
        )

        meta_d = data["metadata"]
        meta = IndicatorFrameMetadata(
            meta_d["symbol"],
            MarketScope(meta_d["market_scope"]),
            meta_d["interval"],
            meta_d["backend"],
            meta_d["row_count"],
            meta_d["input_row_count"],
            meta_d["indicator_count"],
            meta_d["start_open_time"],
            meta_d["end_open_time"],
            meta_d["max_lookback"],
            meta_d["warmup_rows"],
            meta_d["valid_rows"],
            meta_d["generated_at_utc"],
            meta_d["input_hash"],
            meta_d["output_hash"],
            meta_d["config_hash"]
        )

        res = IndicatorRunResult(req, df, meta)
        return res
    except Exception:
        return None

def list_indicator_cache(config: AppConfig) -> list[Path]:
    cache_dir = Path(config.indicators.cache_dir)
    if not cache_dir.exists():
        return []

    return list(cache_dir.glob("*.parquet"))

def clear_indicator_cache(config: AppConfig, dry_run: bool = True) -> dict[str, Any]:
    paths = list_indicator_cache(config)
    cleared = []

    for p in paths:
        if not dry_run:
            p.unlink()
            meta_path = p.with_suffix(".json")
            if meta_path.exists():
                meta_path.unlink()
        cleared.append(str(p))

    return {
        "dry_run": dry_run,
        "cleared_count": len(cleared),
        "files": cleared
    }
