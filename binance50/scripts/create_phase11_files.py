import os
from pathlib import Path

# Directories to create
dirs = [
    "src/binance50/indicators",
    "src/binance50/indicators/adapters",
    "src/binance50/features",
    "src/binance50/safety",
    "src/binance50/storage",
    "tests",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

# Files to create (with empty content or init marker)
files = {
    "src/binance50/indicators/__init__.py": "",
    "src/binance50/indicators/models.py": "",
    "src/binance50/indicators/registry.py": "",
    "src/binance50/indicators/engine.py": "",
    "src/binance50/indicators/context.py": "",
    "src/binance50/indicators/validators.py": "",
    "src/binance50/indicators/warmup.py": "",
    "src/binance50/indicators/transforms.py": "",
    "src/binance50/indicators/trend.py": "",
    "src/binance50/indicators/momentum.py": "",
    "src/binance50/indicators/volatility.py": "",
    "src/binance50/indicators/volume.py": "",
    "src/binance50/indicators/adapters/__init__.py": "",
    "src/binance50/indicators/adapters/base.py": "",
    "src/binance50/indicators/adapters/native.py": "",
    "src/binance50/indicators/adapters/talib_adapter.py": "",
    "src/binance50/indicators/adapters/pandas_ta_adapter.py": "",
    "src/binance50/indicators/reports.py": "",
    "src/binance50/indicators/cache.py": "",
    "src/binance50/indicators/export.py": "",
    "src/binance50/indicators/quality.py": "",
    "src/binance50/features/__init__.py": "",
    "src/binance50/features/basic_returns.py": "",
    "src/binance50/safety/indicator_guard.py": "",
    "tests/test_indicator_models.py": "",
    "tests/test_indicator_registry.py": "",
    "tests/test_indicator_warmup.py": "",
    "tests/test_indicator_transforms.py": "",
    "tests/test_trend_indicators.py": "",
    "tests/test_momentum_indicators.py": "",
    "tests/test_volatility_indicators.py": "",
    "tests/test_volume_indicators.py": "",
    "tests/test_indicator_engine.py": "",
    "tests/test_indicator_adapters.py": "",
    "tests/test_indicator_quality.py": "",
    "tests/test_indicator_cache.py": "",
    "tests/test_indicator_guard.py": "",
    "tests/test_cli_indicators.py": "",
}

for path, content in files.items():
    p = Path(path)
    if not p.exists():
        p.write_text(content)
        print(f"Created: {path}")
