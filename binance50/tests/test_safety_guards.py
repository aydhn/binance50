import pytest

from binance50.config.loader import load_config
from binance50.core.exceptions import LiveTradingBlockedError, SafetyError
from binance50.safety.live_guard import assert_live_trading_allowed
from binance50.safety.mode_guard import validate_mode_consistency


def test_paper_mode_safe():
    config = load_config()
    # local_paper_spot defaults
    validate_mode_consistency(config)


def test_live_guard_blocks_by_default(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_live")
    # Need to disable force paper mode to even allow config to load with LIVE mode
    # But actually, LiveTradingBlockedError is what we want from the live guard.
    config = load_config()
    with pytest.raises(LiveTradingBlockedError):
        assert_live_trading_allowed(config)


def test_mode_consistency_invalid(monkeypatch):
    monkeypatch.setenv("BINANCE50_TRADING_MODE", "testnet")
    # local_paper_spot doesn't allow TESTNET mode
    config = load_config()
    with pytest.raises(SafetyError):
        validate_mode_consistency(config)
