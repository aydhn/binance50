from pathlib import Path

import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import LiveUnlockError
from binance50.safety.live_guard import build_live_guard_report
from binance50.security.live_unlock import (
    assert_live_risk_ack,
    assert_live_unlock_phrase,
    build_live_unlock_report,
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


def test_default_blocked(base_config):
    report = build_live_unlock_report(base_config)
    assert report["live_blocked_by_unlock_guard"] is True


def test_missing_phrase_blocked(base_config, monkeypatch):
    monkeypatch.delenv("BINANCE50_LIVE_UNLOCK", raising=False)
    with pytest.raises(LiveUnlockError):
        assert_live_unlock_phrase(base_config)


def test_missing_risk_ack_blocked(base_config, monkeypatch):
    monkeypatch.delenv("BINANCE50_LIVE_RISK_ACK", raising=False)
    with pytest.raises(LiveUnlockError):
        assert_live_risk_ack(base_config)


def test_full_unlock(base_config, monkeypatch):
    monkeypatch.setenv("BINANCE50_LIVE_UNLOCK", base_config.safety.live_unlock_phrase_required)
    monkeypatch.setenv("BINANCE50_LIVE_RISK_ACK", base_config.safety.live_risk_ack_required)
    assert_live_unlock_phrase(base_config)
    assert_live_risk_ack(base_config)
    report = build_live_unlock_report(base_config)
    assert report["live_blocked_by_unlock_guard"] is False


def test_live_guard_blocked_by_default(base_config):
    report = build_live_guard_report(base_config)
    assert report["live_trading_blocked"] is True
