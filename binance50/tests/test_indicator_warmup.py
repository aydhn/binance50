import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import InsufficientHistoryError
from binance50.indicators.models import IndicatorBackend, IndicatorGroup, IndicatorSpec
from binance50.indicators.warmup import (
    assert_sufficient_history,
    compute_valid_row_mask,
    estimate_indicator_lookback,
    estimate_max_lookback,
    mark_warmup_rows,
    summarize_warmup,
)


def test_estimate_lookback():
    spec1 = IndicatorSpec("sma", IndicatorGroup.TREND, IndicatorBackend.NATIVE, {}, [], [], 20)
    spec2 = IndicatorSpec("ema", IndicatorGroup.TREND, IndicatorBackend.NATIVE, {}, [], [], 50)

    assert estimate_indicator_lookback(spec1) == 20
    assert estimate_max_lookback([spec1, spec2]) == 50
    assert estimate_max_lookback([]) == 0


def test_mark_warmup_rows():
    df = pd.DataFrame({"open_time": [1, 2, 3, 4, 5]})
    marked = mark_warmup_rows(df, 2)
    assert "is_warmup" in marked.columns
    assert marked["is_warmup"].tolist() == [True, True, False, False, False]

    marked2 = mark_warmup_rows(df, 10)
    assert marked2["is_warmup"].tolist() == [True, True, True, True, True]


def test_compute_valid_row_mask():
    df = pd.DataFrame({"col1": [None, 1, 2, 3], "col2": [None, None, 2, 3]})

    mask = compute_valid_row_mask(df, ["col1", "col2"], 0.5)
    assert mask.tolist() == [False, False, True, True]


def test_summarize_warmup():
    df = pd.DataFrame({"open_time": [100, 200, 300, 400], "col1": [None, 1, 2, 3]})

    summary = summarize_warmup(df, ["col1"], 1)
    assert summary["max_lookback"] == 1
    assert summary["warmup_rows"] == 1
    assert summary["valid_rows"] == 3
    assert summary["first_valid_times"]["col1"] == 200


def test_assert_sufficient_history():
    config = AppConfig()
    config.indicators.min_rows_required = 10

    df = pd.DataFrame({"open_time": range(15)})
    spec = IndicatorSpec("sma", IndicatorGroup.TREND, IndicatorBackend.NATIVE, {}, [], [], 5)

    # Should pass
    assert_sufficient_history(df, [spec], config)

    # Fail min rows
    df_small = pd.DataFrame({"open_time": range(5)})
    with pytest.raises(InsufficientHistoryError):
        assert_sufficient_history(df_small, [spec], config)

    # Fail max lookback
    df_lookback = pd.DataFrame({"open_time": range(15)})
    spec_long = IndicatorSpec("sma", IndicatorGroup.TREND, IndicatorBackend.NATIVE, {}, [], [], 20)
    with pytest.raises(InsufficientHistoryError):
        assert_sufficient_history(df_lookback, [spec_long], config)
