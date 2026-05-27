import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.diversity import compute_ensemble_diversity, compute_prediction_correlation, compute_diversity_score, classify_low_diversity

def test_compute_ensemble_diversity():
    config = AppConfig()
    rep = compute_ensemble_diversity({"m1": [], "m2": []}, config)
    assert rep.model_count == 2
    assert rep.diversity_score == 1.0

def test_classify_low_diversity():
    config = AppConfig()
    rep = compute_ensemble_diversity({"m1": []}, config)
    rep.diversity_score = 0.1
    assert classify_low_diversity(rep)
