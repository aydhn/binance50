import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioSimilarityReport(BaseModel):
    run_id: str
    candidate_count: int
    high_similarity_pairs: list[dict] = Field(default_factory=list)
    blocked_similarity_pairs: list[dict] = Field(default_factory=list)
    similarity_matrix_summary: dict | None = None
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def build_candidate_similarity_vectors(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> pd.DataFrame:
    s_config = config.portfolio_sandbox.similarity
    features = []
    ids = []

    for cand in candidates:
        ids.append(cand.candidate_id)
        vec = {}
        if "signal_score" in s_config.include_score_vector:
            vec["signal_score"] = cand.signal_score or 0.0
        if "risk_score" in s_config.include_score_vector:
            vec["risk_score"] = cand.risk_score or 0.0
        if "ml_blend_score" in s_config.include_score_vector:
            vec["ml_blend_score"] = cand.ml_blend_score or 0.0

        # Add metadata features if available and mapped
        if "volatility_risk" in s_config.include_score_vector and cand.risk_context:
            vec["volatility_risk"] = cand.risk_context.get("volatility_risk", 0.0)

        features.append(vec)

    return pd.DataFrame(features, index=ids)


def compute_candidate_cosine_similarity(vectors: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if vectors.empty:
        return pd.DataFrame()

    # Fill NAs
    vectors = vectors.fillna(0.0)

    # Compute cosine similarity
    try:
        from scipy.spatial.distance import pdist, squareform
    except ImportError:
        return pd.DataFrame(np.eye(len(vectors)), index=vectors.index, columns=vectors.index)
    try:
        dist_matrix = pdist(vectors.values, metric="cosine")
        sim_matrix = 1.0 - squareform(dist_matrix)
        # Handle nan resulting from zero vectors
        sim_matrix = np.nan_to_num(sim_matrix, nan=0.0)
        return pd.DataFrame(sim_matrix, index=vectors.index, columns=vectors.index)
    except Exception:
        # Fallback if scipy not available or errors
        return pd.DataFrame(np.eye(len(vectors)), index=vectors.index, columns=vectors.index)


def detect_high_similarity_candidates(
    candidates: list[PortfolioCandidateInput], similarity_matrix: pd.DataFrame, config: AppConfig
) -> list[dict]:
    high_sim = []
    s_config = config.portfolio_sandbox.similarity

    if similarity_matrix.empty:
        return high_sim

    c_ids = list(similarity_matrix.index)
    for i in range(len(c_ids)):
        for j in range(i + 1, len(c_ids)):
            sim = float(similarity_matrix.iloc[i, j])
            if sim >= s_config.similarity_threshold_warning:
                high_sim.append(
                    {
                        "candidate_1": c_ids[i],
                        "candidate_2": c_ids[j],
                        "similarity": sim,
                        "blocked": sim >= s_config.similarity_threshold_block,
                    }
                )
    return high_sim


def build_similarity_report(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioSimilarityReport:
    report = PortfolioSimilarityReport(run_id="unknown", candidate_count=len(candidates))

    if not config.portfolio_sandbox.similarity.enabled:
        return report

    vectors = build_candidate_similarity_vectors(candidates, config)
    sim_matrix = compute_candidate_cosine_similarity(vectors, config)

    high_sim = detect_high_similarity_candidates(candidates, sim_matrix, config)
    report.high_similarity_pairs = [p for p in high_sim if not p["blocked"]]
    report.blocked_similarity_pairs = [p for p in high_sim if p["blocked"]]

    if len(high_sim) > 0:
        report.warnings.append(f"Detected {len(high_sim)} highly similar candidate pairs.")

    return report
