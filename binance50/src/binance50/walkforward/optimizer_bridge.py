from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindow


class WalkForwardOptimizerBridge:
    def __init__(
        self, config: AppConfig, optimizer_runner: Any, optimizer_search_space_builder: Any
    ):
        self.config = config
        self.optimizer_runner = optimizer_runner
        self.optimizer_search_space_builder = optimizer_search_space_builder

    def run_optimizer_for_window(
        self,
        window: WalkForwardWindow,
        train_df: pd.DataFrame,
        validation_df: pd.DataFrame,
        base_request: Any,
    ) -> Any:
        limited_config = self.limit_trials_for_window(self.config)
        request = self.build_window_optimizer_request(window, base_request)
        result = self.optimizer_runner.run(
            request, train_df=train_df, validation_df=validation_df, config=limited_config
        )
        return result

    def select_best_trial_for_window(self, optimizer_result: Any, config: AppConfig) -> Any:
        # Assuming the optimizer_result has a list of trials, and each trial has a robust_score or similar
        # Fallback to the primary metric if validation_robust_score is not specifically available
        select_by = config.walkforward.optimizer.select_best_by

        if not optimizer_result.trials:
            return None

        best_trial = None
        best_score = -float("inf")

        for trial in optimizer_result.trials:
            if trial.status != "completed":
                continue

            # Simulate getting score, actual implementation would depend on OptimizationRunResult model
            score = trial.metrics.get(select_by)
            if score is None:
                score = trial.metrics.get(config.optimizer.objective.primary_metric, -float("inf"))

            if score > best_score:
                best_score = score
                best_trial = trial

        return best_trial

    def build_window_optimizer_request(self, window: WalkForwardWindow, base_request: Any) -> Any:
        # Clone request and annotate with window ID
        import copy

        req = copy.deepcopy(base_request)
        if hasattr(req, "metadata"):
            req.metadata["window_id"] = window.window_id
        return req

    def limit_trials_for_window(self, config: AppConfig) -> AppConfig:
        import copy

        new_config = copy.deepcopy(config)
        new_config.optimizer.mode.max_trials = new_config.walkforward.optimizer.override_max_trials
        return new_config

    def validate_optimizer_selection(
        self, optimizer_result: Any, selected_trial: Any, config: AppConfig
    ) -> None:
        if config.walkforward.optimizer.use_test_for_selection:
            raise ValueError("Test data must not be used for selecting the best trial")
        if selected_trial is None:
            raise ValueError("No valid trial found to select")
