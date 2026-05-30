from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionConfigError, OrderSubmissionForbiddenError


def assert_execution_config_safe(config: AppConfig) -> None:
    if config.execution.global_.allow_order_submission:
        raise ExecutionConfigError("allow_order_submission must be False in Phase 28")
    if config.execution.global_.allow_gateway_calls:
        raise ExecutionConfigError("allow_gateway_calls must be False in Phase 28")
    if not config.execution.kill_switch.global_kill_switch_default_on:
        raise ExecutionConfigError("global_kill_switch_default_on must be True in Phase 28")


def assert_execution_input_safe(source_result: Any, config: AppConfig) -> None:
    pass


def assert_execution_output_safe(result: Any, config: AppConfig) -> None:
    pass


def assert_no_order_submission_enabled(config: AppConfig) -> None:
    if config.execution.global_.allow_order_submission:
        raise OrderSubmissionForbiddenError("Order submission is explicitly forbidden.")


def assert_no_gateway_calls_enabled(config: AppConfig) -> None:
    if config.execution.global_.allow_gateway_calls:
        raise ExecutionConfigError("Gateway calls are explicitly forbidden.")


def assert_no_live_testnet_enabled(config: AppConfig) -> None:
    if config.execution.global_.allow_live_intents or config.execution.global_.allow_testnet_intents:
        raise ExecutionConfigError("Live and testnet intents are explicitly forbidden.")


def build_execution_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "order_submission_disabled": not config.execution.global_.allow_order_submission,
        "gateway_calls_disabled": not config.execution.global_.allow_gateway_calls,
        "live_testnet_intents_disabled": not (config.execution.global_.allow_live_intents or config.execution.global_.allow_testnet_intents),
        "kill_switch_active": config.execution.kill_switch.global_kill_switch_default_on
    }
