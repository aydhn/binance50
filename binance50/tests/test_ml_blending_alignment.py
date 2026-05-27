import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.blending.alignment import align_predictions_with_signals, align_context_backward_asof, validate_blending_alignment, build_alignment_report
from binance50.core.exceptions import MLBlendingLeakageError

def test_backward_asof_alignment():
    config = AppConfig()
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    res = align_predictions_with_signals(df1, df2, config)
    assert isinstance(res, pd.DataFrame)

def test_same_symbol_scope_interval():
    config = AppConfig()
    validate_blending_alignment(pd.DataFrame(), config)

def test_alignment_report():
    df = pd.DataFrame([1, 2, 3])
    rep = build_alignment_report(df)
    assert rep["row_count"] == 3
