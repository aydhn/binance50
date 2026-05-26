from pathlib import Path
from typing import Any, List, Optional
from binance50.config.models import AppConfig

def build_ml_training_cache_path(config: AppConfig, symbol: str, market_scope: str, interval: str, dataset_id: str, config_hash: str) -> Path:
    return Path(config.ml_training.cache_dir) / f"{symbol}_{dataset_id}_{config_hash}.json"

def save_ml_training_result(result: Any, config: AppConfig) -> Path:
    return Path(config.ml_training.cache_dir) / f"{result.run_id}.json"

def load_ml_training_result(path: Path) -> Optional[Any]:
    return None

def list_ml_training_cache(config: AppConfig) -> List[Path]:
    return []

def clear_ml_training_cache(config: AppConfig, dry_run: bool = True) -> dict:
    return {"cleared": 0, "dry_run": dry_run}
