from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.constraints import validate_parameter_set
from binance50.optimizer.models import (
    OptimizationMethod,
    OptimizationRunRequest,
    OptimizationRunResult,
    OptimizationTrial,
    ParameterSpec,
    TrialStatus,
)
from binance50.optimizer.samplers import RandomParameterSampler


class RandomSearchOptimizer:
    def __init__(self, config: AppConfig):
        self.config = config
        self.sampler = RandomParameterSampler()

    def build_trials(
        self, request: OptimizationRunRequest, specs: list[ParameterSpec]
    ) -> list[OptimizationTrial]:
        parameter_sets = self.sampler.generate(specs, self.config)

        trials = []
        for i, param_set in enumerate(parameter_sets):
            try:
                validate_parameter_set(param_set, self.config)

                trial = OptimizationTrial(
                    trial_id=f"{request.request_id}_random_{i}",
                    run_id=request.request_id,
                    method=OptimizationMethod.RANDOM,
                    parameter_set=param_set,
                    status=TrialStatus.PENDING,
                    started_at_utc=0,
                )
                trials.append(trial)
            except ValueError as e:
                trial = OptimizationTrial(
                    trial_id=f"{request.request_id}_random_{i}",
                    run_id=request.request_id,
                    method=OptimizationMethod.RANDOM,
                    parameter_set=param_set,
                    status=TrialStatus.REJECTED_BY_GUARD,
                    error=str(e),
                    started_at_utc=0,
                )
                trials.append(trial)

        return trials

    def run(
        self, request: OptimizationRunRequest, specs: list[ParameterSpec], trial_runner: Any
    ) -> OptimizationRunResult:
        trials = self.build_trials(request, specs)

        completed_trials = []
        for trial in trials:
            if trial.status == TrialStatus.REJECTED_BY_GUARD:
                completed_trials.append(trial)
                continue

            try:
                completed_trial = trial_runner.run_trial(
                    trial, None, request
                )  # data_splits pass appropriately
                completed_trials.append(completed_trial)
            except Exception as e:
                trial.status = TrialStatus.FAILED
                trial.error = str(e)
                completed_trials.append(trial)
                if (
                    not self.config.optimizer.mode.continue_on_trial_failure
                    or self.config.optimizer.mode.fail_fast
                ):
                    break

        # Filter completed for best trial
        valid_trials = [
            t
            for t in completed_trials
            if t.status == TrialStatus.COMPLETED and t.robust_score is not None
        ]

        best_trial = None
        if valid_trials:
            best_trial = max(valid_trials, key=lambda t: t.robust_score or -float("inf"))

        ranked_trials = sorted(
            valid_trials, key=lambda t: t.robust_score or -float("inf"), reverse=True
        )

        return OptimizationRunResult(
            request=request,
            run_id=request.request_id,
            method=OptimizationMethod.RANDOM,
            trials=completed_trials,
            best_trial=best_trial,
            ranked_trials=ranked_trials,
            success=len(valid_trials) > 0,
        )
