from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


def build_deduplication_key(candidate: PortfolioCandidateInput) -> tuple:
    return (
        candidate.symbol,
        candidate.market_scope,
        candidate.interval,
        candidate.open_time,
        candidate.direction,
    )


def resolve_duplicate_candidates(
    duplicates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioCandidateInput:
    # Sort deterministically based on available scores, tie-break with candidate_id
    def sort_key(c: PortfolioCandidateInput):
        # We want the highest scores to win
        s_score = c.signal_score if c.signal_score is not None else -1.0
        r_score = c.risk_score if c.risk_score is not None else -1.0
        m_score = c.ml_blend_score if c.ml_blend_score is not None else -1.0
        combined = s_score + r_score + m_score
        return (combined, s_score, r_score, m_score, c.candidate_id)

    sorted_dups = sorted(duplicates, key=sort_key, reverse=True)
    winner = sorted_dups[0]

    # Store source_ids of losers in winner's metadata for traceability
    loser_ids = [c.candidate_id for c in sorted_dups[1:]]
    winner.metadata["deduplicated_from"] = loser_ids

    return winner


def deduplicate_candidates(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> list[PortfolioCandidateInput]:
    if not config.portfolio_sandbox.eligibility.reject_duplicate_symbol_direction_bar:
        return candidates

    grouped = {}
    for cand in candidates:
        key = build_deduplication_key(cand)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(cand)

    deduped = []
    for key, group in grouped.items():
        if len(group) == 1:
            deduped.append(group[0])
        else:
            deduped.append(resolve_duplicate_candidates(group, config))

    # Re-sort to maintain original order roughly, or sort deterministically
    return sorted(deduped, key=lambda c: c.candidate_id)


def build_deduplication_report(
    original: list[PortfolioCandidateInput], deduped: list[PortfolioCandidateInput]
) -> dict:
    return {
        "original_count": len(original),
        "deduplicated_count": len(deduped),
        "duplicates_removed": len(original) - len(deduped),
    }
