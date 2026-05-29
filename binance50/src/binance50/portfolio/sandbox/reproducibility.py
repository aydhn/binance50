import hashlib
import json

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import (
    PortfolioCandidateInput,
    PortfolioSelectedSandboxCandidate,
    PortfolioSelectionRunResult,
)


def compute_portfolio_config_hash(config: AppConfig) -> str:
    # A simplified hash of the relevant config
    config_dict = config.portfolio_sandbox.model_dump(mode="json")
    # Clean up non-deterministic keys if any
    config_str = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()


def compute_candidate_hash(candidate: PortfolioCandidateInput) -> str:
    # Build a stable dict
    data = {
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "signal_score": candidate.signal_score,
        "risk_score": candidate.risk_score,
        "ml_blend_score": candidate.ml_blend_score,
        "open_time": candidate.open_time.isoformat() if candidate.open_time else None,
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def compute_portfolio_selection_input_hash(
    inputs: list[PortfolioCandidateInput], config: AppConfig
) -> str:
    hashes = sorted([compute_candidate_hash(c) for c in inputs])
    config_hash = compute_portfolio_config_hash(config)
    combined = config_hash + ":" + ",".join(hashes)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_selected_set_hash(selected_candidates: list[PortfolioSelectedSandboxCandidate]) -> str:
    data = []
    for c in selected_candidates:
        data.append(
            {"selected_id": c.selected_id, "rank": c.rank, "portfolio_score": c.portfolio_score}
        )
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()


def compute_portfolio_selection_output_hash(result: PortfolioSelectionRunResult) -> str:
    return compute_selected_set_hash(result.selected_candidates)


def build_portfolio_reproducibility_report(
    result: PortfolioSelectionRunResult, config: AppConfig
) -> dict:
    return {
        "config_hash": compute_portfolio_config_hash(config),
        "input_hash": compute_portfolio_selection_input_hash(result.input_candidates, config),
        "output_hash": compute_portfolio_selection_output_hash(result),
    }


def assert_portfolio_selection_reproducible(
    result_a: PortfolioSelectionRunResult, result_b: PortfolioSelectionRunResult
) -> None:
    hash_a = compute_portfolio_selection_output_hash(result_a)
    hash_b = compute_portfolio_selection_output_hash(result_b)
    if hash_a != hash_b:
        from binance50.core.exceptions import PortfolioSandboxError

        raise PortfolioSandboxError(
            f"Reproducibility failed: output hashes differ {hash_a} != {hash_b}"
        )
