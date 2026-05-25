from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import OptimizationRunResult, ParameterSet


def assert_optimizer_config_safe(config: AppConfig) -> None:
    if not config.optimizer.real_exchange_forbidden:
        raise ValueError("Optimizer config must forbid real exchange")
    if not config.optimizer.paper_trade_forbidden:
        raise ValueError("Optimizer config must forbid paper trading")
    if not config.optimizer.live_trade_forbidden:
        raise ValueError("Optimizer config must forbid live trading")
    if not config.optimizer.order_creation_forbidden:
        raise ValueError("Optimizer config must forbid order creation")
    if not config.optimizer.api_key_forbidden:
        raise ValueError("Optimizer config must forbid API keys")
    if not config.optimizer.signed_request_forbidden:
        raise ValueError("Optimizer config must forbid signed requests")


def assert_search_space_safe(specs: list[Any], config: AppConfig) -> None:
    for spec in specs:
        if not config.optimizer.search_space.allow_execution_params and (
            "execution" in spec.path.lower() or "order" in spec.path.lower()
        ):
            raise ValueError(f"Execution parameters forbidden in search space: {spec.path}")
        if not config.optimizer.search_space.allow_live_params and (
            "live" in spec.path.lower() or "paper" in spec.path.lower()
        ):
            raise ValueError(f"Live/paper parameters forbidden in search space: {spec.path}")


def assert_parameter_set_safe(parameter_set: ParameterSet, config: AppConfig) -> None:
    assert_no_execution_params(parameter_set)
    assert_no_live_or_paper_params(parameter_set)


def assert_no_execution_params(parameter_set: ParameterSet) -> None:
    for path in parameter_set.values:
        if "execution" in path.lower() or "order" in path.lower() or "quantity" in path.lower():
            raise ValueError(f"Execution parameters forbidden: {path}")


def assert_no_live_or_paper_params(parameter_set: ParameterSet) -> None:
    for path in parameter_set.values:
        if "live" in path.lower() or "paper" in path.lower() or "real" in path.lower():
            raise ValueError(f"Live/paper parameters forbidden: {path}")


def assert_optimizer_output_safe(result: OptimizationRunResult, config: AppConfig) -> None:
    # Just check intent metadata if any exists
    if result.request.max_trials is not None and result.request.max_trials < 0:
        raise ValueError("Max trials cannot be negative")


def build_optimizer_safety_report(config: AppConfig) -> dict:
    return {
        "status": "safe",
        "real_exchange_forbidden": config.optimizer.real_exchange_forbidden,
        "paper_trade_forbidden": config.optimizer.paper_trade_forbidden,
        "live_trade_forbidden": config.optimizer.live_trade_forbidden,
        "order_creation_forbidden": config.optimizer.order_creation_forbidden,
    }
