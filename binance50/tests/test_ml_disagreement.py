import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.disagreement import compute_model_disagreement, compute_signal_model_disagreement, compute_pairwise_disagreement, classify_high_disagreement

def test_compute_model_disagreement():
    config = AppConfig()
    rep = compute_model_disagreement({}, config)
    assert rep.model_disagreement_rate == 0.0

def test_compute_signal_model_disagreement():
    config = AppConfig()
    res = compute_signal_model_disagreement([], config)
    assert res["rate"] == 0.0

def test_classify_high_disagreement():
    config = AppConfig()
    assert not classify_high_disagreement(None, config)
