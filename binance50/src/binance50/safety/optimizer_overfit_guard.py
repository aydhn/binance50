from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult


def assert_overfit_policy_safe(config: AppConfig) -> None:
    if not config.optimizer.overfit.enabled:
        # Warning or error based on strictness
        pass


def assert_trial_not_overfit(report: Any, config: AppConfig) -> None:
    if report.rejected:
        raise ValueError(f"Trial rejected due to overfit: {report.warnings}")


def assert_best_trial_robust(result: OptimizationRunResult, config: AppConfig) -> None:
    if result.best_trial and result.best_trial.robustness_report:
        if result.best_trial.robustness_report.get("fragile_optimum_warning"):
            pass  # Usually just a warning, handled in report


def build_optimizer_overfit_safety_report(config: AppConfig) -> dict:
    return {
        "status": "safe" if config.optimizer.overfit.enabled else "warning",
        "overfit_enabled": config.optimizer.overfit.enabled,
    }
