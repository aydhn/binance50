import numpy as np
import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioCorrelationError
from binance50.portfolio.sandbox.correlation import PortfolioCorrelationReport


def assert_correlation_config_safe(config: AppConfig) -> None:
    c_config = config.portfolio_sandbox.correlation
    if c_config.reject_forward_returns and not c_config.use_returns:
        raise PortfolioCorrelationError(
            "Config mismatch: reject_forward_returns requires use_returns"
        )


def assert_no_forward_returns_for_correlation(metadata: dict) -> None:
    if metadata.get("contains_forward_returns", False):
        raise PortfolioCorrelationError("Forward returns detected in correlation metadata")


def assert_no_future_columns_in_correlation_data(df: pd.DataFrame) -> None:
    future_cols = ["target", "label", "future"]
    for c in future_cols:
        if c in df.columns:
            raise PortfolioCorrelationError(f"Future column {c} detected in correlation data")


def assert_correlation_matrix_valid(report: PortfolioCorrelationReport) -> None:
    matrix = report.correlation_matrix
    if matrix is not None:
        df = pd.DataFrame(matrix)
        if not np.allclose(df, df.T, equal_nan=True):
            raise PortfolioCorrelationError("Correlation matrix is not symmetric")


def build_portfolio_correlation_safety_report(config: AppConfig) -> dict:
    try:
        assert_correlation_config_safe(config)
        return {"status": "passed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
