
import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.indicators.cache import (
    build_indicator_cache_path,
    clear_indicator_cache,
    list_indicator_cache,
    load_indicator_result,
    save_indicator_result,
)
from binance50.indicators.models import (
    IndicatorFrameMetadata,
    IndicatorRunRequest,
    IndicatorRunResult,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    config = AppConfig()
    config.indicators.cache_dir = str(tmp_path)
    return config, tmp_path

def test_build_cache_path(temp_cache_dir):
    config, _ = temp_cache_dir
    p = build_indicator_cache_path(config, "BTCUSDT", "spot", "1m", "native", "hash123")
    assert p.name == "spot_btcusdt_1m_native_hash123.parquet"
    assert ".." not in p.name # Simple path traversal check

def test_save_load_result(temp_cache_dir):
    config, tmp_path = temp_cache_dir

    df = pd.DataFrame({"close": [1, 2, 3]})
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [])
    meta = IndicatorFrameMetadata("BTC", MarketScope.SPOT, "1m", "native", 3, 3, 0, 0, 0, 0, 0, 3, "", "", "", "hash123")
    res = IndicatorRunResult(req, df, meta)

    p = save_indicator_result(res, config)
    assert p.exists()
    assert p.with_suffix(".json").exists()

    loaded = load_indicator_result(p)
    assert loaded is not None
    assert loaded.metadata.config_hash == "hash123"
    assert len(loaded.output_df) == 3

def test_list_and_clear_cache(temp_cache_dir):
    config, tmp_path = temp_cache_dir

    df = pd.DataFrame({"close": [1]})
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [])
    meta = IndicatorFrameMetadata("BTC", MarketScope.SPOT, "1m", "native", 1, 1, 0, 0, 0, 0, 0, 1, "", "", "", "hash123")
    res = IndicatorRunResult(req, df, meta)

    save_indicator_result(res, config)

    lst = list_indicator_cache(config)
    assert len(lst) == 1

    # Dry run
    clear_res = clear_indicator_cache(config, dry_run=True)
    assert clear_res["cleared_count"] == 1
    assert len(list_indicator_cache(config)) == 1

    # Actual clear
    clear_res = clear_indicator_cache(config, dry_run=False)
    assert clear_res["cleared_count"] == 1
    assert len(list_indicator_cache(config)) == 0
