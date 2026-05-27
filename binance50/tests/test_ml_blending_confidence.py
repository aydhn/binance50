import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.confidence import compute_blend_confidence, build_blend_confidence_report

class MockCandidate:
    confidence = 0.8

def test_compute_blend_confidence():
    assert compute_blend_confidence(MockCandidate()) == 0.8

def test_build_blend_confidence_report():
    config = AppConfig()
    rep = build_blend_confidence_report([MockCandidate()], config)
    assert rep.avg_blend_confidence == 0.5
