import pandas as pd

from binance50.config.models import AppConfig
from binance50.optimizer.splitters import (
    build_time_series_cv_splits,
    chronological_train_validation_test_split,
)


def test_chronological_split():
    config = AppConfig()
    df = pd.DataFrame({"close": range(1000)})
    train, val, test, meta = chronological_train_validation_test_split(df, config)
    assert len(train) == 600
    assert len(val) == 200
    assert len(test) == 200


def test_time_series_cv_splits():
    config = AppConfig()
    df = pd.DataFrame({"close": range(1000)})
    splits = build_time_series_cv_splits(df, config)
    assert len(splits) == 3
