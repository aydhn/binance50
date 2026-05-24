import pytest

from binance50.config.models import AppConfig
from binance50.risk.volatility import check_atr_pct, check_realized_vol_z, check_volatile_regime


@pytest.fixture
def test_config():
    return AppConfig()


def test_check_atr_pct(test_config):
    test_config.risk.volatility.max_atr_pct_for_candidate = 5.0
    comp = check_atr_pct({"vol_atr_14_pct": 6.0}, test_config)
    assert comp.passed is False

    comp2 = check_atr_pct({"vol_atr_14_pct": 4.0}, test_config)
    assert comp2.passed is True


def test_check_realized_vol_z(test_config):
    test_config.risk.volatility.max_realized_vol_z = 2.0
    comp = check_realized_vol_z({"vol_realized_vol_20_z": 3.0}, test_config)
    assert comp.passed is False


def test_check_volatile_regime(test_config):
    comp_vol = check_volatile_regime({"regime": "volatile"}, test_config)
    assert comp_vol.penalty == test_config.risk.volatility.volatile_regime_penalty

    comp_calm = check_volatile_regime({"regime": "calm"}, test_config)
    assert comp_calm.bonus == test_config.risk.volatility.calm_regime_bonus
