import numpy as np
import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.indicators.adapters.native import NativeIndicatorAdapter
from binance50.indicators.engine import IndicatorEngine
from binance50.indicators.models import IndicatorRunRequest
from binance50.indicators.registry import IndicatorRegistry


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "open_time": np.arange(1000, 1100),
        "close_time": np.arange(1001, 1101),
        "open": np.random.uniform(10, 20, 100),
        "high": np.random.uniform(20, 25, 100),
        "low": np.random.uniform(5, 10, 100),
        "close": np.random.uniform(10, 20, 100),
        "volume": np.random.uniform(100, 1000, 100),
        "is_closed": [True] * 100
    })

def test_engine_compute_default(sample_data):
    config = AppConfig()
    config.indicators.min_rows_required = 10
    registry = IndicatorRegistry(config)
    adapter = NativeIndicatorAdapter(registry)
    engine = IndicatorEngine(config, registry, adapter)

    # Restrict specs so it doesn't take too long or fail memory
    spec = registry.get("sma_20")
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [spec])

    res = engine.compute(sample_data, req)

    assert res.success is True
    assert "trend_sma_20" in res.output_df.columns
    assert "is_warmup" in res.output_df.columns
    assert res.metadata.row_count == 100
    assert res.metadata.indicator_count == 1
    assert res.metadata.warmup_rows == 20

def test_engine_drop_incomplete(sample_data):
    config = AppConfig()
    config.indicators.min_rows_required = 10
    config.indicators.drop_incomplete_last_candle = True

    registry = IndicatorRegistry(config)
    adapter = NativeIndicatorAdapter(registry)
    engine = IndicatorEngine(config, registry, adapter)

    data = sample_data.copy()
    data.loc[99, "is_closed"] = False

    spec = registry.get("sma_20")
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [spec])

    res = engine.compute(data, req)
    assert res.success is True
    assert len(res.output_df) == 99

def test_engine_future_column_fails(sample_data):
    config = AppConfig()
    config.indicators.min_rows_required = 10
    registry = IndicatorRegistry(config)
    adapter = NativeIndicatorAdapter(registry)
    engine = IndicatorEngine(config, registry, adapter)

    data = sample_data.copy()
    data["future_return"] = 0.1

    spec = registry.get("sma_20")
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [spec])

    res = engine.compute(data, req)
    assert res.success is False
    assert "LookaheadBiasError" in res.error or "Lookahead Bias risk" in res.error
