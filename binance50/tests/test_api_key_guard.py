from pathlib import Path

import pytest
from pydantic import SecretStr

from binance50.config.loader import load_config
from binance50.core.exceptions import (
    ApiPermissionError,
    CredentialPairError,
    UnsupportedPermissionError,
)
from binance50.safety.api_key_guard import (
    assert_live_profile_has_required_permissions,
    assert_readonly_profile_has_no_trade_permissions,
    build_api_key_safety_report,
    validate_credentials_required_policy,
    validate_permission_policy,
)


@pytest.fixture
def base_config(tmp_path: Path):
    # Setup dummy environment.yaml to provide the matrix
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "environments.yaml").write_text("""
default_profile: local_paper_spot
profiles:
  local_paper_spot:
    profile_name: local_paper_spot
    exchange: binance
    runtime_environment: local
    trading_mode: paper
    market_scope: spot
    account_domain: spot
    endpoints:
      rest_base_url: null
      rest_fallback_urls: []
      websocket_market_base_url: null
      websocket_user_base_url: null
    is_testnet: false
    is_mainnet: false
    is_paper: true
    is_live: false
    allows_real_orders: false
    requires_api_key: false
    requires_api_secret: false
    requires_live_guard: false
    supports_user_data_stream: false
    supports_market_stream: false
    supports_order_placement: false
    permission_level: no_credentials
  spot_mainnet_readonly:
    profile_name: spot_mainnet_readonly
    exchange: binance
    runtime_environment: mainnet
    trading_mode: paper
    market_scope: spot
    account_domain: spot
    endpoints:
      rest_base_url: "https://api.binance.com"
      rest_fallback_urls: []
      websocket_market_base_url: "wss://stream.binance.com:9443/ws"
      websocket_user_base_url: "wss://stream.binance.com:9443/ws"
    is_testnet: false
    is_mainnet: true
    is_paper: true
    is_live: false
    allows_real_orders: false
    requires_api_key: false
    requires_api_secret: false
    requires_live_guard: false
    supports_user_data_stream: true
    supports_market_stream: true
    supports_order_placement: false
    permission_level: no_credentials
  spot_mainnet_live:
    profile_name: spot_mainnet_live
    exchange: binance
    runtime_environment: mainnet
    trading_mode: live
    market_scope: spot
    account_domain: spot
    endpoints:
      rest_base_url: "https://api.binance.com"
      rest_fallback_urls: []
      websocket_market_base_url: "wss://stream.binance.com:9443/ws"
      websocket_user_base_url: "wss://stream.binance.com:9443/ws"
    is_testnet: false
    is_mainnet: true
    is_paper: false
    is_live: true
    allows_real_orders: true
    requires_api_key: true
    requires_api_secret: true
    requires_live_guard: true
    supports_user_data_stream: true
    supports_market_stream: true
    supports_order_placement: true
    permission_level: live_order
  usdm_futures_mainnet_live:
    profile_name: usdm_futures_mainnet_live
    exchange: binance
    runtime_environment: mainnet
    trading_mode: live
    market_scope: usdm_futures
    account_domain: usdm_futures
    endpoints:
      rest_base_url: "https://fapi.binance.com"
      rest_fallback_urls: []
      websocket_market_base_url: "wss://fstream.binance.com"
      websocket_user_base_url: "wss://fstream.binance.com"
    is_testnet: false
    is_mainnet: true
    is_paper: false
    is_live: true
    allows_real_orders: true
    requires_api_key: true
    requires_api_secret: true
    requires_live_guard: true
    supports_user_data_stream: true
    supports_market_stream: true
    supports_order_placement: true
    permission_level: live_order
""")
    (tmp_path / "config" / "default.yaml").write_text("project:\n  name: test")

    return load_config(str(tmp_path / "config"))


def test_paper_profile_credentials_not_required(base_config):
    # Default is paper
    validate_credentials_required_policy(base_config)


def test_credential_pair_error(base_config):
    base_config.credentials.binance.api_key = SecretStr("TEST_KEY")
    base_config.credentials.binance.api_secret = SecretStr("")
    with pytest.raises(CredentialPairError):
        validate_credentials_required_policy(base_config)

    base_config.credentials.binance.api_key = SecretStr("")
    base_config.credentials.binance.api_secret = SecretStr("TEST_SECRET")
    with pytest.raises(CredentialPairError):
        validate_credentials_required_policy(base_config)


def test_readonly_profile_with_trade_permission(base_config):
    base_config.runtime.environment_profile = "spot_mainnet_readonly"
    base_config.credentials.binance.permission_spot_trade = True
    with pytest.raises(ApiPermissionError):
        assert_readonly_profile_has_no_trade_permissions(base_config)


def test_spot_live_requires_spot_permission(base_config):
    base_config.runtime.environment_profile = "spot_mainnet_live"
    with pytest.raises(ApiPermissionError):
        assert_live_profile_has_required_permissions(base_config)

    base_config.credentials.binance.permission_spot_trade = True
    assert_live_profile_has_required_permissions(base_config)


def test_futures_live_requires_futures_permission(base_config):
    base_config.runtime.environment_profile = "usdm_futures_mainnet_live"
    with pytest.raises(ApiPermissionError):
        assert_live_profile_has_required_permissions(base_config)

    base_config.credentials.binance.permission_futures_trade = True
    assert_live_profile_has_required_permissions(base_config)


def test_margin_unsupported(base_config):
    base_config.credentials.binance.permission_margin_trade = True
    with pytest.raises(UnsupportedPermissionError):
        validate_permission_policy(base_config)


def test_build_api_key_safety_report_redacts(base_config):
    base_config.credentials.binance.api_key = SecretStr("MY_SECRET_KEY")
    base_config.credentials.binance.api_secret = SecretStr("MY_SECRET_SECRET")
    report = build_api_key_safety_report(base_config)

    # Check that secrets are not in report
    report_str = str(report)
    assert "MY_SECRET" not in report_str
