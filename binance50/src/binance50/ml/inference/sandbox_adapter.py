from typing import Any, Dict, List
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.ml.inference.models import MLPredictionRow, MLSandboxOutputStatus, MLInferenceIntent
from binance50.core.exceptions import MLSandboxIntegrationError

class MLSandboxSignalCandidate(BaseModel):
    sandbox_id: str
    source_prediction_id: str
    model_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: str
    predicted_label: str
    confidence: float
    probability_snapshot: Dict[str, float]
    status: MLSandboxOutputStatus = MLSandboxOutputStatus.SANDBOX_ONLY
    intent: MLInferenceIntent = MLInferenceIntent.RESEARCH_ONLY
    blocked_from_signal_engine: bool = True
    explanation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLSandboxRiskContext(BaseModel):
    sandbox_id: str
    source_prediction_id: str
    model_id: str
    confidence: float
    calibration_status: str
    drift_warnings: List[str] = Field(default_factory=list)
    status: MLSandboxOutputStatus = MLSandboxOutputStatus.SANDBOX_ONLY
    intent: MLInferenceIntent = MLInferenceIntent.RESEARCH_ONLY
    blocked_from_risk_engine: bool = True
    explanation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MLSandboxAdapter:
    def build_sandbox_signal_candidates(self, predictions: List[MLPredictionRow], reports: Dict[str, Any], config: AppConfig) -> List[MLSandboxSignalCandidate]:
        if not config.ml_inference.sandbox_integration.create_ml_signal_candidate_sandbox:
            return []

        candidates = []
        for p in predictions:
            candidates.append(MLSandboxSignalCandidate(
                sandbox_id=f"sandbox_sig_{p.prediction_id}",
                source_prediction_id=p.prediction_id,
                model_id=p.model_id,
                symbol=p.symbol,
                market_scope=p.market_scope,
                interval=p.interval,
                open_time=p.open_time,
                predicted_label=p.predicted_label,
                confidence=p.confidence or 0.0,
                probability_snapshot=p.probabilities or {},
                intent=MLInferenceIntent.RESEARCH_ONLY,
                blocked_from_signal_engine=True,
                explanation="Generated in ML Sandbox, isolated from production signal engine."
            ))
        return candidates

    def build_sandbox_risk_context(self, predictions: List[MLPredictionRow], reports: Dict[str, Any], config: AppConfig) -> List[MLSandboxRiskContext]:
        if not config.ml_inference.sandbox_integration.create_ml_risk_context_sandbox:
            return []

        drift_rep = reports.get("drift")
        drift_warnings = getattr(drift_rep, "warnings", []) if drift_rep else []

        cal_rep = reports.get("calibration")
        cal_status = getattr(cal_rep, "calibration_status", "unknown") if cal_rep else "unknown"

        contexts = []
        for p in predictions:
            contexts.append(MLSandboxRiskContext(
                sandbox_id=f"sandbox_risk_{p.prediction_id}",
                source_prediction_id=p.prediction_id,
                model_id=p.model_id,
                confidence=p.confidence or 0.0,
                calibration_status=cal_status,
                drift_warnings=drift_warnings,
                intent=MLInferenceIntent.RESEARCH_ONLY,
                blocked_from_risk_engine=True,
                explanation="Generated in ML Sandbox, isolated from production risk engine."
            ))
        return contexts

    def validate_sandbox_outputs(self, outputs: Dict[str, List[Any]], config: AppConfig) -> None:
        for cat, items in outputs.items():
            for item in items:
                if not getattr(item, "explanation", None):
                    raise MLSandboxIntegrationError(f"Explanation required for {cat} sandbox output")
                if hasattr(item, "order_id") or hasattr(item, "quantity"):
                    raise MLSandboxIntegrationError("Order intent detected in sandbox output")

    def block_production_writes(self, outputs: Dict[str, List[Any]], config: AppConfig) -> None:
        for item in outputs.get("signals", []):
            if not item.blocked_from_signal_engine:
                raise MLSandboxIntegrationError("Sandbox signal candidate must be blocked from production signal engine")

        for item in outputs.get("risks", []):
            if not item.blocked_from_risk_engine:
                raise MLSandboxIntegrationError("Sandbox risk context must be blocked from production risk engine")
