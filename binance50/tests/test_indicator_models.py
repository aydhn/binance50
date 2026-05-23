import pandas as pd

from binance50.core.enums import MarketScope
from binance50.indicators.models import (
    IndicatorBackend,
    IndicatorColumnMetadata,
    IndicatorFrameMetadata,
    IndicatorGroup,
    IndicatorOutputStatus,
    IndicatorRunRequest,
    IndicatorRunResult,
    IndicatorSpec,
)


def test_indicator_spec_to_dict():
    spec = IndicatorSpec(
        name="sma_20",
        group=IndicatorGroup.TREND,
        backend=IndicatorBackend.NATIVE,
        parameters={"period": 20},
        input_columns=["close"],
        output_columns=["trend_sma_20"],
        min_lookback=20,
        description="Simple Moving Average",
        version=1,
    )
    d = spec.to_dict(redacted=True)
    assert d["name"] == "sma_20"
    assert d["group"] == "trend"
    assert d["backend"] == "native"
    assert d["parameters"] == {"period": 20}
    assert d["input_columns"] == ["close"]
    assert d["output_columns"] == ["trend_sma_20"]
    assert d["min_lookback"] == 20
    assert d["description"] == "Simple Moving Average"


def test_indicator_run_request_to_dict():
    req = IndicatorRunRequest(
        symbol="BTCUSDT",
        market_scope=MarketScope.SPOT,
        interval="1m",
        input_dataset_name="ohlcv",
        backend="native",
        indicator_specs=[],
        start_time_ms=1000,
        end_time_ms=2000,
        include_input_columns=True,
        request_id="req1",
        correlation_id="cor1",
    )
    d = req.to_dict()
    assert d["symbol"] == "BTCUSDT"
    assert d["market_scope"] == "spot"
    assert d["interval"] == "1m"
    assert d["input_dataset_name"] == "ohlcv"
    assert d["backend"] == "native"
    assert d["indicator_specs_count"] == 0
    assert d["start_time_ms"] == 1000
    assert d["end_time_ms"] == 2000
    assert d["include_input_columns"] is True


def test_indicator_frame_metadata_to_dict():
    meta = IndicatorFrameMetadata(
        symbol="BTCUSDT",
        market_scope=MarketScope.SPOT,
        interval="1m",
        backend="native",
        row_count=100,
        input_row_count=100,
        indicator_count=5,
        start_open_time=1000,
        end_open_time=2000,
        max_lookback=20,
        warmup_rows=19,
        valid_rows=81,
        generated_at_utc="2023-01-01T00:00:00Z",
        input_hash="hash1",
        output_hash="hash2",
        config_hash="hash3",
        warnings=[],
    )
    d = meta.to_dict()
    assert d["symbol"] == "BTCUSDT"
    assert d["market_scope"] == "spot"
    assert d["input_hash"] == "hash1"
    assert d["output_hash"] == "hash2"
    assert d["config_hash"] == "hash3"


def test_indicator_column_metadata_to_dict():
    meta = IndicatorColumnMetadata(
        column_name="trend_sma_20",
        indicator_name="sma_20",
        group=IndicatorGroup.TREND,
        parameters={"period": 20},
        min_lookback=20,
        nan_count=19,
        valid_count=81,
        first_valid_open_time=1000,
        last_valid_open_time=2000,
        status=IndicatorOutputStatus.VALID,
        warnings=[],
    )
    d = meta.to_dict()
    assert d["column_name"] == "trend_sma_20"
    assert d["status"] == "valid"


def test_indicator_run_result_to_dict():
    req = IndicatorRunRequest("BTC", MarketScope.SPOT, "1m", "ohlcv", "native", [])
    meta = IndicatorFrameMetadata(
        "BTC", MarketScope.SPOT, "1m", "native", 10, 10, 0, 0, 0, 0, 0, 10, "", "", "", ""
    )
    df = pd.DataFrame()
    res = IndicatorRunResult(req, df, meta)
    d = res.to_dict()
    assert d["success"] is True
    assert d["error"] is None
    assert d["row_count"] == 0
