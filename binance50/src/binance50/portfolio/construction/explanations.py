from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioConstructionQualityError
from binance50.portfolio.construction.models import (
    PortfolioAllocationBreakdown,
    PortfolioAllocationItem,
    PortfolioAllocationMethod,
)


def build_allocation_item_explanation(item: PortfolioAllocationItem, context: dict[str, Any]) -> str:
    if item.method == PortfolioAllocationMethod.equal_weight: return f"Equal weight allocation of {item.sandbox_weight*100:.2f}% (hypothetical notional ${item.hypothetical_notional_usdt:.2f})."
    elif item.method == PortfolioAllocationMethod.inverse_volatility: return explain_inverse_vol_weight(item, context)
    elif item.method == PortfolioAllocationMethod.volatility_targeting_skeleton: return f"{explain_inverse_vol_weight(item, context)} Scaled to hit portfolio target volatility."
    elif item.method == PortfolioAllocationMethod.risk_parity_skeleton: return f"Risk parity allocation of {item.sandbox_weight*100:.2f}% (hypothetical notional ${item.hypothetical_notional_usdt:.2f}) aiming for equal risk contribution."
    elif item.method == PortfolioAllocationMethod.scipy_slsqp_skeleton: return f"SciPy optimized allocation of {item.sandbox_weight*100:.2f}% (hypothetical notional ${item.hypothetical_notional_usdt:.2f})."
    return f"Sandbox allocation of {item.sandbox_weight*100:.2f}%."

def explain_inverse_vol_weight(item: PortfolioAllocationItem, context: dict[str, Any]) -> str:
    vol = item.volatility_estimate_pct
    return f"Inverse volatility allocation of {item.sandbox_weight*100:.2f}% (hypothetical notional ${item.hypothetical_notional_usdt:.2f}) based on realized volatility of {vol:.2f}%."

def build_method_explanation(method: PortfolioAllocationMethod, breakdown: PortfolioAllocationBreakdown, context: dict[str, Any]) -> str:
    parts = [f"Hypothetical portfolio constructed using {method.value} method.", f"Total allocated weight: {breakdown.total_weight*100:.2f}%.", f"Expected portfolio volatility: {breakdown.expected_portfolio_volatility_pct:.2f}%."]
    if breakdown.warnings: parts.append(f"Generated {len(breakdown.warnings)} warnings during construction.")
    return " ".join(parts)

def explain_volatility_targeting(report: dict[str, Any]) -> str:
    if not report.get("enabled", False): return "Volatility targeting is disabled."
    current = report.get("current_portfolio_volatility_pct", 0.0)
    target = report.get("target_volatility_pct", 0.0)
    scale = report.get("scale_factor", 1.0)
    return f"Scaled portfolio weights by {scale:.4f} to move expected volatility from {current:.2f}% to target {target:.2f}%."

def explain_risk_parity_skeleton(report: dict[str, Any]) -> str:
    if not report.get("enabled", False): return "Risk parity is disabled."
    if not report.get("success", False): return "Risk parity optimization failed or fell back to inverse volatility."
    obj = report.get("objective_value", 0.0)
    return f"Successfully optimized for equal risk contribution. Objective value: {obj:.6f}."

def validate_allocation_explanation(text: str, config: AppConfig) -> None:
    if not text:
        if config.portfolio_construction.quality.reject_missing_explanation: raise PortfolioConstructionQualityError("Explanation text is empty.")
        return
    text_lower = text.lower()
    forbidden_words = ["buy", "sell", "execute", "order", "fill", "market order", "limit order"]
    if config.portfolio_construction.quality.reject_order_like_output:
        for word in forbidden_words:
            if f" {word} " in f" {text_lower} ": raise PortfolioConstructionQualityError(f"Explanation contains forbidden order-like word: '{word}'.")
    if config.portfolio_construction.quality.reject_production_allocation_intent and ("production allocation" in text_lower or "position sizing" in text_lower): raise PortfolioConstructionQualityError("Explanation implies production allocation intent.")
    if config.portfolio_construction.quality.reject_live_or_paper_intent and ("live trade" in text_lower or "paper trade" in text_lower or "live execution" in text_lower): raise PortfolioConstructionQualityError("Explanation implies live or paper execution intent.")
