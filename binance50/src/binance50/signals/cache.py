import json
from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import SignalScoringResult


def build_signal_cache_path(config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str) -> Path:
    cache_dir = Path(config.signals.cache_dir)
    return cache_dir / f"{market_scope}_{symbol}_{interval}_{config_hash}.json"


def save_signal_result(result: SignalScoringResult, config: AppConfig) -> Path:
    if not config.signals.cache_enabled:
        return Path()

    cache_dir = Path(config.signals.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    path = build_signal_cache_path(
        config,
        result.request.symbol,
        result.request.market_scope,
        result.request.interval,
        result.metadata.config_hash
    )

    with open(path, "w") as f:
        # Convert to dict and handle datetimes properly, or rely on pydantic
        data = result.model_dump(mode="json")
        json.dump(data, f, indent=2)

    return path


def load_signal_result(path: Path) -> SignalScoringResult | None:
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return SignalScoringResult.model_validate(data)
    except Exception:
        return None


def list_signal_cache(config: AppConfig) -> list[Path]:
    cache_dir = Path(config.signals.cache_dir)
    if not cache_dir.exists():
        return []
    return list(cache_dir.glob("*.json"))


def clear_signal_cache(config: AppConfig, dry_run: bool = True) -> dict[str, Any]:
    files = list_signal_cache(config)
    deleted = 0
    if not dry_run:
        for f in files:
            f.unlink()
            deleted += 1

    return {
        "status": "success",
        "dry_run": dry_run,
        "files_found": len(files),
        "files_deleted": deleted
    }
