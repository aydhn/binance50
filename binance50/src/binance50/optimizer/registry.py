import pandas as pd

from binance50.optimizer.models import OptimizationRunResult, OptimizationTrial


class OptimizationRegistry:
    def __init__(self):
        self.runs: dict[str, OptimizationRunResult] = {}
        self.trials: dict[str, OptimizationTrial] = {}

    def register_run(self, result: OptimizationRunResult) -> None:
        self.runs[result.run_id] = result
        for trial in result.trials:
            self.register_trial(trial)

    def register_trial(self, trial: OptimizationTrial) -> None:
        self.trials[trial.trial_id] = trial

    def get_trial(self, trial_id: str) -> OptimizationTrial | None:
        return self.trials.get(trial_id)

    def list_trials(self, run_id: str | None = None) -> list[OptimizationTrial]:
        if run_id:
            return [t for t in self.trials.values() if t.run_id == run_id]
        return list(self.trials.values())

    def rank_trials(self, run_id: str, metric: str = "robust_score") -> list[OptimizationTrial]:
        trials = self.list_trials(run_id)
        # Filter for completed trials with the metric
        valid_trials = [
            t for t in trials if t.status == "completed" and getattr(t, metric, None) is not None
        ]
        return sorted(valid_trials, key=lambda t: getattr(t, metric), reverse=True)

    def get_best_trial(self, run_id: str) -> OptimizationTrial | None:
        ranked = self.rank_trials(run_id)
        return ranked[0] if ranked else None

    def to_dataframe(self) -> pd.DataFrame:
        data = []
        for trial in self.trials.values():
            data.append(trial.model_dump())
        return pd.DataFrame(data)
