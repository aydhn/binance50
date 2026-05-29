import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.correlation import compute_correlation_matrix, detect_high_correlation_pairs
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType

def test_compute_correlation_matrix():
    config = AppConfig()
    config.portfolio_sandbox.correlation.min_periods = 1

    df = pd.DataFrame({
        "BTCUSDT": [0.01, 0.02, -0.01, 0.03],
        "ETHUSDT": [0.01, 0.02, -0.01, 0.02]
    })

    matrix = compute_correlation_matrix(df, config)
    assert not matrix.empty
    assert matrix.loc["BTCUSDT", "ETHUSDT"] > 0.9
