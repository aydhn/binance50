import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskLimitError
from binance50.risk.limits import (
    build_limit_report,
    check_global_exposure_placeholder,
    check_max_candidates_per_hour,
    check_signal_score_threshold,
    validate_global_risk_limits,
)


@pytest.fixture
def test_config():
    return AppConfig()


class DummyScoredSignal:
    def __init__(self, score):
        self.final_score = score


def test_validate_global_risk_limits(test_config):
    test_config.risk.global_limits.max_total_risk_pct = 6.0
    with pytest.raises(RiskLimitError):
        validate_global_risk_limits(test_config)


def test_check_signal_score_threshold(test_config):
    test_config.risk.global_limits.min_signal_score_for_risk_review = 65.0

    comp_pass = check_signal_score_threshold(DummyScoredSignal(70.0), test_config)
    assert comp_pass.passed is True

    comp_fail = check_signal_score_threshold(DummyScoredSignal(60.0), test_config)
    assert comp_fail.passed is False


def test_check_max_candidates_per_hour(test_config):
    test_config.risk.global_limits.max_candidates_per_hour = 2
    df = pd.DataFrame([1, 2, 3])
    comp = check_max_candidates_per_hour(df, test_config)
    assert comp.passed is False


def test_check_global_exposure_placeholder(test_config):
    test_config.risk.global_limits.max_total_risk_pct = 2.0
    ctx_pass = {"total_exposure_pct": 1.5}
    comp = check_global_exposure_placeholder(ctx_pass, test_config)
    assert comp.passed is True

    ctx_fail = {"total_exposure_pct": 2.5}
    comp_fail = check_global_exposure_placeholder(ctx_fail, test_config)
    assert comp_fail.passed is False


def test_build_limit_report(test_config):
    report = build_limit_report(test_config)
    assert "global_limits" in report
