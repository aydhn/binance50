import hashlib
import json
import time
from pathlib import Path

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import OHLCVCacheError
from binance50.market_data.ohlcv_models import OHLCVFrameMetadata


def _sanitize_symbol(symbol: str) -> str:
    # Basic path traversal prevention
    return "".join(c for c in symbol if c.isalnum()).upper()


def _get_partitioned_path(
    config: AppConfig,
    base_dir: str,
    symbol: str,
    market_scope: MarketScope,
    interval: str,
    extension: str,
) -> Path:
    safe_symbol = _sanitize_symbol(symbol)
    path = Path(base_dir)

    if config.market_data.cache_partitioning.by_market_scope:
        path = path / market_scope.value

    if config.market_data.cache_partitioning.by_symbol:
        path = path / safe_symbol

    if config.market_data.cache_partitioning.by_interval:
        path = path / interval

    # Filename
    filename = f"{safe_symbol}_{interval}.{extension}"
    return path / filename


def build_ohlcv_cache_path(
    config: AppConfig, symbol: str, market_scope: MarketScope, interval: str
) -> Path:
    base_dir = config.market_data.cache_dir
    extension = config.market_data.cache_format
    return _get_partitioned_path(config, base_dir, symbol, market_scope, interval, extension)


def build_ohlcv_metadata_path(
    config: AppConfig, symbol: str, market_scope: MarketScope, interval: str
) -> Path:
    base_dir = config.market_data.metadata_dir
    return _get_partitioned_path(config, base_dir, symbol, market_scope, interval, "meta.json")


def ensure_cache_dirs(config: AppConfig) -> None:
    try:
        Path(config.market_data.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(config.market_data.metadata_dir).mkdir(parents=True, exist_ok=True)
        Path(config.market_data.export_dir).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OHLCVCacheError(f"Failed to create cache directories: {e}")


def compute_dataframe_hash(df: pd.DataFrame) -> str:
    if df.empty:
        return hashlib.sha256(b"empty").hexdigest()

    # Simple hash of the open_time and close values to represent state
    # We could hash the entire dataframe but this is faster and sufficient for basic integrity
    hash_str = pd.util.hash_pandas_object(df[["open_time", "close"]]).sum()
    return hashlib.sha256(str(hash_str).encode("utf-8")).hexdigest()


def write_metadata(metadata: OHLCVFrameMetadata, path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(metadata.dict_redacted(), f, indent=2)
    except Exception as e:
        raise OHLCVCacheError(f"Failed to write metadata to {path}: {e}")


def read_metadata(path: Path) -> OHLCVFrameMetadata | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return OHLCVFrameMetadata(**data)
    except Exception as e:
        raise OHLCVCacheError(f"Failed to read metadata from {path}: {e}")


def is_cache_available(
    config: AppConfig, symbol: str, market_scope: MarketScope, interval: str
) -> bool:
    cache_path = build_ohlcv_cache_path(config, symbol, market_scope, interval)
    meta_path = build_ohlcv_metadata_path(config, symbol, market_scope, interval)
    return cache_path.exists() and meta_path.exists()


def get_cache_age_seconds(path: Path) -> float | None:
    if not path.exists():
        return None
    return time.time() - path.stat().st_mtime
