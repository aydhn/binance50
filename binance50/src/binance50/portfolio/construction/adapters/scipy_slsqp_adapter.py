from typing import Any, Callable, Dict, Tuple
import numpy as np
from binance50.config.models import AppConfig
from binance50.portfolio.construction.adapters.base import BasePortfolioOptimizerAdapter
from binance50.core.exceptions import PortfolioConstructionOptimizerError

class SciPySLSQPPortfolioAdapter(BasePortfolioOptimizerAdapter):
    def availability_report(self) -> Dict[str, Any]:
        try:
            import scipy.optimize as sco # noqa: F401
            return {"available": True, "version": getattr(sco, "__version__", "unknown")}
        except ImportError:
            return {"available": False, "version": None}

    def minimize_objective(self, objective_fn: Callable, x0: np.ndarray, bounds: Tuple, constraints: Dict, config: AppConfig) -> Dict[str, Any]:
        if not config.portfolio_construction.allocation_methods.allow_scipy_optimizer_skeleton: raise PortfolioConstructionOptimizerError("SciPy optimizer is explicitly forbidden by config.")
        try:
            import scipy.optimize as sco
        except ImportError:
            raise PortfolioConstructionOptimizerError("SciPy is required but not installed.") from None
        opts = {'maxiter': 1000, 'ftol': 1e-6}
        result = sco.minimize(objective_fn, x0, method='SLSQP', bounds=bounds, constraints=constraints, options=opts)
        self.validate_result(result, config)
        return {"success": result.success, "weights": result.x, "objective_value": result.fun, "message": result.message}

    def build_bounds(self, n_assets: int, config: AppConfig) -> Tuple:
        max_w = config.portfolio_construction.equal_weight.max_single_weight_pct / 100.0
        return tuple((0.0, max_w) for _ in range(n_assets))

    def build_constraints(self, config: AppConfig) -> Dict[str, Any]:
        target_sum = min(1.0 - (config.portfolio_construction.simulated_capital.cash_buffer_pct / 100.0), config.portfolio_construction.simulated_capital.max_allocated_capital_pct / 100.0)
        return {'type': 'eq', 'fun': lambda x: np.sum(x) - target_sum}

    def validate_result(self, result: Any, config: AppConfig) -> None:
        if result.success and not np.isfinite(result.x).all(): raise PortfolioConstructionOptimizerError("Optimization succeeded but produced non-finite weights.")
