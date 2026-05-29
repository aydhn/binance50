import pytest
import pandas as pd
from binance50.safety.portfolio_correlation_guard import assert_no_future_columns_in_correlation_data
from binance50.core.exceptions import PortfolioCorrelationError

def test_assert_no_future_columns_in_correlation_data():
    df = pd.DataFrame({"target": [1, 2]})
    with pytest.raises(PortfolioCorrelationError, match="Future column target detected"):
        assert_no_future_columns_in_correlation_data(df)
