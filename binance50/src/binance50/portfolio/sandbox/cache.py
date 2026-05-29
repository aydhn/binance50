import json
from pathlib import Path

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioSelectionRunResult


def build_portfolio_sandbox_cache_path(
    config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str
) -> Path:
    cache_dir = Path(config.portfolio_sandbox.cache_dir)
    return cache_dir / f"portfolio_{symbol}_{market_scope}_{interval}_{config_hash}.json"


def save_portfolio_selection_result(result: PortfolioSelectionRunResult, config: AppConfig) -> Path:
    if not config.portfolio_sandbox.cache_enabled:
        return Path("/dev/null")

    req = result.request
    from binance50.portfolio.sandbox.reproducibility import compute_portfolio_config_hash

    config_hash = compute_portfolio_config_hash(config)

    path = build_portfolio_sandbox_cache_path(
        config, req.symbol or "all", req.market_scope or "all", req.interval or "all", config_hash
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(result.model_dump_json(indent=2))

    return path


def load_portfolio_selection_result(path: Path) -> PortfolioSelectionRunResult | None:
    if not path.exists():
        return None

    try:
        with open(path) as f:
            data = json.load(f)
        return PortfolioSelectionRunResult(**data)
    except Exception:
        return None


def list_portfolio_sandbox_cache(config: AppConfig) -> list[Path]:
    cache_dir = Path(config.portfolio_sandbox.cache_dir)
    if not cache_dir.exists():
        return []
    return list(cache_dir.glob("portfolio_*.json"))


def clear_portfolio_sandbox_cache(config: AppConfig, dry_run: bool = True) -> dict:
    files = list_portfolio_sandbox_cache(config)
    deleted = 0
    if not dry_run:
        for f in files:
            f.unlink()
            deleted += 1
    return {"files_found": len(files), "files_deleted": deleted, "dry_run": dry_run}
