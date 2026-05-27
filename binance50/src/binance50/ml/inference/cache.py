import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLInferenceRunResult

def build_ml_inference_cache_path(config: AppConfig, symbol: str, market_scope: str, interval: str, model_id: str, dataset_id: str, config_hash: str) -> Path:
    base = Path(config.ml_inference.cache_dir)
    return base / f"{symbol}_{market_scope}_{interval}_{model_id}_{dataset_id}_{config_hash}.json"

def save_ml_inference_result(result: MLInferenceRunResult, config: AppConfig) -> Path:
    # Dummy mock
    return Path(config.ml_inference.cache_dir) / "dummy.json"

def load_ml_inference_result(path: Path) -> Optional[MLInferenceRunResult]:
    # Dummy mock
    return None

def list_ml_inference_cache(config: AppConfig) -> List[Path]:
    base = Path(config.ml_inference.cache_dir)
    if not base.exists():
        return []
    return list(base.glob("*.json"))

def clear_ml_inference_cache(config: AppConfig, dry_run: bool = True) -> Dict[str, Any]:
    base = Path(config.ml_inference.cache_dir)
    if not base.exists():
        return {"status": "success", "cleared": 0, "dry_run": dry_run}

    count = len(list(base.glob("*.json")))
    if not dry_run:
        shutil.rmtree(base)
        base.mkdir(parents=True, exist_ok=True)

    return {"status": "success", "cleared": count, "dry_run": dry_run}
