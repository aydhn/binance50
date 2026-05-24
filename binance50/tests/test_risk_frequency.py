from datetime import datetime, timedelta

import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.risk.frequency import (
    check_candidate_frequency,
    check_same_direction_frequency,
    check_total_review_frequency,
)


@pytest.fixture
def test_config():
    return AppConfig()


def test_check_candidate_frequency(test_config):
    test_config.risk.frequency.max_risk_reviews_per_symbol_per_hour = 2
    now = datetime.utcnow()
    df = pd.DataFrame(
        [
            {"symbol": "BTCUSDT", "open_time": now},
            {"symbol": "BTCUSDT", "open_time": now - timedelta(minutes=10)},
            {"symbol": "BTCUSDT", "open_time": now - timedelta(minutes=20)},
        ]
    )
    comp = check_candidate_frequency("BTCUSDT", now, df, test_config)
    assert comp.passed is False


def test_check_same_direction_frequency(test_config):
    test_config.risk.frequency.max_same_direction_candidates_per_symbol_per_hour = 1
    df = pd.DataFrame(
        [
            {"symbol": "BTCUSDT", "direction": "bullish"},
            {"symbol": "BTCUSDT", "direction": "bullish"},
        ]
    )
    comp = check_same_direction_frequency("BTCUSDT", "bullish", df, test_config)
    assert comp.passed is False


def test_check_total_review_frequency(test_config):
    test_config.risk.frequency.max_risk_reviews_total_per_hour = 1
    df = pd.DataFrame([1, 2])
    comp = check_total_review_frequency(df, test_config)
    assert comp.passed is False
