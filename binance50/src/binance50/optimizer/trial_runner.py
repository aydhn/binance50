import time
from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunRequest, OptimizationTrial, TrialStatus
from binance50.optimizer.objective import compute_objective_score
from binance50.optimizer.overfit import build_overfit_report
from binance50.optimizer.reproducibility import compute_trial_hash


class OptimizationTrialRunner:
    def __init__(
        self, config: AppConfig, backtest_runner: Any = None, report_pack_builder: Any = None
    ):
        self.config = config
        self.backtest_runner = backtest_runner
        self.report_pack_builder = report_pack_builder

    def run_trial(
        self, trial: OptimizationTrial, data_splits: Any, base_request: OptimizationRunRequest
    ) -> OptimizationTrial:
        trial.started_at_utc = int(time.time() * 1000)
        trial.status = TrialStatus.RUNNING

        try:
            self.build_trial_config(self.config, trial.parameter_set)

            # Simulated run - actual implementation would call backtest_runner with splits
            train_report = self.run_backtest_for_split(
                trial.parameter_set,
                data_splits.train if data_splits else None,
                "train",
                base_request,
            )
            val_report = self.run_backtest_for_split(
                trial.parameter_set,
                data_splits.validation if data_splits else None,
                "validation",
                base_request,
            )
            test_report = self.run_backtest_for_split(
                trial.parameter_set, data_splits.test if data_splits else None, "test", base_request
            )

            trial.train_result = train_report
            trial.validation_result = val_report
            trial.test_result = test_report

            # Evaluate objective and overfit on validation results
            if val_report:
                breakdown = compute_objective_score(val_report, self.config)
                trial.objective_score = breakdown.final_score
                trial.robust_score = breakdown.final_score  # updated later if robust analysis runs

            if train_report and val_report:
                trial.overfit_report = build_overfit_report(trial, self.config).model_dump()

            self.validate_trial_result(trial)

            trial.status = TrialStatus.COMPLETED

        except Exception as e:
            self.handle_trial_failure(trial, e)

        trial.finished_at_utc = int(time.time() * 1000)

        # Ensures determinism
        trial_hash = compute_trial_hash(trial)
        trial.metadata["hash"] = trial_hash

        return trial

    def run_backtest_for_split(
        self, parameter_set: Any, split_df: Any, split_name: str, base_request: Any
    ) -> dict:
        # Placeholder for actual backtest run
        return {
            "metrics": {
                "total_return": 10.0,
                "sharpe": 1.2,
                "max_drawdown": -15.0,
                "trade_count": 25,
            },
            "costs": {"cost_drag_pct": 5.0},
        }

    def build_trial_config(self, base_config: AppConfig, parameter_set: Any) -> AppConfig:
        # Placeholder for deep copy and patch application
        return base_config

    def compute_trial_scores(self, trial: OptimizationTrial) -> None:
        if trial.validation_result:
            breakdown = compute_objective_score(trial.validation_result, self.config)
            trial.objective_score = breakdown.final_score
            trial.robust_score = breakdown.final_score

    def validate_trial_result(self, trial: OptimizationTrial) -> None:
        if trial.objective_score is None:
            raise ValueError("Trial objective score could not be computed")

    def handle_trial_failure(self, trial: OptimizationTrial, error: Exception) -> None:
        trial.status = TrialStatus.FAILED
        trial.error = str(error)
