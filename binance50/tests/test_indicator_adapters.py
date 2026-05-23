import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.core.exceptions import OptionalIndicatorBackendMissingError
from binance50.indicators.adapters.native import NativeIndicatorAdapter
from binance50.indicators.adapters.pandas_ta_adapter import PandasTaIndicatorAdapter
from binance50.indicators.adapters.talib_adapter import TalibIndicatorAdapter
from binance50.indicators.context import IndicatorContext
from binance50.indicators.registry import IndicatorRegistry


def test_native_adapter():
    config = AppConfig()
    registry = IndicatorRegistry(config)
    adapter = NativeIndicatorAdapter(registry)

    assert adapter.name == "native"
    assert adapter.is_available() is True

    rep = adapter.availability_report()
    assert rep["available"] is True
    assert rep["supported_functions_count"] > 0

    # Compute test
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    spec = registry.get("sma_9")
    ctx = IndicatorContext(config, "BTC", MarketScope.SPOT, "1m", "native", ["close"])

    res = adapter.compute(spec, df, ctx)
    assert len(res) == 10
    assert "trend_sma_9" in res.columns


def test_talib_adapter():
    adapter = TalibIndicatorAdapter()
    assert adapter.name == "talib_optional"

    rep = adapter.availability_report()
    assert "available" in rep

    # Check graceful unavailable behavior if not installed
    if not adapter.is_available():
        with pytest.raises(OptionalIndicatorBackendMissingError):
            adapter.compute(None, pd.DataFrame(), None)


def test_pandas_ta_adapter():
    adapter = PandasTaIndicatorAdapter()
    assert adapter.name == "pandas_ta_optional"

    rep = adapter.availability_report()
    assert "available" in rep

    if not adapter.is_available():
        with pytest.raises(OptionalIndicatorBackendMissingError):
            adapter.compute(None, pd.DataFrame(), None)
