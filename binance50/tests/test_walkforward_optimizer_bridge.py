import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardMode, WalkForwardWindow
from binance50.walkforward.optimizer_bridge import WalkForwardOptimizerBridge


class MockTrial:
    def __init__(self, status, metrics):
        self.status = status
        self.metrics = metrics
        self.parameters = {"a": 1}


class MockOptResult:
    def __init__(self):
        self.trials = [
            MockTrial("completed", {"robust_score": 10.0}),
            MockTrial("completed", {"robust_score": 20.0}),
        ]


class MockRunner:
    def run(self, req, train_df, validation_df, config):
        return MockOptResult()


def test_optimizer_bridge():
    config = AppConfig()
    bridge = WalkForwardOptimizerBridge(config, MockRunner(), None)
    window = WalkForwardWindow(
        window_id="w1",
        index=0,
        mode=WalkForwardMode.rolling_window,
        train_start=0,
        train_end=1,
        validation_start=1,
        validation_end=2,
        test_start=2,
        test_end=3,
        train_rows=1,
        validation_rows=1,
        test_rows=1,
        embargo_bars=0,
    )
    opt_res = bridge.run_optimizer_for_window(
        window, pd.DataFrame(), pd.DataFrame(), type("obj", (object,), {})()
    )
    best = bridge.select_best_trial_for_window(opt_res, config)
    assert best.metrics["robust_score"] == 20.0
