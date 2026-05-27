import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_blending_guard import assert_ml_blending_config_safe, assert_no_live_paper_execution_intent
from binance50.core.exceptions import MLBlendingSafetyError
import json

def test_default_config_safe():
    config = AppConfig()
    assert_ml_blending_config_safe(config) # Should not raise

def test_execution_intent_error():
    with pytest.raises(MLBlendingSafetyError):
        assert_no_live_paper_execution_intent({"execution_buy": True})
