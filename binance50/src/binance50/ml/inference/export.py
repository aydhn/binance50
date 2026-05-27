import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from binance50.ml.inference.models import MLInferenceRunResult, MLPredictionRow

def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def export_ml_inference_summary_to_json(result: MLInferenceRunResult, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump({"run_id": result.run_id, "status": result.status}, f)
    return path

def export_predictions_to_parquet(predictions: List[MLPredictionRow], path: Path) -> Path:
    _ensure_dir(path)
    df = pd.DataFrame([p.model_dump() for p in predictions])
    if not df.empty:
        df.to_parquet(path)
    return path

def export_prediction_preview_to_csv(predictions: List[MLPredictionRow], path: Path, rows: int = 1000) -> Path:
    _ensure_dir(path)
    df = pd.DataFrame([p.model_dump() for p in predictions[:rows]])
    if not df.empty:
        df.to_csv(path, index=False)
    return path

def export_probability_report_to_json(report: Any, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump(report.model_dump() if report else {}, f)
    return path

def export_calibration_check_to_json(report: Any, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump(report.model_dump() if report else {}, f)
    return path

def export_threshold_sweep_to_csv(report: Any, path: Path) -> Path:
    _ensure_dir(path)
    if report and report.rows:
        df = pd.DataFrame([r.model_dump() for r in report.rows])
        df.to_csv(path, index=False)
    return path

def export_distribution_report_to_json(report: Any, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump(report.model_dump() if report else {}, f)
    return path

def export_drift_report_to_json(report: Any, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump(report.model_dump() if report else {}, f)
    return path

def export_sandbox_outputs_to_json(result: MLInferenceRunResult, path: Path) -> Path:
    _ensure_dir(path)
    outputs = result.sandbox_outputs or {}
    data = {
        "signals": [s.model_dump() for s in outputs.get("signals", [])],
        "risks": [r.model_dump() for r in outputs.get("risks", [])]
    }
    with open(path, "w") as f:
        json.dump(data, f)
    return path

def export_inference_manifest_to_json(manifest: Any, path: Path) -> Path:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump(manifest.model_dump() if manifest else {}, f)
    return path
