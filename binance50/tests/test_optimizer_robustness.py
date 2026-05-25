from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationTrial, ParameterSet
from binance50.optimizer.robustness import compute_robustness_for_trials


def test_robustness_computation():
    config = AppConfig()
    pset = ParameterSet(parameter_set_id="1", values={}, config_patch={}, hash="")
    trial1 = OptimizationTrial(
        trial_id="1",
        run_id="1",
        method="grid",
        parameter_set=pset,
        status="completed",
        started_at_utc=0,
        objective_score=10.0,
    )
    trial2 = OptimizationTrial(
        trial_id="2",
        run_id="1",
        method="grid",
        parameter_set=pset,
        status="completed",
        started_at_utc=0,
        objective_score=9.0,
    )

    reports = compute_robustness_for_trials([trial1, trial2], config)
    assert len(reports) == 2
    assert reports["1"].robustness_score is not None
