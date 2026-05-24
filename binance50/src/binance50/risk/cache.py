from pathlib import Path

from binance50.config.models import AppConfig
from binance50.risk.models import RiskRunResult


def build_risk_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str
) -> Path:
    base = Path(config.risk.cache_dir)
    return base / f"{symbol}_{market_scope}_{interval}_{config_hash}.json"


def save_risk_result(result: RiskRunResult, config: AppConfig) -> Path:
    if not config.risk.cache_enabled:
        return Path("/dev/null")
    path = build_risk_cache_path(
        config,
        result.request.symbol or "unknown",
        result.request.market_scope or "unknown",
        result.request.interval or "unknown",
        "hash_placeholder",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(result.model_dump_json())
    return path


def load_risk_result(path: Path) -> RiskRunResult | None:
    if not path.exists():
        return None
    with path.open("r") as f:
        return RiskRunResult.model_validate_json(f.read())


def list_risk_cache(config: AppConfig) -> list[Path]:
    base = Path(config.risk.cache_dir)
    if not base.exists():
        return []
    return list(base.glob("*.json"))


def clear_risk_cache(config: AppConfig, dry_run: bool = True) -> dict:
    files = list_risk_cache(config)
    cleared = 0
    if not dry_run:
        for f in files:
            f.unlink()
            cleared += 1
    return {"files_found": len(files), "cleared": cleared, "dry_run": dry_run}
