import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_calibration_guard import (
    assert_calibration_config_safe, assert_calibrator_not_fit_on_test
)

class MockReport:
    calibration_split = "test"

def test_ml_calibration_guard():
    config = AppConfig()
    assert_calibration_config_safe(config)

    config.ml_training.calibration.fit_calibrator_on_test_forbidden = False
    with pytest.raises(ValueError, match="fit_calibrator_on_test_forbidden must be True"):
        assert_calibration_config_safe(config)

    with pytest.raises(ValueError, match="Calibrator fit on test set"):
        assert_calibrator_not_fit_on_test(MockReport())
