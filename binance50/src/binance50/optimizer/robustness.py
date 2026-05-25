from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationTrial


class RobustnessReport(BaseModel):
    trial_id: str
    rank_stability_score: float | None = None
    metric_dispersion_score: float | None = None
    neighbor_sensitivity_score: float | None = None
    robustness_score: float | None = None
    fragile_optimum_warning: bool = False
    comparable_neighbor_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def compute_robustness_for_trials(
    trials: list[OptimizationTrial], config: AppConfig
) -> dict[str, RobustnessReport]:
    if not config.optimizer.robustness.enabled:
        return {}

    reports = {}

    # Pre-compute stability if configured
    rank_stability = (
        compute_rank_stability(trials, config)
        if config.optimizer.robustness.compute_rank_stability
        else 0.0
    )

    for trial in trials:
        if not trial.objective_score:
            continue

        dispersion = (
            compute_metric_dispersion(trial, config)
            if config.optimizer.robustness.compute_metric_dispersion
            else 0.0
        )

        neighbors = find_neighbor_trials(trial, trials, config)
        sensitivity = (
            compute_neighbor_sensitivity(trial, neighbors, config)
            if config.optimizer.robustness.compute_neighbor_sensitivity
            else 0.0
        )

        # Combine robust score (higher is better)
        # Assuming lower sensitivity and dispersion is better, we subtract them from a base
        robustness = (
            trial.objective_score
            - (sensitivity * 0.5)
            - (dispersion * 0.2)
            + (rank_stability * 0.1)
        )

        fragile = classify_fragile_optimum(sensitivity, config)

        warnings = []
        if fragile and config.optimizer.robustness.warn_fragile_optimum:
            warnings.append("Fragile optimum detected: High neighbor sensitivity")

        report = RobustnessReport(
            trial_id=trial.trial_id,
            rank_stability_score=rank_stability,
            metric_dispersion_score=dispersion,
            neighbor_sensitivity_score=sensitivity,
            robustness_score=robustness,
            fragile_optimum_warning=fragile,
            comparable_neighbor_count=len(neighbors),
            warnings=warnings,
        )
        reports[trial.trial_id] = report

        # Also update the trial itself
        trial.robust_score = robustness
        trial.robustness_report = report.model_dump()

    return reports


def compute_rank_stability(trials: list[OptimizationTrial], config: AppConfig) -> float:
    # Requires multiple time splits to calculate properly, placeholder
    return 1.0


def compute_metric_dispersion(trial: OptimizationTrial, config: AppConfig) -> float:
    # E.g. gap between win rate and profit factor normalized
    return 0.1


def compute_neighbor_sensitivity(
    trial: OptimizationTrial, neighbors: list[OptimizationTrial], config: AppConfig
) -> float:
    if not neighbors or not trial.objective_score:
        return 0.0

    # Calculate how much objective score drops in neighborhood
    drops = []
    for neighbor in neighbors:
        if neighbor.objective_score is not None:
            drop = trial.objective_score - neighbor.objective_score
            if drop > 0:
                drops.append(drop)

    if not drops:
        return 0.0

    # Return average drop as sensitivity
    return sum(drops) / len(drops)


def find_neighbor_trials(
    trial: OptimizationTrial, trials: list[OptimizationTrial], config: AppConfig
) -> list[OptimizationTrial]:
    neighbors = []
    # Identify neighbors based on parameter values distance
    # Here is a placeholder
    return neighbors


def classify_fragile_optimum(sensitivity: float, config: AppConfig) -> bool:
    # Example threshold
    return sensitivity > 20.0
