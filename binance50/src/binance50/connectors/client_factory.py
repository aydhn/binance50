from typing import Any

from pydantic import BaseModel

from binance50.audit.writer import audit_event
from binance50.config.models import AppConfig
from binance50.connectors.base import (
    ExchangeAdapterProtocol,
    RestConnectorProtocol,
    WebSocketConnectorProtocol,
)
from binance50.connectors.disabled_client import DisabledExchangeAdapter
from binance50.connectors.mock_client import MockExchangeAdapter
from binance50.connectors.order_gateway import DisabledOrderGateway, OrderGatewayProtocol
from binance50.connectors.response_models import ConnectorHealth
from binance50.safety.connector_guard import assert_connector_allowed, build_connector_safety_report


class ConnectorBundle(BaseModel):
    # Pydantic may struggle with protocols so we use Any and set model_config
    rest: Any
    websocket: Any
    order_gateway: Any
    adapter: Any
    health: ConnectorHealth
    safety_report: dict[str, Any]

    model_config = {"arbitrary_types_allowed": True}


def create_rest_client(config: AppConfig) -> RestConnectorProtocol:
    bundle = create_connector_bundle(config)
    return bundle.rest  # type: ignore[no-any-return]


def create_websocket_client(config: AppConfig) -> WebSocketConnectorProtocol:
    bundle = create_connector_bundle(config)
    return bundle.websocket  # type: ignore[no-any-return]


def create_order_gateway(config: AppConfig) -> OrderGatewayProtocol:
    bundle = create_connector_bundle(config)
    return bundle.order_gateway  # type: ignore[no-any-return]


def create_exchange_adapter(config: AppConfig) -> ExchangeAdapterProtocol:
    bundle = create_connector_bundle(config)
    return bundle.adapter  # type: ignore[no-any-return]


def create_connector_bundle(config: AppConfig) -> ConnectorBundle:
    from binance50.connectors.adapter_registry import get_adapter_factory, resolve_adapter_key

    safety_report = build_connector_safety_report(config)

    if not config.connector.connection_enabled:
        if config.connector.mock_enabled:
            adapter_obj: ExchangeAdapterProtocol = MockExchangeAdapter()
            audit_event(
                "connector_enabled",
                component="connector",
                action="init",
                metadata={
                    "type": "mock",
                    "profile": config.selected_environment_profile.profile_name.value,
                },
            )
        else:
            adapter_obj = DisabledExchangeAdapter()
            audit_event(
                "connector_disabled",
                component="connector",
                action="init",
                metadata={"reason": "connection_enabled is false"},
            )
    else:
        # Check guard before producing real skeleton
        assert_connector_allowed(config)
        adapter_key = resolve_adapter_key(config)
        factory_func = get_adapter_factory(adapter_key)
        adapter_obj = factory_func(config)
        audit_event(
            "connector_enabled",
            component="connector",
            action="init",
            metadata={"type": "skeleton", "adapter": adapter_key},
        )

    order_gateway = DisabledOrderGateway()  # order gateway always disabled in this phase
    health = adapter_obj.get_health()

    return ConnectorBundle(
        rest=adapter_obj.rest,
        websocket=adapter_obj.websocket,
        order_gateway=order_gateway,
        adapter=adapter_obj,
        health=health,
        safety_report=safety_report,
    )
