import json
from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardRunResult


def build_walkforward_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, mode: str, config_hash: str
) -> Path:
    cache_dir = Path(config.walkforward.cache_dir)
    return cache_dir / f"{symbol}_{market_scope}_{interval}_{mode}_{config_hash}.json"


def save_walkforward_result(result: WalkForwardRunResult, config: AppConfig) -> Path:
    if not config.walkforward.cache_enabled:
        return Path("")

    req = result.request
    meta = getattr(result, "metadata", {})
    config_hash = meta.get("config_hash", "unknown")

    path = build_walkforward_cache_path(
        config, req.symbol, req.market_scope, req.interval, req.mode.value, config_hash
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclude dataframes when dumping to json
    dump = result.model_dump(exclude={"stitched_oos_equity"})

    with open(path, "w") as f:
        json.dump(dump, f)

    return path


def load_walkforward_result(path: Path) -> WalkForwardRunResult | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return WalkForwardRunResult(**data)
    except Exception:
        return None


def list_walkforward_cache(config: AppConfig) -> list[Path]:
    cache_dir = Path(config.walkforward.cache_dir)
    if not cache_dir.exists():
        return []
    return list(cache_dir.glob("*.json"))


def clear_walkforward_cache(config: AppConfig, dry_run: bool = True) -> dict[str, Any]:
    cache_dir = Path(config.walkforward.cache_dir)
    if not cache_dir.exists():
        return {"cleared": 0, "dry_run": dry_run}

    files = list(cache_dir.glob("*.json"))
    if not dry_run:
        for f in files:
            f.unlink()

    return {"cleared": len(files), "dry_run": dry_run}
