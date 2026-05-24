import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import MTFLookaheadError
from binance50.indicators.mtf import (
    MTFAlignmentRequest,
    align_higher_tf_to_base,
    prepare_higher_tf_features,
)


def test_backward_asof_alignment(config: AppConfig):
    # Base: every minute
    base_times = pd.date_range("2023-01-01 10:00:00", periods=5, freq="min")
    base_df = pd.DataFrame({"open_time": base_times, "base_val": range(5)})

    # Higher: every 5 minutes
    # Closes at 10:00, 10:05
    pd.date_range("2023-01-01 09:55:00", periods=2, freq="5min")
    h_df = pd.DataFrame(
        {
            "close_time": [
                pd.Timestamp("2023-01-01 10:00:00"),
                pd.Timestamp("2023-01-01 10:05:00"),
            ],
            "is_closed": [True, True],
            "h_val": [100, 200],
        }
    )

    req = MTFAlignmentRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        base_interval="1m",
        higher_interval="5m",
        base_df_hash="x",
        higher_df_hash="y",
        tolerance_ms=5 * 60 * 1000,
        require_higher_tf_closed=True,
        alignment_method="asof_backward",
    )

    prep_h = prepare_higher_tf_features(h_df, "5m", config)
    res = align_higher_tf_to_base(base_df, prep_h, req, config)

    # 10:00 -> should match the 10:00 close from higher TF
    # 10:01 -> should match 10:00
    # 10:02 -> should match 10:00

    assert res.matched_rows == 5
    assert res.unmatched_rows == 0
    assert "mtf_5m_h_val" in res.aligned_df.columns
    assert res.aligned_df.iloc[0]["mtf_5m_h_val"] == 100
    assert res.aligned_df.iloc[4]["mtf_5m_h_val"] == 100


def test_future_alignment_blocked(config: AppConfig):
    # Setting field directly shouldn't be validated unless validate_assignment is true, so we just set it
    config.indicator_v2.mtf.disallow_forward_alignment = True

    req = MTFAlignmentRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        base_interval="1m",
        higher_interval="5m",
        base_df_hash="x",
        higher_df_hash="y",
        tolerance_ms=5 * 60 * 1000,
        require_higher_tf_closed=True,
        alignment_method="forward",
    )

    base_df = pd.DataFrame(
        {"open_time": pd.date_range("2023-01-01 10:00:00", periods=1, freq="min")}
    )
    h_df = pd.DataFrame({"close_time": [pd.Timestamp("2023-01-01 10:05:00")]})

    with pytest.raises(MTFLookaheadError):
        align_higher_tf_to_base(base_df, h_df, req, config)
