import pytest

from binance50.config.models import AppConfig
from binance50.risk.leverage import (
    check_futures_context_allowed,
    check_leverage_policy,
    estimate_leverage_context,
)


@pytest.fixture
def test_config():
    return AppConfig()


def test_check_futures_context_allowed(test_config):
    test_config.risk.futures.allow_usdm_futures_context = False
    comp = check_futures_context_allowed("futures", test_config)
    assert comp.passed is False

    test_config.risk.futures.allow_usdm_futures_context = True
    comp2 = check_futures_context_allowed("futures", test_config)
    assert comp2.passed is True


def test_estimate_leverage_context(test_config):
    test_config.risk.futures.default_leverage_for_estimate = 2
    ctx = estimate_leverage_context(None, test_config)
    assert ctx["estimated_leverage"] == 2


def test_check_leverage_policy(test_config):
    test_config.risk.futures.hard_max_leverage_allowed = 10
    test_config.risk.futures.max_leverage_for_estimate = 5
    test_config.risk.futures.reject_if_leverage_above_policy = True

    comp1 = check_leverage_policy(3, test_config)
    assert comp1.passed is True

    comp2 = check_leverage_policy(6, test_config)
    assert comp2.passed is False

    comp3 = check_leverage_policy(12, test_config)
    assert comp3.passed is False
