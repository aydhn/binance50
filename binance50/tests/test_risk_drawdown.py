import pytest

from binance50.config.models import AppConfig
from binance50.risk.drawdown import (
    DrawdownSnapshot,
    build_empty_drawdown_snapshot,
    check_daily_loss_limit,
    check_monthly_loss_limit,
    check_weekly_loss_limit,
)


@pytest.fixture
def test_config():
    return AppConfig()


def test_drawdown_checks(test_config):
    test_config.risk.global_limits.max_daily_loss_pct = 1.0
    test_config.risk.global_limits.max_weekly_loss_pct = 3.0
    test_config.risk.global_limits.max_monthly_loss_pct = 6.0

    snapshot = DrawdownSnapshot(daily_loss_pct=2.0, weekly_loss_pct=4.0, monthly_loss_pct=7.0)

    assert check_daily_loss_limit(snapshot, test_config).passed is False
    assert check_weekly_loss_limit(snapshot, test_config).passed is False
    assert check_monthly_loss_limit(snapshot, test_config).passed is False


def test_empty_drawdown(test_config):
    snapshot = build_empty_drawdown_snapshot(test_config)
    assert check_daily_loss_limit(snapshot, test_config).passed is True
