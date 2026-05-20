import pytest

from binance50.config.loader import load_config
from binance50.connectors.client_factory import create_connector_bundle
from binance50.connectors.disabled_client import DisabledExchangeAdapter
from binance50.connectors.mock_client import MockExchangeAdapter
from binance50.connectors.order_gateway import DisabledOrderGateway
from binance50.core.enums import EnvironmentProfileName
from binance50.core.exceptions import UnsupportedFeatureError


def test_default_produces_disabled_adapter() -> None:
    config = load_config()
    bundle = create_connector_bundle(config)
    assert isinstance(bundle.adapter, DisabledExchangeAdapter)
    assert isinstance(bundle.order_gateway, DisabledOrderGateway)
    assert bundle.health.status == "disabled_safe"


def test_mock_enabled_produces_mock_adapter() -> None:
    config = load_config()
    config.connector.mock_enabled = True
    bundle = create_connector_bundle(config)
    assert isinstance(bundle.adapter, MockExchangeAdapter)
    assert bundle.health.status == "mock_success"


def test_coinm_placeholder_throws() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.COINM_FUTURES_PLACEHOLDER
    config.connector.connection_enabled = True
    # Let's bypass paper-mock guard by setting it to a mainnet profile if needed,
    # or just enable mock if paper
    config.connector.mock_enabled = True

    with pytest.raises(UnsupportedFeatureError, match="COIN-M futures are not implemented"):
        create_connector_bundle(config)


def test_usdm_capabilities() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.USDM_FUTURES_TESTNET
    config.connector.connection_enabled = True
    bundle = create_connector_bundle(config)

    caps = bundle.rest.get_capabilities()
    assert caps.supports_routed_futures_streams is True


def test_spot_capabilities() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.SPOT_TESTNET
    config.connector.connection_enabled = True
    bundle = create_connector_bundle(config)

    caps = bundle.rest.get_capabilities()
    assert caps.supports_combined_streams is True
    assert caps.supports_raw_streams is True
