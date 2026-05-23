import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.signals.models import ConfluenceGroup
from binance50.safety.confluence_guard import assert_confluence_config_safe, assert_conflict_policy_safe, assert_confluence_groups_safe, build_confluence_safety_report

@pytest.fixture
def config():
    return AppConfig()

def test_assert_confluence_config_safe(config):
    assert_confluence_config_safe(config)
    config.signals.confluence.max_confluence_score = 150.0
    from binance50.core.exceptions import SignalConfigError
    with pytest.raises(SignalConfigError):
        assert_confluence_config_safe(config)

def test_assert_conflict_policy_safe(config):
    assert_conflict_policy_safe(config)
    config.signals.conflicts.max_conflict_penalty = 0.0
    from binance50.core.exceptions import SignalConfigError
    with pytest.raises(SignalConfigError):
        assert_conflict_policy_safe(config)

def test_assert_confluence_groups_safe(config):
    g1 = ConfluenceGroup(
        group_id="g1", symbol="BTCUSDT", market_scope="spot", interval="1m",
        open_time=0, direction="bullish", candidates=[], plugin_names=[], plugin_types=[],
        same_direction_count=2, opposite_direction_count=0, confluence_score=50.0, conflict_penalty=0.0
    )
    assert_confluence_groups_safe([g1], config)

    g2 = ConfluenceGroup(
        group_id="g2", symbol="BTCUSDT", market_scope="spot", interval="1m",
        open_time=0, direction="bullish", candidates=[], plugin_names=[], plugin_types=[],
        same_direction_count=2, opposite_direction_count=0, confluence_score=150.0, conflict_penalty=0.0
    )
    from binance50.core.exceptions import SignalConfluenceError
    with pytest.raises(SignalConfluenceError):
        assert_confluence_groups_safe([g2], config)

def test_build_confluence_safety_report(config):
    report = build_confluence_safety_report(config)
    assert report["confluence_config_safe"] is True
    assert report["conflict_policy_safe"] is True
    assert len(report["errors"]) == 0
