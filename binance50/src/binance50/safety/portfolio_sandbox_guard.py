from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioSandboxSafetyError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, PortfolioSelectionRunResult


def assert_portfolio_sandbox_config_safe(config: AppConfig) -> None:
    p_config = config.portfolio_sandbox

    if not p_config.real_exchange_forbidden:
        raise PortfolioSandboxSafetyError("real_exchange_forbidden must be True")
    if not p_config.paper_trade_forbidden:
        raise PortfolioSandboxSafetyError("paper_trade_forbidden must be True")
    if not p_config.live_trade_forbidden:
        raise PortfolioSandboxSafetyError("live_trade_forbidden must be True")
    if not p_config.order_creation_forbidden:
        raise PortfolioSandboxSafetyError("order_creation_forbidden must be True")
    if not p_config.api_key_forbidden:
        raise PortfolioSandboxSafetyError("api_key_forbidden must be True")
    if not p_config.signed_request_forbidden:
        raise PortfolioSandboxSafetyError("signed_request_forbidden must be True")
    if not p_config.dashboard_forbidden:
        raise PortfolioSandboxSafetyError("dashboard_forbidden must be True")

    if not p_config.allocation_production_forbidden:
        raise PortfolioSandboxSafetyError("allocation_production_forbidden must be True")
    if not p_config.position_sizing_production_forbidden:
        raise PortfolioSandboxSafetyError("position_sizing_production_forbidden must be True")


def assert_portfolio_input_safe(inputs: list[PortfolioCandidateInput], config: AppConfig) -> None:
    for c in inputs:
        if config.portfolio_sandbox.inputs.reject_execution_fields:
            if any(x in c.metadata for x in ["order_id", "quantity", "leverage", "price"]):
                raise PortfolioSandboxSafetyError("Execution fields detected in input candidate")


def assert_portfolio_output_safe(result: PortfolioSelectionRunResult, config: AppConfig) -> None:
    assert_research_only_selection(result)


def assert_research_only_selection(result: PortfolioSelectionRunResult) -> None:
    for c in result.selected_candidates:
        if c.intent.value not in ["research_only", "sandbox_only", "no_order"]:
            raise PortfolioSandboxSafetyError(
                f"Candidate {c.candidate_id} has invalid intent: {c.intent.value}"
            )


def assert_no_live_paper_execution_intent(payload: dict) -> None:
    intent = payload.get("intent")
    if intent in ["live", "paper", "order", "execution"]:
        raise PortfolioSandboxSafetyError(f"Execution intent detected: {intent}")


def build_portfolio_sandbox_safety_report(config: AppConfig) -> dict:
    try:
        assert_portfolio_sandbox_config_safe(config)
        return {"status": "passed", "checks": "all strict requirements met"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
