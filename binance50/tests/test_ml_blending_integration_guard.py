import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_blending_integration_guard import assert_signal_write_forbidden, assert_blocked_flags_true
from binance50.core.exceptions import MLBlendingIntegrationError

def test_signal_write_forbidden():
    config = AppConfig()
    assert_signal_write_forbidden(config)

def test_blocked_flags_true():
    class MockCand:
        blocked_from_signal_engine = False
    with pytest.raises(MLBlendingIntegrationError):
        assert_blocked_flags_true([MockCand()])
