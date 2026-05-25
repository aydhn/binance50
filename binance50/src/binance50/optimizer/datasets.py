import pandas as pd

from binance50.optimizer.models import OptimizationRunResult, OptimizationTrial


def optimization_trials_to_dataframe(trials: list[OptimizationTrial]) -> pd.DataFrame:
    data = []
    for trial in trials:
        data.append(
            {
                "trial_id": trial.trial_id,
                "run_id": trial.run_id,
                "method": trial.method.value,
                "status": trial.status.value,
                "objective_score": trial.objective_score,
                "robust_score": trial.robust_score,
                "started_at_utc": trial.started_at_utc,
                "finished_at_utc": trial.finished_at_utc,
            }
        )
    return pd.DataFrame(data)


def optimization_run_to_dataframe(result: OptimizationRunResult) -> pd.DataFrame:
    data = [
        {
            "run_id": result.run_id,
            "symbol": result.request.symbol,
            "market_scope": result.request.market_scope,
            "interval": result.request.interval,
            "method": result.method.value,
            "trial_count": len(result.trials),
            "success": result.success,
        }
    ]
    return pd.DataFrame(data)


def overfit_reports_to_dataframe(trials: list[OptimizationTrial]) -> pd.DataFrame:
    data = []
    for trial in trials:
        if trial.overfit_report:
            data.append(trial.overfit_report)
    return pd.DataFrame(data)


def robustness_reports_to_dataframe(trials: list[OptimizationTrial]) -> pd.DataFrame:
    data = []
    for trial in trials:
        if trial.robustness_report:
            data.append(trial.robustness_report)
    return pd.DataFrame(data)
