from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.ml.blending.models import MLBlendingRunResult


def build_ml_blending_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str
) -> Path:
    return (
        Path(config.ml_blending.cache_dir)
        / f"{symbol}_{market_scope}_{interval}_{config_hash}.json"
    )


def save_ml_blending_result(result: MLBlendingRunResult, config: AppConfig) -> Path:
    return Path("dummy.json")


def load_ml_blending_result(path: Path) -> MLBlendingRunResult | None:
    return None


def list_ml_blending_cache(config: AppConfig) -> list[Path]:
    return []


def clear_ml_blending_cache(config: AppConfig, dry_run: bool = True) -> dict[str, Any]:
    return {"cleared": 0}
