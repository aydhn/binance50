import json
from pathlib import Path
from typing import Optional

from binance50.config.models import AppConfig
from .models import ExecutionSafetyRunResult


def build_execution_cache_path(config: AppConfig, symbol: str, market_scope: str, interval: str, config_hash: str) -> Path:
    cache_dir = Path(config.execution.cache_dir)
    return cache_dir / f"{symbol}_{market_scope}_{interval}_{config_hash}.json"

def save_execution_safety_result(result: ExecutionSafetyRunResult, config: AppConfig) -> Path:
    # A simple mock save, in real app it would dump dataclasses to json
    cache_dir = Path(config.execution.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"result_{result.run_id}.json"
    path.write_text(json.dumps({"run_id": result.run_id, "success": result.success}))
    return path

def load_execution_safety_result(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

def list_execution_cache(config: AppConfig) -> list[Path]:
    cache_dir = Path(config.execution.cache_dir)
    if not cache_dir.exists():
        return []
    return list(cache_dir.glob("*.json"))

def clear_execution_cache(config: AppConfig, dry_run: bool = True) -> dict:
    files = list_execution_cache(config)
    cleared = 0
    if not dry_run:
        for f in files:
            f.unlink()
            cleared += 1
    return {"found": len(files), "cleared": cleared, "dry_run": dry_run}
