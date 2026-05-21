from pathlib import Path

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import OHLCVStoreError
from binance50.market_data.cache import (
    build_ohlcv_cache_path,
    build_ohlcv_metadata_path,
    ensure_cache_dirs,
    is_cache_available,
    read_metadata,
    write_metadata,
)
from binance50.market_data.ohlcv_models import OHLCVFrameMetadata


class OHLCVStore:
    def __init__(self, config: AppConfig):
        self.config = config
        ensure_cache_dirs(config)

    def save(self, df: pd.DataFrame, metadata: OHLCVFrameMetadata) -> Path:
        cache_path = build_ohlcv_cache_path(
            self.config, metadata.symbol, metadata.market_scope, metadata.interval
        )
        meta_path = build_ohlcv_metadata_path(
            self.config, metadata.symbol, metadata.market_scope, metadata.interval
        )

        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            if self.config.market_data.cache_format == "parquet":
                df.to_parquet(cache_path, index=False)
            elif self.config.market_data.cache_format == "csv":
                df.to_csv(cache_path, index=False)
            elif self.config.market_data.cache_format == "jsonl":
                df.to_json(cache_path, orient="records", lines=True)
            else:
                raise OHLCVStoreError(
                    f"Unsupported cache format: {self.config.market_data.cache_format}"
                )

            metadata.cache_path = str(cache_path)
            write_metadata(metadata, meta_path)
            return cache_path
        except Exception as e:
            raise OHLCVStoreError(f"Failed to save OHLCV data to {cache_path}: {e}")

    def load(
        self, symbol: str, market_scope: MarketScope, interval: str
    ) -> tuple[pd.DataFrame, OHLCVFrameMetadata | None]:
        if not self.exists(symbol, market_scope, interval):
            raise OHLCVStoreError(f"No cache found for {symbol} {interval} {market_scope}")

        cache_path = build_ohlcv_cache_path(self.config, symbol, market_scope, interval)
        meta_path = build_ohlcv_metadata_path(self.config, symbol, market_scope, interval)

        try:
            if self.config.market_data.cache_format == "parquet":
                df = pd.read_parquet(cache_path)
            elif self.config.market_data.cache_format == "csv":
                df = pd.read_csv(cache_path)
            elif self.config.market_data.cache_format == "jsonl":
                df = pd.read_json(cache_path, orient="records", lines=True)
            else:
                raise OHLCVStoreError(
                    f"Unsupported cache format: {self.config.market_data.cache_format}"
                )

            metadata = read_metadata(meta_path)

            # Note: Quality validation after load will be handled externally if configured

            return df, metadata
        except Exception as e:
            raise OHLCVStoreError(f"Failed to load OHLCV data from {cache_path}: {e}")

    def exists(self, symbol: str, market_scope: MarketScope, interval: str) -> bool:
        return is_cache_available(self.config, symbol, market_scope, interval)

    def delete(self, symbol: str, market_scope: MarketScope, interval: str) -> None:
        cache_path = build_ohlcv_cache_path(self.config, symbol, market_scope, interval)
        meta_path = build_ohlcv_metadata_path(self.config, symbol, market_scope, interval)

        try:
            if cache_path.exists():
                cache_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
        except OSError as e:
            raise OHLCVStoreError(f"Failed to delete cache files for {symbol} {interval}: {e}")

    def list_available(self) -> list[dict[str, str]]:
        available = []
        meta_dir = Path(self.config.market_data.metadata_dir)

        if not meta_dir.exists():
            return available

        for path in meta_dir.rglob("*_meta.json"):
            try:
                meta = read_metadata(path)
                if meta:
                    available.append(
                        {
                            "symbol": meta.symbol,
                            "market_scope": meta.market_scope.value,
                            "interval": meta.interval,
                            "row_count": str(meta.row_count),
                            "source": meta.source.value,
                            "generated_at": meta.generated_at_utc,
                        }
                    )
            except Exception:
                pass

        return available

    def compact(self, symbol: str, market_scope: MarketScope, interval: str) -> None:
        if not self.exists(symbol, market_scope, interval):
            return

        # Simplistic compaction: just load, deduplicate, and save back
        from binance50.market_data.incremental import deduplicate_by_open_time

        df, meta = self.load(symbol, market_scope, interval)
        deduped_df = deduplicate_by_open_time(df)

        if len(deduped_df) < len(df) and meta:
            meta.row_count = len(deduped_df)
            self.save(deduped_df, meta)
