from binance50.config.models import AppConfig
from binance50.optimizer.grid_search import GridSearchOptimizer
from binance50.optimizer.models import OptimizationMethod, OptimizationRunRequest, ParameterSpec


class MockRunner:
    def run_trial(self, trial, data_splits, base_request):
        trial.status = "completed"
        trial.robust_score = 1.0
        return trial


def test_grid_trials_built():
    config = AppConfig()
    opt = GridSearchOptimizer(config)
    req = OptimizationRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        method=OptimizationMethod.GRID,
        request_id="1",
    )
    specs = [
        ParameterSpec(name="p1", path="p1", value_type="int", values=[1, 2], description="test")
    ]
    trials = opt.build_trials(req, specs)
    assert len(trials) == 2


def test_grid_run():
    config = AppConfig()
    opt = GridSearchOptimizer(config)
    req = OptimizationRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        method=OptimizationMethod.GRID,
        request_id="1",
    )
    specs = [
        ParameterSpec(name="p1", path="p1", value_type="int", values=[1, 2], description="test")
    ]
    result = opt.run(req, specs, MockRunner())
    assert result.success
    assert len(result.trials) == 2
