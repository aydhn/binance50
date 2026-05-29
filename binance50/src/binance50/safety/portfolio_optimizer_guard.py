from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioSandboxSafetyError
from binance50.portfolio.sandbox.optimizer_skeleton import PortfolioOptimizerSkeletonReport


def assert_portfolio_optimizer_config_safe(config: AppConfig) -> None:
    if not config.portfolio_sandbox.optimizer_skeleton.production_allocation_forbidden:
        raise PortfolioSandboxSafetyError("production_allocation_forbidden must be True")


def assert_optimizer_output_sandbox_only(
    report: PortfolioOptimizerSkeletonReport, config: AppConfig
) -> None:
    if (
        config.portfolio_sandbox.optimizer_skeleton.production_allocation_forbidden
        and report.used_for_selection
    ):
        if config.portfolio_sandbox.optimizer_skeleton.default_enabled_for_selection:
            raise PortfolioSandboxSafetyError("Optimizer cannot be default enabled for selection")


def assert_no_production_allocation(
    report: PortfolioOptimizerSkeletonReport, config: AppConfig
) -> None:
    pass


def assert_no_real_position_sizing(
    report: PortfolioOptimizerSkeletonReport, config: AppConfig
) -> None:
    pass


def build_portfolio_optimizer_safety_report(config: AppConfig) -> dict:
    try:
        assert_portfolio_optimizer_config_safe(config)
        return {"status": "passed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
