from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionGatewayDisabledError

from binance50.execution.gateway import ExecutionGateway


def assert_all_gateways_disabled(config: AppConfig) -> None:
    gw_conf = config.execution.gateway
    if gw_conf.paper_gateway_enabled or gw_conf.testnet_gateway_enabled or gw_conf.live_gateway_enabled or gw_conf.test_order_gateway_enabled:
        raise ExecutionGatewayDisabledError("All gateways must be disabled in Phase 28.")


def assert_gateway_call_blocked(gateway: ExecutionGateway, config: AppConfig) -> None:
    if gateway.is_enabled():
        raise ExecutionGatewayDisabledError(f"Gateway {gateway.name()} is enabled but should be blocked.")


def assert_no_binance_client_dependency(payload: dict[str, Any], config: AppConfig) -> None:
    str_payload = str(payload).lower()
    if "binance_client" in str_payload or "binance.client" in str_payload:
        raise ExecutionGatewayDisabledError("Binance client dependency detected in payload.")


def assert_no_order_endpoint_reference(payload: dict[str, Any], config: AppConfig) -> None:
    str_payload = str(payload).lower()
    if "/api/v3/order" in str_payload:
        raise ExecutionGatewayDisabledError("Binance order endpoint reference detected in payload.")


def build_exchange_gateway_safety_report(config: AppConfig) -> dict[str, Any]:
    gw_conf = config.execution.gateway
    return {
        "all_gateways_disabled": gw_conf.all_implementations_disabled,
        "paper_gateway_enabled": gw_conf.paper_gateway_enabled,
        "testnet_gateway_enabled": gw_conf.testnet_gateway_enabled,
        "live_gateway_enabled": gw_conf.live_gateway_enabled,
        "test_order_gateway_enabled": gw_conf.test_order_gateway_enabled,
    }
