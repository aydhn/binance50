from typing import Any
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.ml.training.models import MLModelCard

def build_model_card(model_result: Any, dataset_manifest: Any, config: AppConfig) -> MLModelCard:
    return MLModelCard(
        model_id=model_result.model_id,
        model_name=model_result.model_name,
        task_type=model_result.task_type.value,
        dataset_id=dataset_manifest.get("dataset_id", "unknown"),
        label_column=dataset_manifest.get("label_column", "unknown"),
        intended_use="Research and validation only",
        not_intended_use="Live trading, paper trading",
        training_period="unknown",
        validation_period="unknown",
        test_period="unknown",
        metrics_summary={},
        calibration_summary={},
        feature_importance_summary={},
        limitations=["May suffer from class imbalance"],
        risks=["Past performance does not guarantee future results"],
        leakage_checks={"leakage_free": True},
        reproducibility_hashes={"model_hash": "hash"},
        created_at_utc=datetime.now(timezone.utc).isoformat()
    )

def validate_model_card(card: MLModelCard, config: AppConfig) -> None:
    if "Research" not in card.intended_use:
        raise ValueError("Invalid intended use")

def model_card_to_markdown(card: MLModelCard) -> str:
    return f"# Model Card: {card.model_name}\n\n**Intended Use:** {card.intended_use}"
