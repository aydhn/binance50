import math

from binance50.config.models import AppConfig
from binance50.optimizer.objective import compute_objective_score


def test_objective_score_computed():
    config = AppConfig()
    pack = {
        "metrics": {"total_return": 10.0, "sharpe": 1.5, "max_drawdown": -10.0, "trade_count": 50},
        "costs": {},
    }
    res = compute_objective_score(pack, config)
    assert res.final_score is not None


def test_nan_score_reject():
    config = AppConfig()
    pack = {
        "metrics": {
            "total_return": float("nan"),
            "sharpe": 1.5,
            "max_drawdown": -10.0,
            "trade_count": 50,
        },
        "costs": {},
    }
    # normalize_metric handles NaN by converting to 0.0 so it doesn't fail unless final sum is NaN
    res = compute_objective_score(pack, config)
    assert not math.isnan(res.final_score)
