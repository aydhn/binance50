import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class MLBlendingIntegrationContract(BaseModel):
    contract_id: str
    version: str = "1.0"
    sandbox_only: bool = True
    production_write_forbidden: bool = True
    allowed_inputs: list[str] = Field(
        default_factory=lambda: ["ml_inference", "signal_scoring", "regime", "risk"]
    )
    forbidden_outputs: list[str] = Field(
        default_factory=lambda: [
            "order_id",
            "quantity",
            "leverage",
            "entry_price",
            "stop_loss",
            "take_profit",
            "execution_intent",
            "paper_intent",
            "live_intent",
            "production_signal_candidate",
            "production_risk_assessment",
        ]
    )
    required_guards: list[str] = Field(
        default_factory=lambda: [
            "ml_blending_guard",
            "ml_blending_leakage_guard",
            "ml_blending_integration_guard",
        ]
    )
    future_phase: str = "Phase 26"
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_ml_blending_integration_contract(config: AppConfig) -> MLBlendingIntegrationContract:
    return MLBlendingIntegrationContract(contract_id="ml_blending_contract_v1")


def validate_ml_blending_integration_contract(
    contract: MLBlendingIntegrationContract, config: AppConfig
) -> None:
    if not contract.sandbox_only:
        raise ValueError("Contract must be sandbox only")
    if not contract.production_write_forbidden:
        raise ValueError("Production write must be forbidden")


def export_ml_blending_integration_contract(
    contract: MLBlendingIntegrationContract, path: Path
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(contract.model_dump(), f, indent=2)
    return path
