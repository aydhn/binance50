from typing import Any

from binance50.backtest.analytics.advanced_metrics import sanitize_metric
from binance50.config.models import AppConfig


def compute_total_fee_cost(trades: list[Any]) -> float:
    return sum(getattr(t, "fee_usdt", 0.0) for t in trades)


def compute_total_slippage_cost(trades: list[Any]) -> float:
    return sum(getattr(t, "slippage_usdt", 0.0) for t in trades)


def compute_gross_vs_net_pnl(trades: list[Any]) -> tuple[float, float]:
    net = sum(getattr(t, "pnl_usdt", 0.0) for t in trades)
    fees = compute_total_fee_cost(trades)
    slippage = compute_total_slippage_cost(trades)
    gross = net + fees + slippage
    return gross, net


def compute_cost_drag_pct(gross_pnl: float, net_pnl: float) -> float | None:
    if gross_pnl <= 0:
        return None
    cost = gross_pnl - net_pnl
    return sanitize_metric((cost / gross_pnl) * 100.0)


def compute_cost_per_trade(trades: list[Any]) -> float | None:
    if not trades:
        return None
    fees = compute_total_fee_cost(trades)
    slippage = compute_total_slippage_cost(trades)
    return sanitize_metric((fees + slippage) / len(trades))


def build_cost_impact_report(result: Any, config: AppConfig) -> dict[str, Any]:
    # Placeholder: result.trades should be parsed
    trades = getattr(result, "trades", [])
    gross, net = compute_gross_vs_net_pnl(trades)
    drag = compute_cost_drag_pct(gross, net)

    warnings = []
    if drag is not None and drag > config.backtest_reporting.costs.high_cost_drag_pct:
        warnings.append(f"High cost drag detected: {drag:.2f}%")

    return {
        "gross_pnl": sanitize_metric(gross),
        "net_pnl": sanitize_metric(net),
        "total_fees": sanitize_metric(compute_total_fee_cost(trades)),
        "total_slippage": sanitize_metric(compute_total_slippage_cost(trades)),
        "cost_drag_pct": drag,
        "cost_per_trade": compute_cost_per_trade(trades),
        "warnings": warnings,
        "metadata": {"simulation_note": "Fee and slippage values are simulated."},
    }


def analyze_costs(result: Any, config: AppConfig) -> dict[str, Any]:
    if not config.backtest_reporting.costs.enabled:
        return {}
    return build_cost_impact_report(result, config)
