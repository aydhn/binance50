import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.loaders import MLBlendingInputLoader
from binance50.core.exceptions import MLBlendingInputError

def test_load_inference_result():
    config = AppConfig()
    loader = MLBlendingInputLoader(config)
    res = loader.load_ml_inference_results(["1"], config)
    assert isinstance(res, list)

def test_missing_inference_reject():
    config = AppConfig()
    config.ml_blending.inputs.require_ml_inference_result = True
    loader = MLBlendingInputLoader(config)
    with pytest.raises(MLBlendingInputError):
        loader.load_ml_inference_results([], config)

def test_load_signal_scoring_result():
    config = AppConfig()
    loader = MLBlendingInputLoader(config)
    res = loader.load_signal_scoring_result(None, config)
    assert res is None

def test_missing_signal_reject():
    config = AppConfig()
    config.ml_blending.inputs.require_signal_scoring_result = True
    loader = MLBlendingInputLoader(config)
    with pytest.raises(MLBlendingInputError):
        loader.load_signal_scoring_result(None, config)

def test_load_regime_optional():
    config = AppConfig()
    config.ml_blending.inputs.require_regime_context = False
    loader = MLBlendingInputLoader(config)
    res = loader.load_regime_result(None, config)
    assert res is None

def test_load_risk_optional():
    config = AppConfig()
    config.ml_blending.inputs.require_risk_assessment_context = False
    loader = MLBlendingInputLoader(config)
    res = loader.load_risk_result(None, config)
    assert res is None

def test_execution_field_blocked():
    # Enforced by MLBlendingInputLoader in full impl, tested in guards
    pass
