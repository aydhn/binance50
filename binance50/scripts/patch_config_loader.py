from pathlib import Path

import yaml

file_path = Path("config/default.yaml")
with open(file_path) as f:
    config = yaml.safe_load(f)

if "indicators" not in config:
    config["indicators"] = {
        "enabled": True,
        "default_backend": "native",
        "allowed_backends": ["native", "talib_optional", "pandas_ta_optional"],
        "fail_if_optional_backend_missing": False,
        "input_source_priority": ["warehouse", "market_data_cache", "fixture"],
        "output_dataset_name": "indicators",
        "cache_enabled": True,
        "cache_dir": "data/indicators",
        "export_dir": "data/indicators/exports",
        "require_closed_candles": True,
        "drop_incomplete_last_candle": True,
        "prevent_lookahead_bias": True,
        "enforce_monotonic_time": True,
        "reject_duplicate_open_time": True,
        "min_rows_required": 100,
        "max_columns_allowed": 500,
        "max_indicator_specs_per_run": 100,
        "float_precision": "float64",
        "fill_policy": "none",
        "warmup_policy": {
            "keep_warmup_rows": True,
            "mark_warmup_rows": True,
            "min_valid_ratio": 0.70
        },
        "default_periods": {
            "short": 9,
            "medium": 14,
            "long": 21,
            "slow": 50,
            "very_slow": 200
        },
        "trend": {
            "enabled": True,
            "sma_periods": [9, 20, 50, 100, 200],
            "ema_periods": [9, 12, 20, 26, 50, 100, 200],
            "wma_periods": [9, 20, 50],
            "dema_periods": [20, 50],
            "tema_periods": [20, 50],
            "macd": {
                "enabled": True,
                "fast": 12,
                "slow": 26,
                "signal": 9
            },
            "adx": {
                "enabled": True,
                "period": 14
            },
            "aroon": {
                "enabled": True,
                "period": 14
            }
        },
        "momentum": {
            "enabled": True,
            "rsi_periods": [7, 14, 21],
            "stochastic": {
                "enabled": True,
                "k_period": 14,
                "d_period": 3,
                "smooth_k": 3
            },
            "stoch_rsi": {
                "enabled": True,
                "rsi_period": 14,
                "stoch_period": 14,
                "k_period": 3,
                "d_period": 3
            },
            "roc_periods": [5, 10, 20],
            "mom_periods": [5, 10, 20],
            "cci_periods": [14, 20],
            "willr_periods": [14]
        },
        "volatility": {
            "enabled": True,
            "atr_periods": [14, 21],
            "natr_periods": [14],
            "bollinger": {
                "enabled": True,
                "period": 20,
                "stddev": 2.0
            },
            "keltner": {
                "enabled": True,
                "period": 20,
                "atr_period": 14,
                "multiplier": 2.0
            },
            "donchian": {
                "enabled": True,
                "period": 20
            },
            "rolling_std_periods": [10, 20, 50]
        },
        "volume": {
            "enabled": True,
            "obv": True,
            "vwap": {
                "enabled": True,
                "session_mode": "rolling",
                "rolling_period": 20
            },
            "mfi_periods": [14],
            "cmf_periods": [20],
            "adl": True,
            "volume_sma_periods": [20, 50],
            "volume_ema_periods": [20]
        },
        "transforms": {
            "enabled": True,
            "returns_periods": [1, 3, 5, 10],
            "log_returns": True,
            "hl_range": True,
            "oc_change": True,
            "typical_price": True,
            "weighted_close": True,
            "median_price": True
        },
        "quality": {
            "reject_all_nan_indicator": True,
            "reject_constant_indicator": False,
            "warn_high_nan_ratio": True,
            "max_nan_ratio": 0.40,
            "detect_inf": True,
            "detect_extreme_values": True,
            "extreme_zscore_threshold": 20.0
        }
    }

with open(file_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("Patched config.yaml")
