import pytest
import pandas as pd
from binance50.config.models import AppConfig
from binance50.ml.blending.weights import MLBlendWeightEngine
from binance50.ml.blending.ensemble import MLBlendingEngine

def test_blend_row():
    config = AppConfig()
    engine = MLBlendingEngine(config, MLBlendWeightEngine())
    row = pd.Series({"symbol": "BTCUSDT", "market_scope": "spot", "interval": "1m", "open_time": 0, "close_time": 0})
    cand = engine.blend_row(row, {})
    assert cand.symbol == "BTCUSDT"
    assert cand.blended_score == 50.0

def test_final_score_clamp():
    config = AppConfig()
    engine = MLBlendingEngine(config, MLBlendWeightEngine())
    score, proba = engine.compute_final_score({}, 60.0, config)
    assert score == 0.0
    assert proba == 0.5
