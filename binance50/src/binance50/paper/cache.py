from pathlib import Path
from binance50.paper.models import PaperExecutionRunResult

def build_paper_cache_path(config, symbol, market_scope, interval, config_hash) -> Path:
    return Path(config.paper_execution.cache_dir) / f"{symbol}_{market_scope}_{interval}_{config_hash}.pkl"

def save_paper_execution_result(result: PaperExecutionRunResult, config) -> Path:
    path = Path(config.paper_execution.cache_dir) / f"{result.run_id}.pkl"
    # mock
    return path

def load_paper_execution_result(path: Path) -> PaperExecutionRunResult | None:
    return None

def list_paper_cache(config) -> list[Path]:
    return []

def clear_paper_cache(config, dry_run=True) -> dict:
    return {"cleared": 0, "dry_run": dry_run}
