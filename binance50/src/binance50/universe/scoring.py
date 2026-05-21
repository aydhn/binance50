from binance50.config.models import UniverseConfig
from binance50.universe.blacklist import SymbolListPolicy
from binance50.universe.liquidity import liquidity_score
from binance50.universe.models import SymbolDecisionStatus, UniverseCandidate
from binance50.universe.spread import spread_score


def compute_liquidity_component(candidate: UniverseCandidate, config: UniverseConfig) -> float:
    if not candidate.liquidity:
        return 0.0
    return liquidity_score(candidate.liquidity, config)


def compute_spread_component(candidate: UniverseCandidate, config: UniverseConfig) -> float:
    if not candidate.spread:
        return 0.0
    return spread_score(candidate.spread, config.max_spread_bps)


def compute_filter_quality_component(candidate: UniverseCandidate) -> float:
    if not candidate.rule_quality:
        return 0.0
    return candidate.rule_quality.quality_score


def compute_stability_component(candidate: UniverseCandidate) -> float:
    if not candidate.ticker_24h:
        return 0.0
    # simple metric: extremely high price change lowers stability
    change_abs = float(abs(candidate.ticker_24h.price_change_percent))
    if change_abs > 50.0:
        return max(0.0, 100.0 - (change_abs - 50.0) * 2)
    return 100.0


def compute_preference_component(
    candidate: UniverseCandidate, config: UniverseConfig, whitelist_policy: SymbolListPolicy
) -> float:
    score = 0.0
    if candidate.symbol in whitelist_policy.symbols:
        score += 50.0
    if config.prefer_major_symbols and candidate.symbol in config.major_symbols:
        score += 50.0
    return min(100.0, score)


def compute_candidate_score(
    candidate: UniverseCandidate, config: UniverseConfig, whitelist_policy: SymbolListPolicy
) -> float:
    liq_score = compute_liquidity_component(candidate, config)
    spr_score = compute_spread_component(candidate, config)
    filt_score = compute_filter_quality_component(candidate)
    stab_score = compute_stability_component(candidate)
    pref_score = compute_preference_component(candidate, config, whitelist_policy)

    weights = config.scoring
    total_score = (
        liq_score * weights.liquidity_weight
        + spr_score * weights.spread_weight
        + filt_score * weights.filter_quality_weight
        + stab_score * weights.stability_weight
        + pref_score * weights.preference_weight
    )

    return total_score


def rank_candidates(
    candidates: list[UniverseCandidate], config: UniverseConfig
) -> list[UniverseCandidate]:
    def sort_key(c: UniverseCandidate) -> tuple[int, float, float, float, int, str]:
        is_accepted = 1 if c.decision_status == SymbolDecisionStatus.ACCEPTED else 0
        score = c.score
        quote_vol = float(c.liquidity.quote_volume_24h) if c.liquidity else 0.0
        # Negative spread so smaller spread comes first
        spread_bps = float(c.spread.spread_bps) if c.spread else float("inf")
        is_major = 1 if c.symbol in config.major_symbols else 0
        return (is_accepted, score, quote_vol, -spread_bps, is_major, c.symbol)

    return sorted(candidates, key=sort_key, reverse=True)
