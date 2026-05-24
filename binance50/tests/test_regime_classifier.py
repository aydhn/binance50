import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.classifier import RegimeClassifier
from binance50.regimes.models import RegimeMethod, RegimeRunRequest


def test_classifier_orchestration():
    config = AppConfig()
    classifier = RegimeClassifier(config)

    df = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT"],
            "open_time": [1000, 2000],
            "close": [100, 110],
            "ADX": [30.0, 30.0],
        }
    )

    req = RegimeRunRequest(
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        input_dataset_name="test",
        method=RegimeMethod.rule_based,
        request_id="req1",
    )

    result = classifier.classify(df, req)
    assert result.success
    assert len(result.classifications) == 2
