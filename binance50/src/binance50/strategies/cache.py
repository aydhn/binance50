import json
from pathlib import Path

from binance50.config.models import AppConfig
from binance50.strategies.models import StrategyRunResult


def build_strategy_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str
) -> Path:
    p = Path(config.strategies.cache_dir) / market_scope / symbol / interval
    p.mkdir(parents=True, exist_ok=True)
    return p / f"candidates_{config_hash}.jsonl"


def save_strategy_result(result: StrategyRunResult, config: AppConfig) -> Path:
    if not config.strategies.cache_enabled:
        return Path("")

    path = build_strategy_cache_path(
        config,
        result.request.symbol,
        result.request.market_scope,
        result.request.interval,
        result.metadata.config_hash,
    )

    with open(path, "w") as f:
        # Write metadata as first line
        f.write(json.dumps({"_type": "metadata", "data": result.metadata.model_dump()}) + "\n")
        # Write candidates
        for c in result.candidates:
            f.write(json.dumps({"_type": "candidate", "data": c.model_dump()}) + "\n")

    return path


def load_strategy_result(path: Path) -> StrategyRunResult | None:
    # Full load parsing not implemented here for brevity, returning None gracefully
    if not path.exists():
        return None
    return None


def list_strategy_cache(config: AppConfig) -> list[Path]:
    p = Path(config.strategies.cache_dir)
    if not p.exists():
        return []
    return list(p.rglob("*.jsonl"))


def clear_strategy_cache(config: AppConfig, dry_run: bool = True) -> dict[str, int]:
    files = list_strategy_cache(config)
    cleared = 0
    if not dry_run:
        for f in files:
            f.unlink()
            cleared += 1
    return {"files_found": len(files), "files_cleared": cleared, "dry_run": dry_run}
