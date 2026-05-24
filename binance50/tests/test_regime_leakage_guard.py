import pandas as pd
import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeLeakageError
from binance50.safety.regime_leakage_guard import assert_no_regime_lookahead


def test_leakage_guard():
    config = AppConfig()
    df = pd.DataFrame({"future_return": [0.1]})
    with pytest.raises(RegimeLeakageError):
        assert_no_regime_lookahead(df, config)
