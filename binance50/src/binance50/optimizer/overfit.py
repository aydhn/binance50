from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationTrial


class OverfitReport(BaseModel):
    trial_id: str
    train_score: float | None = None
    validation_score: float | None = None
    test_score: float | None = None
    train_validation_gap: float | None = None
    train_validation_sharpe_gap: float | None = None
    validation_test_gap: float | None = None
    parameter_complexity: float = 0.0
    low_trade_count_penalty: float = 0.0
    high_drawdown_penalty: float = 0.0
    cost_drag_penalty: float = 0.0
    overfit_risk_level: str
    rejected: bool = False
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_overfit_report(trial: OptimizationTrial, config: AppConfig) -> OverfitReport:
    train_metrics = trial.train_result.get("metrics", {}) if trial.train_result else {}
    val_metrics = trial.validation_result.get("metrics", {}) if trial.validation_result else {}
    test_metrics = trial.test_result.get("metrics", {}) if trial.test_result else {}
    val_costs = trial.validation_result.get("costs", {}) if trial.validation_result else {}

    train_return = train_metrics.get("total_return", 0.0)
    val_return = val_metrics.get("total_return", 0.0)
    train_metrics.get("sharpe", 0.0)
    val_metrics.get("sharpe", 0.0)

    gap_return, gap_sharpe = compute_train_validation_gap(train_metrics, val_metrics)
    val_test_gap = compute_validation_test_gap(val_metrics, test_metrics)

    complexity_penalty = compute_parameter_complexity_penalty(trial.parameter_set, config)
    trade_count_penalty = 0.0
    if config.optimizer.overfit.penalize_low_trade_count:
        trade_count = val_metrics.get("trade_count", 0)
        if trade_count < config.optimizer.objective.min_trade_count:
            trade_count_penalty = (
                config.optimizer.objective.min_trade_count - trade_count
            ) / config.optimizer.objective.min_trade_count

    drawdown_penalty = 0.0
    if config.optimizer.overfit.penalize_high_drawdown:
        max_dd = abs(val_metrics.get("max_drawdown", 0.0))
        limit = config.optimizer.objective.max_drawdown_hard_limit_pct
        if max_dd > limit:
            drawdown_penalty = (max_dd - limit) / limit

    cost_drag_penalty = 0.0
    if config.optimizer.overfit.penalize_high_cost_drag:
        drag = val_costs.get("cost_drag_pct", 0.0)
        limit = config.optimizer.objective.max_cost_drag_pct
        if drag > limit:
            cost_drag_penalty = (drag - limit) / limit

    # Risk classification
    risk_level = "low"
    rejected = False
    warnings = []

    if (
        gap_return is not None
        and gap_return > config.optimizer.overfit.max_train_validation_return_gap_pct
    ):
        risk_level = "high"
        warnings.append("Train/Validation return gap too high")
        if config.optimizer.overfit.reject_if_train_validation_gap_too_high:
            rejected = True

    if (
        gap_sharpe is not None
        and gap_sharpe > config.optimizer.overfit.max_train_validation_sharpe_gap
    ):
        risk_level = "critical" if risk_level == "high" else "high"
        warnings.append("Train/Validation sharpe gap too high")
        if config.optimizer.overfit.reject_if_train_validation_gap_too_high:
            rejected = True

    if (
        config.optimizer.overfit.reject_if_validation_bad
        and val_return < config.optimizer.overfit.validation_score_min
    ):
        rejected = True
        warnings.append("Validation score below minimum")

    if (
        test_metrics
        and config.optimizer.overfit.reject_if_test_bad
        and test_metrics.get("total_return", 0.0) < config.optimizer.overfit.test_score_min_warning
    ):
        rejected = True
        warnings.append("Test score below minimum")

    report = OverfitReport(
        trial_id=trial.trial_id,
        train_score=train_return,
        validation_score=val_return,
        test_score=test_metrics.get("total_return", 0.0) if test_metrics else None,
        train_validation_gap=gap_return,
        train_validation_sharpe_gap=gap_sharpe,
        validation_test_gap=val_test_gap,
        parameter_complexity=complexity_penalty,
        low_trade_count_penalty=trade_count_penalty,
        high_drawdown_penalty=drawdown_penalty,
        cost_drag_penalty=cost_drag_penalty,
        overfit_risk_level=classify_overfit_risk(gap_return, gap_sharpe, config),
        rejected=rejected,
        warnings=warnings,
    )
    return report


def compute_train_validation_gap(
    train_metrics: dict, val_metrics: dict
) -> tuple[float | None, float | None]:
    if not train_metrics or not val_metrics:
        return None, None
    return (
        train_metrics.get("total_return", 0.0) - val_metrics.get("total_return", 0.0),
        train_metrics.get("sharpe", 0.0) - val_metrics.get("sharpe", 0.0),
    )


def compute_validation_test_gap(val_metrics: dict, test_metrics: dict) -> float | None:
    if not val_metrics or not test_metrics:
        return None
    return val_metrics.get("total_return", 0.0) - test_metrics.get("total_return", 0.0)


def compute_parameter_complexity_penalty(parameter_set: Any, config: AppConfig) -> float:
    if not config.optimizer.overfit.penalize_parameter_complexity:
        return 0.0
    return (
        float(len(parameter_set.values)) * config.optimizer.overfit.complexity_penalty_per_parameter
    )


def classify_overfit_risk(
    gap_return: float | None, gap_sharpe: float | None, config: AppConfig
) -> str:
    if gap_return is None or gap_sharpe is None:
        return "unknown"
    if (
        gap_return > config.optimizer.overfit.max_train_validation_return_gap_pct * 1.5
        or gap_sharpe > config.optimizer.overfit.max_train_validation_sharpe_gap * 1.5
    ):
        return "critical"
    if (
        gap_return > config.optimizer.overfit.max_train_validation_return_gap_pct
        or gap_sharpe > config.optimizer.overfit.max_train_validation_sharpe_gap
    ):
        return "high"
    if gap_return > config.optimizer.overfit.max_train_validation_return_gap_pct * 0.5:
        return "medium"
    return "low"


def should_reject_trial_for_overfit(report: OverfitReport, config: AppConfig) -> bool:
    return report.rejected
