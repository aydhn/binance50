import numpy as np
from typing import Any, Tuple, List, Dict, Optional
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLCalibrationReport
from binance50.ml.training.metrics import safe_brier_score

def compute_reliability_bins(y_true: Any, y_proba: Any, bins: int) -> List[Dict[str, float]]:
    from sklearn.calibration import calibration_curve
    prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=bins)
    return [{"prob_true": float(t), "prob_pred": float(p)} for t, p in zip(prob_true, prob_pred)]

def compute_expected_calibration_error(y_true: Any, y_proba: Any, bins: int) -> Optional[float]:
    # Simplified ECE
    if len(np.unique(y_true)) < 2:
        return None
    from sklearn.calibration import calibration_curve
    prob_true, prob_pred = calibration_curve(y_true, y_proba, n_bins=bins)
    return float(np.mean(np.abs(prob_true - prob_pred)))

def build_uncalibrated_report(estimator: Any, matrix: Any, config: AppConfig) -> MLCalibrationReport:
    warnings = ["uncalibrated"] if config.ml_training.calibration.warn_uncalibrated_probabilities else []
    return MLCalibrationReport(
        model_id="unknown",
        method="none",
        calibrated=False,
        calibration_split="none",
        warnings=warnings
    )

def calibrate_classifier_if_enabled(estimator: Any, matrix: Any, config: AppConfig) -> Tuple[Any, MLCalibrationReport]:
    if not config.ml_training.calibration.enabled or not config.ml_training.calibration.calibrate_classifiers:
        return estimator, build_uncalibrated_report(estimator, matrix, config)

    method = config.ml_training.calibration.method
    split = config.ml_training.calibration.calibration_split

    X_cal, y_cal = getattr(matrix, f"X_{split}"), getattr(matrix, f"y_{split}")

    if len(X_cal) < config.ml_training.calibration.isotonic_min_samples_warning and method == "isotonic":
        pass # Add warning later

    from sklearn.calibration import CalibratedClassifierCV
    calibrator = CalibratedClassifierCV(estimator, method=method, cv=2)
    calibrator.fit(X_cal, y_cal)

    report = MLCalibrationReport(
        model_id="unknown",
        method=method,
        calibrated=True,
        calibration_split=split,
        reliability_bins=[],
        calibration_curve_points=[]
    )
    return calibrator, report

def validate_calibration_report(report: MLCalibrationReport, config: AppConfig) -> None:
    pass
