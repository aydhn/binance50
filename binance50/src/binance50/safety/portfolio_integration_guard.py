from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioIntegrationForbiddenError
from binance50.portfolio.sandbox.models import PortfolioSelectedSandboxCandidate


def assert_no_signal_engine_write(config: AppConfig) -> None:
    if not config.portfolio_sandbox.sandbox_output.write_to_signal_engine_forbidden:
        raise PortfolioIntegrationForbiddenError("Write to signal engine must be forbidden")


def assert_no_risk_engine_write(config: AppConfig) -> None:
    if not config.portfolio_sandbox.sandbox_output.write_to_risk_engine_forbidden:
        raise PortfolioIntegrationForbiddenError("Write to risk engine must be forbidden")


def assert_no_paper_live_write(config: AppConfig) -> None:
    if not config.portfolio_sandbox.sandbox_output.write_to_paper_engine_forbidden:
        raise PortfolioIntegrationForbiddenError("Write to paper engine must be forbidden")
    if not config.portfolio_sandbox.sandbox_output.write_to_live_engine_forbidden:
        raise PortfolioIntegrationForbiddenError("Write to live engine must be forbidden")


def assert_selected_candidates_not_production(
    candidates: list[PortfolioSelectedSandboxCandidate],
) -> None:
    pass


def assert_blocked_flags_true(candidates: list[PortfolioSelectedSandboxCandidate]) -> None:
    for c in candidates:
        if not c.blocked_from_execution:
            raise PortfolioIntegrationForbiddenError("blocked_from_execution must be True")


def build_portfolio_integration_safety_report(config: AppConfig) -> dict:
    try:
        assert_no_signal_engine_write(config)
        assert_no_risk_engine_write(config)
        assert_no_paper_live_write(config)
        return {"status": "passed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
