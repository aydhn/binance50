import pytest

from binance50.config.loader import load_config
from binance50.connectors.endpoint_resolver import build_endpoint_info
from binance50.core.enums import EnvironmentProfileName
from binance50.core.exceptions import ConfigValidationError


def test_paper_profile_endpoints() -> None:
    config = load_config()
    # Default is paper
    assert (
        config.selected_environment_profile.profile_name == EnvironmentProfileName.LOCAL_PAPER_SPOT
    )
    info = build_endpoint_info(config)

    assert info.is_paper is True
    assert info.is_mainnet is False
    assert info.is_testnet is False


def test_spot_testnet_endpoints() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.SPOT_TESTNET
    info = build_endpoint_info(config)

    assert info.is_testnet is True
    assert info.is_mainnet is False
    assert info.rest_base_url == "https://testnet.binance.vision/api"


def test_usdm_futures_testnet_endpoints() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.USDM_FUTURES_TESTNET
    info = build_endpoint_info(config)

    assert info.is_testnet is True
    assert info.rest_base_url == "https://demo-fapi.binance.com"


def test_url_scheme_validation() -> None:
    config = load_config()
    config.runtime.environment_profile = EnvironmentProfileName.SPOT_TESTNET
    from binance50.connectors.endpoint_resolver import validate_endpoint_scheme

    with pytest.raises(ConfigValidationError):
        validate_endpoint_scheme("http://testnet.binance.vision/api")

    with pytest.raises(ConfigValidationError):
        validate_endpoint_scheme("ws://stream.binance.com:9443/ws")
