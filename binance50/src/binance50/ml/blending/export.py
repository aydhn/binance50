from pathlib import Path
from typing import Any

from binance50.ml.blending.integration_contract import MLBlendingIntegrationContract
from binance50.ml.blending.models import MLBlendingRunResult


def export_ml_blending_summary_to_json(result: MLBlendingRunResult, path: Path) -> Path:
    return path


def export_blended_candidates_to_parquet(candidates: list[Any], path: Path) -> Path:
    return path


def export_blended_candidates_preview_to_csv(
    candidates: list[Any], path: Path, rows: int = 1000
) -> Path:
    return path


def export_disagreement_report_to_json(report: Any, path: Path) -> Path:
    return path


def export_diversity_report_to_json(report: Any, path: Path) -> Path:
    return path


def export_confidence_report_to_json(report: Any, path: Path) -> Path:
    return path


def export_integration_contract_to_json(
    contract: MLBlendingIntegrationContract, path: Path
) -> Path:
    return path


def export_blending_quality_report_to_json(report: Any, path: Path) -> Path:
    return path
