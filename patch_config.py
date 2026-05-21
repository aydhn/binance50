import yaml
from pathlib import Path

config_path = Path("binance50/config/default.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

config["market_data"] = {
  "enabled": True,
  "real_fetch_enabled": False,
  "source": "binance_public",
  "prefer_market_data_only_endpoint": True,
  "base_data_endpoint": "https://data-api.binance.vision",
  "spot_klines_path": "/api/v3/klines",
  "usdm_klines_path": "/fapi/v1/klines",
  "default_intervals": [
    "1m",
    "5m",
    "15m",
    "1h",
    "4h",
    "1d"
  ],
  "allowed_intervals": [
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M"
  ],
  "default_history_days": {
    "1m": 30,
    "3m": 60,
    "5m": 90,
    "15m": 180,
    "30m": 365,
    "1h": 730,
    "2h": 730,
    "4h": 1095,
    "6h": 1095,
    "8h": 1095,
    "12h": 1095,
    "1d": 1825,
    "3d": 1825,
    "1w": 3650,
    "1M": 3650
  },
  "spot_max_limit": 1000,
  "usdm_max_limit": 1500,
  "request_limit_safety_margin_pct": 90,
  "exclude_incomplete_last_candle": True,
  "require_closed_candles": True,
  "allow_partial_candle_cache": False,
  "cache_enabled": True,
  "cache_format": "parquet",
  "cache_dir": "data/ohlcv",
  "metadata_dir": "data/ohlcv/metadata",
  "export_dir": "data/ohlcv/exports",
  "cache_partitioning": {
    "by_market_scope": True,
    "by_symbol": True,
    "by_interval": True
  },
  "incremental_enabled": True,
  "overlap_candles_on_update": 2,
  "max_gap_fill_attempts": 3,
  "validate_after_fetch": True,
  "validate_after_cache_load": True,
  "min_rows_required": 100,
  "max_rows_per_symbol_interval": 2000000,
  "quality": {
    "reject_duplicate_open_time": True,
    "reject_out_of_order": True,
    "reject_negative_prices": True,
    "reject_zero_or_negative_close": True,
    "reject_high_low_inconsistency": True,
    "reject_negative_volume": True,
    "warn_zero_volume": True,
    "detect_gaps": True,
    "max_gap_ratio_pct": 1.0,
    "allow_weekend_crypto_continuity": True,
    "timezone": "UTC"
  }
}

with open(config_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
