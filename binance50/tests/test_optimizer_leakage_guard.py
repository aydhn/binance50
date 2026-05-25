import pandas as pd
import pytest

from binance50.safety.optimizer_leakage_guard import assert_no_future_columns


def test_target_column_hata():
    df = pd.DataFrame({"target": [1, 2]})
    with pytest.raises(ValueError):
        assert_no_future_columns(df)
