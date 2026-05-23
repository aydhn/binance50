from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate


class SignalCalibrationReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    mode: str
    calibration_training_deferred: bool
    brier_score_supported: bool
    reliability_bins: int
    expected_calibration_error_supported: bool
    sample_count: int
    metrics: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)


def build_calibration_placeholder_report(config: AppConfig) -> SignalCalibrationReport:
    return SignalCalibrationReport(
        mode=config.signals.calibration.mode,
        calibration_training_deferred=config.signals.calibration.calibration_training_deferred,
        brier_score_supported=config.signals.calibration.brier_score_supported,
        reliability_bins=config.signals.calibration.reliability_bins,
        expected_calibration_error_supported=config.signals.calibration.expected_calibration_error_supported,
        sample_count=0,
        metrics=None,
        warnings=[
            "Calibration training is deferred to Phase 15/16.",
            "Real calibration requires realized labels from backtests or live trading.",
            "Placeholder metrics only."
        ]
    )


def compute_brier_score_if_labels_available(scored_candidates: list[ScoredSignalCandidate], realized_labels: list[int] | None = None) -> float | None:
    if not realized_labels or len(scored_candidates) != len(realized_labels):
        return None

    try:
        import numpy as np
        preds = np.array([c.score / 100.0 for c in scored_candidates])
        labels = np.array(realized_labels)
        brier_score = np.mean((preds - labels) ** 2)
        return float(brier_score)
    except ImportError:
        return None


def compute_reliability_bins_if_labels_available(scored_candidates: list[ScoredSignalCandidate], realized_labels: list[int] | None = None, bins: int = 10) -> dict[str, Any] | None:
    if not realized_labels or len(scored_candidates) != len(realized_labels):
        return None

    try:
        import numpy as np
        preds = np.array([c.score / 100.0 for c in scored_candidates])
        labels = np.array(realized_labels)

        bin_edges = np.linspace(0.0, 1.0, bins + 1)
        bin_indices = np.digitize(preds, bin_edges) - 1
        bin_indices[bin_indices == bins] = bins - 1

        bin_sums = np.bincount(bin_indices, minlength=bins)
        bin_true = np.bincount(bin_indices, weights=labels, minlength=bins)
        bin_pred = np.bincount(bin_indices, weights=preds, minlength=bins)

        non_empty = bin_sums > 0
        bin_acc = np.zeros(bins)
        bin_conf = np.zeros(bins)

        bin_acc[non_empty] = bin_true[non_empty] / bin_sums[non_empty]
        bin_conf[non_empty] = bin_pred[non_empty] / bin_sums[non_empty]

        return {
            "bins": bins,
            "counts": bin_sums.tolist(),
            "accuracies": bin_acc.tolist(),
            "confidences": bin_conf.tolist()
        }
    except ImportError:
        return None


def compute_expected_calibration_error_if_labels_available(scored_candidates: list[ScoredSignalCandidate], realized_labels: list[int] | None = None, bins: int = 10) -> float | None:
    bins_data = compute_reliability_bins_if_labels_available(scored_candidates, realized_labels, bins)
    if not bins_data:
        return None

    import numpy as np
    counts = np.array(bins_data["counts"])
    accs = np.array(bins_data["accuracies"])
    confs = np.array(bins_data["confidences"])

    total = np.sum(counts)
    if total == 0:
        return 0.0

    ece = np.sum(counts * np.abs(accs - confs)) / total
    return float(ece)
