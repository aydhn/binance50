from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult, OptimizationTrial


def build_optimization_run_summary(result: OptimizationRunResult) -> dict:
    return {
        "run_id": result.run_id,
        "method": result.method,
        "trial_count": len(result.trials),
        "success": result.success,
        "best_trial_id": result.best_trial.trial_id if result.best_trial else None,
        "best_robust_score": result.best_trial.robust_score if result.best_trial else None,
    }


def build_trial_table(trials: list[OptimizationTrial], limit: int = 100) -> list[dict]:
    return [
        {
            "trial_id": t.trial_id,
            "status": t.status,
            "objective_score": t.objective_score,
            "robust_score": t.robust_score,
        }
        for t in trials[:limit]
    ]


def build_best_trial_report(result: OptimizationRunResult) -> dict:
    if not result.best_trial:
        return {}
    return result.best_trial.model_dump()


def build_overfit_summary(trials: list[OptimizationTrial]) -> dict:
    # Summarize overfit across trials
    return {"total_trials": len(trials)}


def build_robustness_summary(trials: list[OptimizationTrial]) -> dict:
    return {"total_trials": len(trials)}


def build_search_space_report(specs: list[Any]) -> dict:
    return {"total_parameters": len(specs)}


def build_split_report(metadata: Any) -> dict:
    if metadata is None:
        return {}
    return metadata.model_dump()


def build_optimizer_health_report(config: AppConfig) -> dict:
    return {"status": "healthy", "mode": config.optimizer.mode.default_method}


def build_optimizer_quality_report(result: OptimizationRunResult, config: AppConfig) -> dict:
    issues = []

    if len(result.trials) == 0 and config.optimizer.quality.reject_no_trials:
        issues.append({"type": "no_trials", "severity": "error", "message": "No trials generated"})

    failed_trials = [t for t in result.trials if t.status == "failed"]
    if (
        len(failed_trials) == len(result.trials)
        and len(result.trials) > 0
        and config.optimizer.quality.reject_all_trials_failed
    ):
        issues.append({"type": "all_failed", "severity": "error", "message": "All trials failed"})

    status = "failed" if any(i["severity"] == "error" for i in issues) else "passed"

    return {
        "status": status,
        "run_id": result.run_id,
        "trial_count": len(result.trials),
        "issues": issues,
    }


def assert_optimizer_quality_passed(report: dict, config: AppConfig) -> None:
    if report.get("status") == "failed":
        raise ValueError(f"Optimizer quality checks failed: {report.get('issues')}")
