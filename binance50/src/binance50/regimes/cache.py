from pathlib import Path

from binance50.config.models import AppConfig
from binance50.regimes.models import RegimeRunResult


def build_regime_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, method: str, config_hash: str
) -> Path:
    return (
        Path(config.regimes.cache_dir)
        / f"{market_scope}_{symbol}_{interval}_{method}_{config_hash}.jsonl"
    )


def save_regime_result(result: RegimeRunResult, config: AppConfig) -> Path:
    path = build_regime_cache_path(
        config,
        result.metadata.symbol,
        result.metadata.market_scope,
        result.metadata.interval,
        result.metadata.method,
        result.metadata.config_hash,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    # Placeholder for actual JSONL write
    path.touch()
    return path


def load_regime_result(path: Path) -> RegimeRunResult | None:
    if not path.exists():
        return None
    # Placeholder
    return None


def list_regime_cache(config: AppConfig) -> list[Path]:
    p = Path(config.regimes.cache_dir)
    if not p.exists():
        return []
    return list(p.glob("*.jsonl"))


def clear_regime_cache(config: AppConfig, dry_run: bool = True) -> dict:
    files = list_regime_cache(config)
    if not dry_run:
        for f in files:
            f.unlink()
    return {"deleted": len(files) if not dry_run else 0, "dry_run": dry_run}
