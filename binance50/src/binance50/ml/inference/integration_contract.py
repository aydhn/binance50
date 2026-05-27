from typing import Any, Dict, List
from pathlib import Path
import json
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.core.exceptions import MLSandboxIntegrationError

class MLSignalIntegrationContract(BaseModel):
    contract_id: str
    version: str
    allowed_input_fields: List[str]
    forbidden_output_fields: List[str]
    sandbox_only: bool
    production_write_forbidden: bool
    required_guards: List[str]
    future_phase: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

def build_ml_signal_integration_contract(config: AppConfig) -> MLSignalIntegrationContract:
    return MLSignalIntegrationContract(
        contract_id="ml_signal_contract_v1",
        version="1.0.0",
        allowed_input_fields=["model_id", "symbol", "interval", "predicted_label", "confidence", "probabilities"],
        forbidden_output_fields=["order_id", "quantity", "leverage", "entry_price", "stop_loss", "take_profit", "live", "paper", "execution_intent"],
        sandbox_only=True,
        production_write_forbidden=True,
        required_guards=[
            "assert_signal_auto_write_forbidden",
            "assert_risk_auto_write_forbidden",
            "assert_sandbox_outputs_blocked",
            "assert_no_production_signal_candidate",
            "assert_no_production_risk_assessment"
        ],
        future_phase="Phase 25/26"
    )

def validate_integration_contract(contract: MLSignalIntegrationContract, config: AppConfig) -> None:
    if not contract.sandbox_only or not contract.production_write_forbidden:
        raise MLSandboxIntegrationError("Phase 24 production write is forbidden")

    expected_forbidden = {"order_id", "quantity", "leverage", "entry_price", "stop_loss", "take_profit", "live", "paper", "execution_intent"}
    if not expected_forbidden.issubset(set(contract.forbidden_output_fields)):
        raise MLSandboxIntegrationError("Contract missing required forbidden output fields")

def export_integration_contract(contract: MLSignalIntegrationContract, path: Path) -> Path:
    if path.is_dir():
        path = path / f"{contract.contract_id}.json"

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(contract.model_dump(), f, indent=2)
    return path
