import re

with open('binance50/src/binance50/market_data/store.py', 'r') as f:
    content = f.read()

# Add load_from_warehouse and save_to_warehouse to OHLCVStore
methods_to_add = """
    def save_to_warehouse(self, df: pd.DataFrame, metadata: dict) -> Any:
        if not self.config.storage.enabled:
            return None
        from binance50.storage.importers import import_ohlcv_dataframe
        # Try to infer some fields
        sym = metadata.get("symbol", "UNKNOWN")
        scope = metadata.get("market_scope", "spot")
        inv = metadata.get("interval", "1m")
        return import_ohlcv_dataframe(df, sym, scope, inv, "fetch", self.config)

    def load_from_warehouse(self, symbol: str, market_scope: str, interval: str) -> pd.DataFrame | None:
        if not self.config.storage.enabled:
             return None
        from binance50.storage.parquet_store import ParquetDatasetStore
        store = ParquetDatasetStore(self.config)
        ds_name = self.config.storage.datasets.ohlcv_dataset_name
        filters = {"symbol": symbol, "market_scope": market_scope, "interval": interval}
        df = store.read_dataset(ds_name, filters)
        if df.empty:
             return None
        return df
"""

# Insert methods into OHLCVStore class
content = content.replace(
    "    def load_from_cache(self, symbol: str, market_scope: MarketScope, interval: str) -> pd.DataFrame | None:",
    methods_to_add + "\n    def load_from_cache(self, symbol: str, market_scope: MarketScope, interval: str) -> pd.DataFrame | None:"
)

with open('binance50/src/binance50/market_data/store.py', 'w') as f:
    f.write(content)
