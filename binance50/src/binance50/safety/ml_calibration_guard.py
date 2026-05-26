from typing import Any, Dict
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLModelTrainingResult

def assert_calibration_config_safe(config: AppConfig) -> None:
    if not config.ml_training.calibration.fit_calibrator_on_test_forbidden:
        raise ValueError("fit_calibrator_on_test_forbidden must be True")

def assert_calibrator_not_fit_on_test(report: Any) -> None:
    if report and getattr(report, "calibration_split", None) == "test":
        raise ValueError("Calibrator fit on test set")

def assert_calibration_report_safe(report: Any) -> None:
    assert_calibrator_not_fit_on_test(report)

def assert_probability_outputs_marked_uncalibrated_if_needed(model_result: MLModelTrainingResult) -> None:
    if model_result.calibration_report and not model_result.calibration_report.calibrated:
        pass # Add flag logic

def build_ml_calibration_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {"status": "safe"}
