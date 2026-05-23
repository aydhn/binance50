import numpy as np
import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorQualityError
from binance50.indicators.quality import (
    assert_indicator_quality_passed,
    build_indicator_quality_report,
)


def test_indicator_quality_all_nan():
    config = AppConfig()
    df = pd.DataFrame({"ind1": [np.nan, np.nan, np.nan], "ind2": [1, 2, 3]})

    rep = build_indicator_quality_report(df, ["ind1", "ind2"], config)
    assert rep.status == "fail"
    assert len(rep.issues) == 1
    assert rep.issues[0].issue_type == "all_nan"

    with pytest.raises(IndicatorQualityError):
        assert_indicator_quality_passed(rep, config)


def test_indicator_quality_inf():
    config = AppConfig()
    df = pd.DataFrame({"ind1": [1, np.inf, 3], "ind2": [1, 2, 3]})

    rep = build_indicator_quality_report(df, ["ind1", "ind2"], config)
    assert rep.status == "fail"
    assert rep.issues[0].issue_type == "infinity_detected"


def test_indicator_quality_constant():
    config = AppConfig()
    config.indicators.quality.reject_constant_indicator = True

    df = pd.DataFrame({"ind1": [5, 5, 5], "ind2": [1, 2, 3]})

    rep = build_indicator_quality_report(df, ["ind1", "ind2"], config)
    assert rep.status == "fail"
    assert rep.issues[0].issue_type == "constant_values"


def test_indicator_quality_extreme():
    config = AppConfig()
    config.indicators.quality.extreme_zscore_threshold = 2.0

    df = pd.DataFrame(
        {
            "ind1": [1, 1, 1, 1, 1, 1, 1, 1, 100],  # std will be large but 100 will be high zscore
            "ind2": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        }
    )

    rep = build_indicator_quality_report(df, ["ind1", "ind2"], config)
    # Warning, so status might be pass
    assert rep.status == "pass"
    assert any(i.issue_type == "extreme_values" for i in rep.issues)
    assert "ind1" in rep.extreme_value_columns

    # Assert passes
    assert_indicator_quality_passed(rep, config)


def test_indicator_quality_pass():
    config = AppConfig()
    df = pd.DataFrame({"ind1": [1, 2, 3, 4, 5]})

    rep = build_indicator_quality_report(df, ["ind1"], config)
    assert rep.status == "pass"
    assert len(rep.issues) == 0
    assert_indicator_quality_passed(rep, config)
