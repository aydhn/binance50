import pytest

from binance50.config.models import AppConfig
from binance50.risk.notional import (
    check_max_notional,
    check_min_notional,
    estimate_hypothetical_notional_usdt,
    estimate_hypothetical_risk_pct,
    round_quantity_estimate_to_step_size,
    validate_notional_against_symbol_filters,
)


@pytest.fixture
def test_config():
    return AppConfig()


class DummyScoredSignal:
    pass


def test_notional_estimates(test_config):
    test_config.risk.position_risk.max_notional_per_candidate_usdt = 100.0
    notional = estimate_hypothetical_notional_usdt(DummyScoredSignal(), test_config)
    assert notional == 100.0

    risk_pct = estimate_hypothetical_risk_pct(notional, 1000.0, test_config)
    assert risk_pct == 10.0


def test_notional_checks(test_config):
    test_config.risk.position_risk.min_notional_usdt = 10.0
    test_config.risk.position_risk.max_notional_per_candidate_usdt = 100.0

    comp_min = check_min_notional(5.0, test_config)
    assert comp_min.passed is False

    comp_max = check_max_notional(150.0, test_config)
    assert comp_max.passed is False


def test_rounding_and_filters(test_config):
    assert round_quantity_estimate_to_step_size(1.2345, 0.01) == 1.23

    comp_filter = validate_notional_against_symbol_filters(100.0, None, test_config)
    assert comp_filter.passed is False  # default config rejects if missing metadata
