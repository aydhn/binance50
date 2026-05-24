import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskConfigError
from binance50.safety.risk_guard import assert_risk_config_safe, build_risk_safety_report


@pytest.fixture
def test_config():
    return AppConfig()


def test_assert_risk_config_safe_defaults(test_config):
    # Should not raise exception
    assert_risk_config_safe(test_config)


def test_assert_risk_config_execution_forbidden(test_config):
    test_config.risk.execution_forbidden = False
    with pytest.raises(RiskConfigError):
        assert_risk_config_safe(test_config)


def test_assert_risk_config_real_balance(test_config):
    test_config.risk.account.allow_real_balance_fetch = True
    with pytest.raises(RiskConfigError):
        assert_risk_config_safe(test_config)


def test_assert_risk_config_position_fields(test_config):
    test_config.risk.position_risk.produce_order_quantity = True
    with pytest.raises(
        ValueError
    ):  # Actually fails model validation first due to our Pydantic validator
        test_config.risk.position_risk.validate_safety()


def test_build_risk_safety_report(test_config):
    report = build_risk_safety_report(test_config)
    assert report["execution_forbidden"] is True
