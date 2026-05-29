import pandas as pd

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import (
    PortfolioCandidateStatus,
    PortfolioSelectedSandboxCandidate,
)


def enforce_selection_constraints(
    candidates: list[PortfolioSelectedSandboxCandidate], config: AppConfig
) -> list[PortfolioSelectedSandboxCandidate]:
    e_config = config.portfolio_sandbox.exposure

    selected = []
    symbol_counts = {}
    interval_counts = {}
    direction_counts = {}

    for cand in candidates:
        if len(selected) >= e_config.max_candidates_selected:
            break

        sym_count = symbol_counts.get(cand.symbol, 0)
        if sym_count >= e_config.max_candidates_per_symbol:
            continue

        int_count = interval_counts.get(cand.interval, 0)
        if int_count >= e_config.max_candidates_per_interval:
            continue

        dir_count = direction_counts.get(cand.direction, 0)
        if dir_count >= e_config.max_candidates_same_direction:
            continue

        # Select it
        cand.selected = True
        cand.status = PortfolioCandidateStatus.selected_sandbox
        selected.append(cand)

        # Update counts
        symbol_counts[cand.symbol] = sym_count + 1
        interval_counts[cand.interval] = int_count + 1
        direction_counts[cand.direction] = dir_count + 1

    return selected


def mark_non_selected_candidates(
    all_candidates: list[PortfolioSelectedSandboxCandidate],
    selected: list[PortfolioSelectedSandboxCandidate],
):
    selected_ids = {c.candidate_id for c in selected}
    for cand in all_candidates:
        if cand.candidate_id not in selected_ids:
            cand.selected = False
            cand.status = PortfolioCandidateStatus.rejected


def validate_selected_candidates(
    candidates: list[PortfolioSelectedSandboxCandidate], config: AppConfig
) -> None:
    from binance50.core.exceptions import PortfolioSelectionError

    if config.portfolio_sandbox.sandbox_output.require_blocked_flags:
        for c in candidates:
            if not c.blocked_from_signal_engine:
                raise PortfolioSelectionError("Must be blocked from signal engine")
            if not c.blocked_from_risk_engine:
                raise PortfolioSelectionError("Must be blocked from risk engine")
            if not c.blocked_from_paper_engine:
                raise PortfolioSelectionError("Must be blocked from paper engine")
            if not c.blocked_from_live_engine:
                raise PortfolioSelectionError("Must be blocked from live engine")
            if not c.blocked_from_execution:
                raise PortfolioSelectionError("Must be blocked from execution")

    if config.portfolio_sandbox.sandbox_output.require_no_order_intent:
        for c in candidates:
            if c.intent.value in ["order", "execution", "live", "paper"]:
                raise PortfolioSelectionError("Order intent detected in selected candidate")


def select_top_candidates(
    ranked_candidates: list[PortfolioSelectedSandboxCandidate], config: AppConfig
) -> list[PortfolioSelectedSandboxCandidate]:
    # Ranked candidates are already sorted descending by portfolio_score
    selected = enforce_selection_constraints(ranked_candidates, config)

    # Assign rank
    for i, c in enumerate(selected):
        c.rank = i + 1

    mark_non_selected_candidates(ranked_candidates, selected)
    validate_selected_candidates(selected, config)

    return selected


def selected_candidates_to_dataframe(
    candidates: list[PortfolioSelectedSandboxCandidate],
) -> pd.DataFrame:
    data = []
    for c in candidates:
        data.append(
            {
                "selected_id": c.selected_id,
                "candidate_id": c.candidate_id,
                "symbol": c.symbol,
                "market_scope": c.market_scope,
                "interval": c.interval,
                "direction": c.direction,
                "rank": c.rank,
                "portfolio_score": c.portfolio_score,
                "hypothetical_notional_usdt": c.hypothetical_notional_usdt,
                "intent": c.intent.value,
            }
        )
    return pd.DataFrame(data)
