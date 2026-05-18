import pytest

from binance50.config.loader import load_config
from binance50.core.enums import RuntimeEnvironment, TradingMode
from binance50.core.exceptions import InvalidTradingModeError, LiveTradingBlockedError
from binance50.safety.live_guard import check_live_trading_guard
from binance50.safety.mode_guard import check_mode_consistency


def test_paper_mode_safe():
    config = load_config()
    config.runtime.trading_mode = TradingMode.PAPER
    config.runtime.environment = RuntimeEnvironment.LOCAL

    # Should not raise any exceptions
    check_mode_consistency(config)
    check_live_trading_guard(config)


def test_live_guard_blocks_by_default():
    config = load_config()
    config.runtime.trading_mode = TradingMode.LIVE
    config.runtime.environment = RuntimeEnvironment.MAINNET

    # By default enable_live_trading and confirm_live_trading are False
    # Pydantic validation catches this first during instantiation if set that way,
    # but let's test the guard explicitly bypassing validation
    config.safety.enable_live_trading = False

    with pytest.raises(LiveTradingBlockedError):
        check_live_trading_guard(config)


def test_mode_consistency_invalid():
    config = load_config()
    config.runtime.trading_mode = TradingMode.TESTNET
    config.runtime.environment = RuntimeEnvironment.LOCAL
    # Need a profile mismatch or something to trigger mode inconsistency
    # local_paper_spot profile doesn't allow TESTNET mode

    with pytest.raises(InvalidTradingModeError):
        check_mode_consistency(config)
