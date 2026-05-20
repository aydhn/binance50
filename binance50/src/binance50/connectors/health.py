from typing import Any

from binance50.config.models import AppConfig
from binance50.connectors.client_factory import ConnectorBundle
from binance50.connectors.response_models import ConnectorHealth


def build_connector_health(config: AppConfig) -> ConnectorHealth:
    from binance50.connectors.client_factory import create_connector_bundle

    bundle = create_connector_bundle(config)
    return bundle.health


def build_connector_health_report(bundle: ConnectorBundle) -> dict[str, Any]:
    return {"health": bundle.health.redacted_dump(), "safety_report": bundle.safety_report}


def assert_connector_health_safe(health: ConnectorHealth) -> None:
    pass  # Add logic if needed, e.g., if blocking reasons > 0
