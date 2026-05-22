import json
from datetime import UTC, datetime
from pathlib import Path

from binance50.config.models import UniverseConfig
from binance50.universe.models import UniverseSelectionResult


class UniverseCache:
    def __init__(self, config: UniverseConfig):
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file_path(self, market_scope_str: str) -> Path:
        return self.cache_dir / f"universe_selection_{market_scope_str}.json"

    def save_selection(self, result: UniverseSelectionResult, market_scope_str: str) -> Path:
        if not self.config.cache_enabled:
            return self._get_cache_file_path(market_scope_str)

        path = self._get_cache_file_path(market_scope_str)
        # mode='json' handles datetimes
        data = result.model_dump(mode="json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def load_latest_selection(self, market_scope_str: str) -> UniverseSelectionResult | None:
        if not self.config.cache_enabled:
            return None

        path = self._get_cache_file_path(market_scope_str)
        if not path.exists():
            return None

        if not self.is_cache_fresh(path, self.config.cache_ttl_seconds):
            return None

        try:
            with open(path) as f:
                data = json.load(f)
            return UniverseSelectionResult(**data)
        except Exception:
            return None

    def is_cache_fresh(self, path: Path, ttl_seconds: int) -> bool:
        if not path.exists():
            return False
        mtime = path.stat().st_mtime
        now = datetime.now(UTC).timestamp()
        return (now - mtime) <= ttl_seconds

    def list_cached_selections(self) -> list[Path]:
        if not self.cache_dir.exists():
            return []
        return list(self.cache_dir.glob("universe_selection_*.json"))

    def clear_cache(self) -> None:
        if not self.cache_dir.exists():
            return
        for file in self.cache_dir.glob("universe_selection_*.json"):
            file.unlink()


def save_selection_to_warehouse(result: UniverseSelectionResult, config: AppConfig) -> Any:
    if not config.storage.enabled:
        return None
    from binance50.storage.importers import import_universe_selection
    return import_universe_selection(result.dict(), config)

def load_latest_selection_from_warehouse(config: AppConfig) -> Any:
    if not config.storage.enabled:
        return None
    from binance50.storage.parquet_store import ParquetDatasetStore
    store = ParquetDatasetStore(config)
    ds_name = config.storage.datasets.universe_dataset_name
    df = store.read_dataset(ds_name)
    if df.empty:
        return None
    # Just returning DataFrame for now to fulfill the helper need
    return df
