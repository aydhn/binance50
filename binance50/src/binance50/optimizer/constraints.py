from binance50.config.models import AppConfig
from binance50.optimizer.models import ParameterSet, ParameterSpec


def validate_parameter_set(parameter_set: ParameterSet, config: AppConfig) -> None:
    reject_execution_parameters(parameter_set)
    reject_live_or_paper_parameters(parameter_set)

    cross_errors = validate_cross_parameter_constraints(parameter_set)
    if cross_errors:
        raise ValueError(f"Cross-parameter constraints failed: {cross_errors}")


def validate_parameter_bounds(spec: ParameterSpec) -> None:
    if spec.min_value is not None and spec.max_value is not None:
        if spec.min_value > spec.max_value:
            raise ValueError(f"Invalid bounds for {spec.name}: min > max")

    if spec.values:
        for val in spec.values:
            if spec.min_value is not None and val < spec.min_value:
                raise ValueError(f"Value {val} below min {spec.min_value} for {spec.name}")
            if spec.max_value is not None and val > spec.max_value:
                raise ValueError(f"Value {val} above max {spec.max_value} for {spec.name}")


def validate_cross_parameter_constraints(parameter_set: ParameterSet) -> list[str]:
    errors = []
    v = parameter_set.values

    # RSI constraints
    rsi_oversold = v.get("strategy.mean_reversion.rsi_oversold")
    rsi_overbought = v.get("strategy.mean_reversion.rsi_overbought")

    if rsi_oversold is not None and rsi_overbought is not None:
        if float(rsi_oversold) >= float(rsi_overbought):
            errors.append("rsi_oversold must be < rsi_overbought")

    # Risk thresholds
    research_min = v.get("signals.thresholds.research_candidate_min")
    risk_review_min = v.get("signals.thresholds.risk_review_min")

    if research_min is not None and risk_review_min is not None:
        if float(research_min) > float(risk_review_min):
            errors.append("research_candidate_min must be <= risk_review_min")

    # Notional constraints
    fixed_notional = v.get("backtest.sizing.fixed_notional_usdt")
    max_notional = v.get("backtest.sizing.max_notional_usdt")

    if fixed_notional is not None and max_notional is not None:
        if float(fixed_notional) > float(max_notional):
            errors.append("fixed_notional_usdt must be <= max_notional_usdt")

    # Positive constraints
    max_holding_bars = v.get("backtest.exits.max_holding_bars")
    if max_holding_bars is not None and int(max_holding_bars) <= 0:
        errors.append("max_holding_bars must be > 0")

    slippage = v.get("backtest.slippage.default_slippage_bps")
    if slippage is not None and float(slippage) < 0:
        errors.append("default_slippage_bps must be >= 0")

    min_adx = v.get("strategy.trend_following.min_adx")
    if min_adx is not None and float(min_adx) <= 0:
        errors.append("min_adx must be > 0")

    return errors


def reject_execution_parameters(parameter_set: ParameterSet) -> None:
    for path in parameter_set.values:
        path_lower = path.lower()
        if "execution" in path_lower or "order" in path_lower or "quantity" in path_lower:
            raise ValueError(f"Execution parameters are strictly forbidden: {path}")


def reject_live_or_paper_parameters(parameter_set: ParameterSet) -> None:
    for path in parameter_set.values:
        path_lower = path.lower()
        if "live" in path_lower or "paper" in path_lower or "real" in path_lower:
            raise ValueError(f"Live/paper trading parameters are strictly forbidden: {path}")


def compute_parameter_complexity(parameter_set: ParameterSet) -> float:
    # Basic complexity based on number of parameters
    return float(len(parameter_set.values))
