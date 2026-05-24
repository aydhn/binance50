import pytest

from binance50.config.models import AppConfig
from binance50.risk.liquidity import check_book_depth, check_quote_volume, check_spread_bps


@pytest.fixture
def test_config():
    return AppConfig()


def test_check_spread_bps(test_config):
    test_config.risk.liquidity.max_spread_bps = 10.0
    test_config.risk.liquidity.warning_spread_bps = 5.0

    comp1 = check_spread_bps(4.0, test_config)
    assert comp1.passed is True and comp1.penalty == 0

    comp2 = check_spread_bps(6.0, test_config)
    assert comp2.passed is True and comp2.penalty > 0

    comp3 = check_spread_bps(12.0, test_config)
    assert comp3.passed is False


def test_check_quote_volume(test_config):
    test_config.risk.liquidity.min_quote_volume_24h_usdt = 1000.0
    assert check_quote_volume(500.0, test_config).passed is False
    assert check_quote_volume(1500.0, test_config).passed is True


def test_check_book_depth(test_config):
    test_config.risk.liquidity.min_book_depth_notional_usdt = 100.0
    assert check_book_depth(50.0, test_config).passed is False
