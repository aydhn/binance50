from datetime import datetime

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


def check_candidate_min_scores(
    candidate: PortfolioCandidateInput, config: AppConfig
) -> tuple[bool, str | None]:
    e_config = config.portfolio_sandbox.eligibility

    if candidate.signal_score is not None and candidate.signal_score < e_config.min_signal_score:
        return (
            False,
            f"Signal score {candidate.signal_score} below minimum {e_config.min_signal_score}",
        )

    if candidate.risk_score is not None and candidate.risk_score < e_config.min_risk_score:
        return False, f"Risk score {candidate.risk_score} below minimum {e_config.min_risk_score}"

    if (
        candidate.ml_blend_score is not None
        and candidate.ml_blend_score < e_config.min_ml_blend_score
    ):
        return (
            False,
            f"ML blend score {candidate.ml_blend_score} below minimum {e_config.min_ml_blend_score}",
        )

    return True, None


def check_candidate_staleness(
    candidate: PortfolioCandidateInput, current_time: datetime, config: AppConfig
) -> tuple[bool, str | None]:
    e_config = config.portfolio_sandbox.eligibility
    if not e_config.reject_stale_candidates:
        return True, None

    # Simplified staleness check based on time difference and interval
    # In a full implementation, you would convert interval string (e.g., '1m', '1h') to timedelta and check max_candidate_age_bars
    # For now, we perform a basic check if open_time is in the future or way too old.

    if candidate.open_time > current_time:
        return False, "Candidate open_time is in the future"

    # Placeholder for bar age check logic
    age_seconds = (current_time - candidate.open_time).total_seconds()
    # Simple heuristic: assuming 1m interval, 3 bars = 180s + buffer
    if candidate.interval == "1m" and age_seconds > e_config.max_candidate_age_bars * 60 + 10:
        return False, f"Candidate is stale (age > {e_config.max_candidate_age_bars} bars)"

    return True, None


def check_candidate_required_fields(
    candidate: PortfolioCandidateInput, config: AppConfig
) -> tuple[bool, str | None]:
    e_config = config.portfolio_sandbox.eligibility

    if e_config.reject_missing_symbol and not candidate.symbol:
        return False, "Missing symbol"

    if e_config.reject_missing_interval and not candidate.interval:
        return False, "Missing interval"

    if e_config.reject_missing_direction and not candidate.direction:
        return False, "Missing direction"

    return True, None


def reject_blocked_risk_candidates(
    candidate: PortfolioCandidateInput, config: AppConfig
) -> tuple[bool, str | None]:
    if config.portfolio_sandbox.eligibility.reject_blocked_risk:
        if candidate.risk_context and candidate.risk_context.get("blocked", False):
            return False, "Risk context indicates candidate is blocked"
    return True, None


def filter_eligible_candidates(
    candidates: list[PortfolioCandidateInput], config: AppConfig, current_time: datetime = None
) -> tuple[list[PortfolioCandidateInput], list[PortfolioCandidateInput]]:
    if not config.portfolio_sandbox.eligibility.enabled:
        return candidates, []

    if current_time is None:
        current_time = datetime.utcnow()

    eligible = []
    rejected = []

    for cand in candidates:
        passed, reason = check_candidate_required_fields(cand, config)
        if not passed:
            cand.metadata["rejection_reason"] = reason
            rejected.append(cand)
            continue

        passed, reason = check_candidate_staleness(cand, current_time, config)
        if not passed:
            cand.metadata["rejection_reason"] = reason
            rejected.append(cand)
            continue

        passed, reason = reject_blocked_risk_candidates(cand, config)
        if not passed:
            cand.metadata["rejection_reason"] = reason
            rejected.append(cand)
            continue

        passed, reason = check_candidate_min_scores(cand, config)
        if not passed:
            cand.metadata["rejection_reason"] = reason
            rejected.append(cand)
            continue

        if not config.portfolio_sandbox.eligibility.allow_research_only_candidates:
            if cand.metadata.get("intent") == "research_only":
                cand.metadata["rejection_reason"] = "Research-only candidates not allowed"
                rejected.append(cand)
                continue

        eligible.append(cand)

    return eligible, rejected


def build_eligibility_report(
    eligible: list[PortfolioCandidateInput], rejected: list[PortfolioCandidateInput]
) -> dict:
    return {
        "eligible_count": len(eligible),
        "rejected_count": len(rejected),
        "rejection_reasons": [cand.metadata.get("rejection_reason") for cand in rejected],
    }
