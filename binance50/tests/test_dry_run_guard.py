from pathlib import Path

import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import DryRunViolationError, OrderPathDisabledError
from binance50.safety.dry_run_guard import (
    assert_dry_run_safe,
    assert_no_order_path_when_disabled,
    build_dry_run_report,
    get_effective_trading_mode,
    is_effective_ordering_disabled,
)


@pytest.fixture
def base_config(tmp_path: Path):
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
""")
    (tmp_path / "config" / "default.yaml").write_text("project:\n  name: test")
    return load_config(str(tmp_path / "config"))


def test_default_real_order_impossible(base_config):
    assert is_effective_ordering_disabled(base_config)
    report = build_dry_run_report(base_config)
    assert report["real_orders_impossible"] is True


def test_dry_run_violation(base_config):
    base_config.safety.dry_run = True
    base_config.connector.order_gateway_enabled = True
    with pytest.raises(DryRunViolationError):
        assert_dry_run_safe(base_config)


def test_disable_all_orders_violation(base_config):
    base_config.safety.disable_all_orders = True
    base_config.connector.order_gateway_enabled = True
    with pytest.raises(OrderPathDisabledError):
        assert_no_order_path_when_disabled(base_config)


def test_force_paper_mode_overrides(base_config):
    base_config.safety.force_paper_mode = True
    base_config.runtime.trading_mode = "live"
    effective = get_effective_trading_mode(base_config)
    assert effective.value == "paper"
