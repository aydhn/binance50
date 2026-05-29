from typing import Any, Dict
from binance50.config.models import AppConfig
from binance50.portfolio.construction.adapters.base import BasePortfolioOptimizerAdapter
from binance50.core.exceptions import PortfolioConstructionOptimizerError

class PyPortfolioOptSkeletonAdapter(BasePortfolioOptimizerAdapter):
    def availability_report(self) -> Dict[str, Any]:
        try:
            import pypfopt # noqa: F401
            return {"available": True, "version": getattr(pypfopt, "__version__", "unknown")}
        except ImportError:
            return {"available": False, "version": None}

    def explain_supported_methods(self) -> Dict[str, str]:
        return {"hrp": "Hierarchical Risk Parity", "ef": "Efficient Frontier", "black_litterman": "Black-Litterman Allocation"}

    def build_hrp_contract(self) -> Dict[str, Any]:
        return {"inputs": ["returns_df"], "outputs": ["weights"], "constraints_supported": ["long_only"]}

    def build_efficient_frontier_contract(self) -> Dict[str, Any]:
        return {"inputs": ["expected_returns", "covariance_matrix"], "outputs": ["weights"], "constraints_supported": ["min_weight", "max_weight", "target_return", "target_risk"]}

    def validate_adapter_sandbox_only(self, config: AppConfig) -> None:
        if not config.portfolio_construction.allocation_methods.production_optimizer_forbidden:
            raise PortfolioConstructionOptimizerError("PyPortfolioOpt adapter can only be used when production_optimizer_forbidden is True.")
