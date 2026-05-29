from typing import Any, Dict, List
import pandas as pd
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.portfolio.construction.adapters.scipy_slsqp_adapter import SciPySLSQPPortfolioAdapter
from binance50.portfolio.construction.inverse_volatility import compute_inverse_volatility_weights

class PortfolioConstructionOptimizerSkeletonReport(BaseModel):
    enabled: bool
    scipy_available: bool
    method: str
    used_for_default_allocation: bool
    objective_description: str
    constraints: dict[str, Any]
    success: bool
    weights: dict[str, float] = Field(default_factory=dict)
    objective_value: float = 0.0
    production_allocation_forbidden: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

def build_constrained_allocation_problem(candidates: List[Any], cov_matrix: pd.DataFrame, config: AppConfig) -> Dict[str, Any]:
    adapter = SciPySLSQPPortfolioAdapter()
    bounds = adapter.build_bounds(len(candidates), config)
    cons = adapter.build_constraints(config)
    return {"objective": "Minimize Portfolio Variance (Skeleton Example)", "bounds": bounds, "constraints": str(cons)}

def run_scipy_slsqp_skeleton(candidates: List[Any], cov_matrix: pd.DataFrame, volatilities: Dict[str, float], config: AppConfig) -> PortfolioConstructionOptimizerSkeletonReport:
    warnings = []
    if not config.portfolio_construction.allocation_methods.allow_scipy_optimizer_skeleton:
        return PortfolioConstructionOptimizerSkeletonReport(enabled=False, scipy_available=False, method="scipy_slsqp_skeleton", used_for_default_allocation=False, objective_description="", constraints={}, success=False, production_allocation_forbidden=True)
    adapter = SciPySLSQPPortfolioAdapter()
    availability = adapter.availability_report()
    if not availability["available"]:
        warnings.append("SciPy is missing. Skipping optimization.")
        return PortfolioConstructionOptimizerSkeletonReport(enabled=True, scipy_available=False, method="scipy_slsqp_skeleton", used_for_default_allocation=False, objective_description="Minimize Variance", constraints={}, success=False, production_allocation_forbidden=True, warnings=warnings)
    symbols = list(cov_matrix.columns)
    n = len(symbols)
    def min_var_objective(w): return w.T @ cov_matrix.values @ w
    x0 = [1.0/n] * n
    bounds = adapter.build_bounds(n, config)
    constraints = adapter.build_constraints(config)
    problem_desc = build_constrained_allocation_problem(candidates, cov_matrix, config)
    try:
        result = adapter.minimize_objective(min_var_objective, x0, bounds, constraints, config)
        if result["success"]:
            weights_dict = {symbols[i]: float(result["weights"][i]) for i in range(n)}
            report = PortfolioConstructionOptimizerSkeletonReport(enabled=True, scipy_available=True, method="scipy_slsqp_skeleton", used_for_default_allocation=False, objective_description=problem_desc["objective"], constraints=problem_desc, success=True, weights=weights_dict, objective_value=float(result["objective_value"]), production_allocation_forbidden=config.portfolio_construction.allocation_methods.production_optimizer_forbidden, warnings=warnings)
            validate_optimizer_skeleton_output(report, config)
            return report
        else:
            warnings.append(f"Optimization failed: {result.get('message')}")
            weights_dict = fallback_to_inverse_volatility(candidates, volatilities, config)
            return PortfolioConstructionOptimizerSkeletonReport(enabled=True, scipy_available=True, method="scipy_slsqp_skeleton", used_for_default_allocation=False, objective_description=problem_desc["objective"], constraints=problem_desc, success=False, weights=weights_dict, production_allocation_forbidden=True, warnings=warnings)
    except Exception as e:
        warnings.append(f"Optimization threw exception: {str(e)}")
        weights_dict = fallback_to_inverse_volatility(candidates, volatilities, config)
        return PortfolioConstructionOptimizerSkeletonReport(enabled=True, scipy_available=True, method="scipy_slsqp_skeleton", used_for_default_allocation=False, objective_description=problem_desc["objective"], constraints=problem_desc, success=False, weights=weights_dict, production_allocation_forbidden=True, warnings=warnings)

def validate_optimizer_skeleton_output(report: PortfolioConstructionOptimizerSkeletonReport, config: AppConfig) -> None:
    if not report.production_allocation_forbidden: raise ValueError("Optimizer skeleton must have production_allocation_forbidden = True.")

def fallback_to_inverse_volatility(candidates: List[Any], volatilities: Dict[str, float], config: AppConfig) -> Dict[str, float]:
    return compute_inverse_volatility_weights(candidates, volatilities, config)
