import re

with open('binance50/src/binance50/universe/cache.py', 'r') as f:
    content = f.read()

methods_to_add = """
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
"""

content = content + "\n" + methods_to_add

with open('binance50/src/binance50/universe/cache.py', 'w') as f:
    f.write(content)
