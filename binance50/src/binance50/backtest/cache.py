from pathlib import Path

from .models import BacktestRunResult


def build_backtest_cache_path(
    config, symbol: str, market_scope: str, interval: str, config_hash: str
) -> Path:
    return (
        Path(config.backtest.cache_dir) / f"{symbol}_{market_scope}_{interval}_{config_hash}.json"
    )


def save_backtest_result(result: BacktestRunResult, config) -> Path:
    # Stub
    return Path("stub")


def load_backtest_result(path: Path) -> BacktestRunResult | None:
    return None


def list_backtest_cache(config) -> list[Path]:
    return []


def clear_backtest_cache(config, dry_run=True) -> dict:
    return {}
