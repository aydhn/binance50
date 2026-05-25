import math

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationTrial


class ObjectiveScoreBreakdown(BaseModel):
    total_return_component: float
    sharpe_component: float
    sortino_component: float
    calmar_component: float
    drawdown_component: float
    profit_factor_component: float
    expectancy_component: float
    trade_count_component: float
    stability_component: float
    cost_drag_component: float
    overfit_penalty_component: float
    final_score: float
    warnings: list[str] = Field(default_factory=list)


def compute_objective_score(
    backtest_report_pack: dict, config: AppConfig
) -> ObjectiveScoreBreakdown:
    # Extract metrics from the report pack (simplified for skeleton)
    metrics = backtest_report_pack.get("metrics", {})
    costs = backtest_report_pack.get("costs", {})
    metrics.get("trade_count", 0)

    warnings = []

    # Base metrics
    total_return = metrics.get("total_return", 0.0)
    sharpe = metrics.get("sharpe", 0.0)
    sortino = metrics.get("sortino", 0.0)
    calmar = metrics.get("calmar", 0.0)
    metrics.get("max_drawdown", 0.0)
    profit_factor = metrics.get("profit_factor", 1.0)
    expectancy = metrics.get("expectancy", 0.0)
    costs.get("cost_drag_pct", 0.0)

    # Weights
    weights = config.optimizer.objective.components

    # Compute components
    total_return_comp = (
        normalize_metric(total_return, "total_return", config) * weights.total_return_weight
    )
    sharpe_comp = normalize_metric(sharpe, "sharpe", config) * weights.sharpe_weight
    sortino_comp = normalize_metric(sortino, "sortino", config) * weights.sortino_weight
    calmar_comp = normalize_metric(calmar, "calmar", config) * weights.calmar_weight
    drawdown_comp = (
        compute_drawdown_penalty(metrics, config) * abs(weights.max_drawdown_weight) * -1
    )
    profit_factor_comp = (
        normalize_metric(profit_factor, "profit_factor", config) * weights.profit_factor_weight
    )
    expectancy_comp = normalize_metric(expectancy, "expectancy", config) * weights.expectancy_weight
    trade_count_comp = (
        compute_trade_count_penalty(metrics, config) * abs(weights.trade_count_weight) * -1
    )
    stability_comp = 0.0  # Placeholder for robustness integration
    cost_drag_comp = compute_cost_drag_penalty(costs, config) * abs(weights.cost_drag_weight) * -1

    overfit_penalty_comp = 0.0  # To be updated after overfit calculation

    final_score = (
        total_return_comp
        + sharpe_comp
        + sortino_comp
        + calmar_comp
        + drawdown_comp
        + profit_factor_comp
        + expectancy_comp
        + trade_count_comp
        + stability_comp
        + cost_drag_comp
        + overfit_penalty_comp
    )

    if math.isnan(final_score) or math.isinf(final_score):
        raise ValueError("Objective score is NaN or Infinity")

    final_score = max(
        config.optimizer.objective.score_clamp_min,
        min(config.optimizer.objective.score_clamp_max, final_score),
    )

    return ObjectiveScoreBreakdown(
        total_return_component=total_return_comp,
        sharpe_component=sharpe_comp,
        sortino_component=sortino_comp,
        calmar_component=calmar_comp,
        drawdown_component=drawdown_comp,
        profit_factor_component=profit_factor_comp,
        expectancy_component=expectancy_comp,
        trade_count_component=trade_count_comp,
        stability_component=stability_comp,
        cost_drag_component=cost_drag_comp,
        overfit_penalty_component=overfit_penalty_comp,
        final_score=final_score,
        warnings=warnings,
    )


def compute_validation_objective(trial: OptimizationTrial, config: AppConfig) -> float:
    if not trial.validation_result:
        return config.optimizer.objective.score_clamp_min

    breakdown = compute_objective_score(trial.validation_result, config)
    return breakdown.final_score


def compute_train_validation_gap_penalty(
    train_report: dict, validation_report: dict, config: AppConfig
) -> float:
    train_metrics = train_report.get("metrics", {})
    val_metrics = validation_report.get("metrics", {})

    train_return = train_metrics.get("total_return", 0.0)
    val_return = val_metrics.get("total_return", 0.0)

    gap = train_return - val_return
    if gap > config.optimizer.overfit.max_train_validation_return_gap_pct:
        return gap / 100.0  # simple penalty scaling
    return 0.0


def compute_trade_count_penalty(metrics: dict, config: AppConfig) -> float:
    trade_count = metrics.get("trade_count", 0)
    min_trade = config.optimizer.objective.min_trade_count

    if trade_count < min_trade:
        # Higher penalty for fewer trades
        return (min_trade - trade_count) / min_trade
    return 0.0


def compute_drawdown_penalty(metrics: dict, config: AppConfig) -> float:
    max_dd = abs(metrics.get("max_drawdown", 0.0))
    limit = config.optimizer.objective.max_drawdown_hard_limit_pct

    if max_dd > limit:
        return (max_dd - limit) / limit * 2.0  # harsh penalty
    return max_dd / 100.0


def compute_cost_drag_penalty(cost_report: dict, config: AppConfig) -> float:
    drag = cost_report.get("cost_drag_pct", 0.0)
    limit = config.optimizer.objective.max_cost_drag_pct

    if drag > limit:
        return (drag - limit) / limit * 2.0
    return drag / 100.0


def normalize_metric(value: float, metric_name: str, config: AppConfig) -> float:
    # A simple normalization placeholder - in reality might use standard scalers or clipping
    if math.isnan(value) or math.isinf(value):
        return 0.0

    # Scale ranges based on metric typical values
    if metric_name == "sharpe":
        return max(-1.0, min(3.0, value)) / 3.0
    elif metric_name == "profit_factor":
        return max(0.0, min(3.0, value - 1.0)) / 2.0
    elif metric_name == "total_return":
        return max(-1.0, min(2.0, value / 100.0))

    return value


def validate_objective_score(score: float, config: AppConfig) -> None:
    if math.isnan(score) or math.isinf(score):
        raise ValueError("Score is NaN or Infinity")
