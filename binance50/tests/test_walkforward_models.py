from binance50.walkforward.models import (
    WalkForwardMode,
    WalkForwardRunRequest,
    WalkForwardRunResult,
    WalkForwardWindow,
)


def test_walkforward_window_model():
    window = WalkForwardWindow(
        window_id="test_win",
        index=0,
        mode=WalkForwardMode.rolling_window,
        train_start=0,
        train_end=100,
        validation_start=100,
        validation_end=120,
        test_start=120,
        test_end=140,
        train_rows=100,
        validation_rows=20,
        test_rows=20,
        embargo_bars=0,
    )
    assert window.window_id == "test_win"


def test_walkforward_run_result():
    req = WalkForwardRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        input_ohlcv_dataset_name="fix",
        mode=WalkForwardMode.rolling_window,
        optimizer_method="grid",
        request_id="123",
        correlation_id="123",
    )
    res = WalkForwardRunResult(
        request=req,
        run_id="run1",
        mode=WalkForwardMode.rolling_window,
        windows=[],
        window_results={},
        success=True,
    )
    assert res.run_id == "run1"
