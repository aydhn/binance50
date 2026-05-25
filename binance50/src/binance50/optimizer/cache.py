import json
from pathlib import Path

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult


def build_optimizer_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, method: str, config_hash: str
) -> Path:
    base = Path(config.optimizer.cache_dir)
    return base / f"{symbol}_{market_scope}_{interval}_{method}_{config_hash}.json"


def save_optimization_result(result: OptimizationRunResult, config: AppConfig) -> Path:
    if not config.optimizer.cache_enabled:
        return Path()
    path = Path(config.optimizer.cache_dir) / f"{result.run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(result.model_dump(), f)
    return path


def load_optimization_result(path: Path) -> OptimizationRunResult | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return OptimizationRunResult(**data)
    except Exception:
        return None


def list_optimizer_cache(config: AppConfig) -> list[Path]:
    base = Path(config.optimizer.cache_dir)
    if not base.exists():
        return []
    return list(base.glob("*.json"))


def clear_optimizer_cache(config: AppConfig, dry_run: bool = True) -> dict:
    paths = list_optimizer_cache(config)
    if not dry_run:
        for p in paths:
            p.unlink()
    return {"cleared": len(paths), "dry_run": dry_run}
