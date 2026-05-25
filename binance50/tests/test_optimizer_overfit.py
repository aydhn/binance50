from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationTrial, ParameterSet
from binance50.optimizer.overfit import build_overfit_report


def test_overfit_risk_levels():
    config = AppConfig()
    pset = ParameterSet(parameter_set_id="1", values={}, config_patch={}, hash="")
    trial = OptimizationTrial(
        trial_id="1",
        run_id="1",
        method="grid",
        parameter_set=pset,
        status="completed",
        started_at_utc=0,
        train_result={"metrics": {"total_return": 100.0, "sharpe": 3.0}},
        validation_result={"metrics": {"total_return": 10.0, "sharpe": 0.5}},
    )

    report = build_overfit_report(trial, config)
    assert report.overfit_risk_level in ["high", "critical"]
    assert report.rejected
