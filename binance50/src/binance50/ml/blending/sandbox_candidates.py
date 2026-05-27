from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.ml.blending.models import (
    MLBlendBreakdown,
    MLBlendedSandboxCandidate,
    MLBlendingIntent,
    MLBlendOutputStatus,
)


def build_blended_sandbox_candidate(
    row: Any,
    score: float,
    proba: float,
    breakdown: MLBlendBreakdown,
    explanation: str,
    config: AppConfig,
) -> MLBlendedSandboxCandidate:
    return MLBlendedSandboxCandidate(
        blended_candidate_id="mock_id",
        symbol=getattr(row, "symbol", "UNKNOWN"),
        market_scope=getattr(row, "market_scope", "spot"),
        interval=getattr(row, "interval", "1m"),
        open_time=getattr(row, "open_time", 0),
        close_time=getattr(row, "close_time", 0),
        direction=1 if score > 50 else -1,
        blended_score=score,
        blended_probability=proba,
        confidence=abs(proba - 0.5) * 2,
        status=MLBlendOutputStatus.sandbox_only,
        intent=MLBlendingIntent.sandbox_only,
        blocked_from_signal_engine=True,
        blocked_from_risk_engine=True,
        blocked_from_execution=True,
        breakdown=breakdown,
        explanation=explanation,
    )


def validate_blended_sandbox_candidate(
    candidate: MLBlendedSandboxCandidate, config: AppConfig
) -> None:
    if not candidate.blocked_from_signal_engine:
        raise ValueError("Must be blocked from signal engine")
    if not candidate.blocked_from_risk_engine:
        raise ValueError("Must be blocked from risk engine")
    if not candidate.blocked_from_execution:
        raise ValueError("Must be blocked from execution")


def candidates_to_dataframe(candidates: list[MLBlendedSandboxCandidate]) -> pd.DataFrame:
    return pd.DataFrame([c.model_dump() for c in candidates])


def dataframe_to_candidates(df: pd.DataFrame) -> list[MLBlendedSandboxCandidate]:
    return [MLBlendedSandboxCandidate(**row.to_dict()) for _, row in df.iterrows()]
