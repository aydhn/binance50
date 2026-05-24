import uuid
from enum import StrEnum

import pandas as pd
from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.exceptions import DivergenceDetectionError

from .pivots import PivotPoint, PivotType, detect_indicator_pivots, detect_price_pivots


class DivergenceType(StrEnum):
    regular_bullish = "regular_bullish"
    regular_bearish = "regular_bearish"
    hidden_bullish = "hidden_bullish"
    hidden_bearish = "hidden_bearish"


class DivergenceSignalCandidate(BaseModel):
    candidate_id: str
    symbol: str
    interval: str
    divergence_type: DivergenceType
    price_source: str
    indicator_source: str
    first_pivot_time: pd.Timestamp
    second_pivot_time: pd.Timestamp
    first_price_value: float
    second_price_value: float
    first_indicator_value: float
    second_indicator_value: float
    price_delta_pct: float
    indicator_delta_pct: float
    pivot_distance_bars: int
    score: float
    status: str = "candidate"
    warnings: list[str] = []

    class Config:
        arbitrary_types_allowed = True


def match_price_indicator_pivots(
    price_pivots: list[PivotPoint], indicator_pivots: list[PivotPoint], max_distance_bars: int
) -> list[tuple[PivotPoint, PivotPoint]]:
    """Match price and indicator pivots that occur near each other."""
    matches = []

    # Simple matching: indicator pivot must be within distance of price pivot
    # Usually they occur on the exact same bar, or very close

    ind_idx_map = {p.index: p for p in indicator_pivots}

    for p_pivot in price_pivots:
        # Search window
        start_idx = p_pivot.index - max_distance_bars
        end_idx = p_pivot.index + max_distance_bars

        best_match = None
        min_dist = float("inf")

        for idx in range(start_idx, end_idx + 1):
            if idx in ind_idx_map:
                i_pivot = ind_idx_map[idx]
                if i_pivot.pivot_type == p_pivot.pivot_type:
                    dist = abs(idx - p_pivot.index)
                    if dist < min_dist:
                        min_dist = dist
                        best_match = i_pivot

        if best_match:
            matches.append((p_pivot, best_match))

    return matches


def detect_divergences_for_indicator(
    df: pd.DataFrame, price_source: str, indicator_source: str, config: AppConfig
) -> list[DivergenceSignalCandidate]:
    cfg = config.indicator_v2.divergence
    if not cfg.enabled:
        return []

    if price_source not in df.columns or indicator_source not in df.columns:
        raise DivergenceDetectionError(
            f"Missing source columns: {price_source} or {indicator_source}"
        )

    price_pivots = detect_price_pivots(df, price_source, config)
    indicator_pivots = detect_indicator_pivots(df, indicator_source, config)

    # We only care about matching pivots
    matched_pivots = match_price_indicator_pivots(
        price_pivots,
        indicator_pivots,
        max_distance_bars=2,  # Allow small misalignment between price and indicator
    )

    candidates = []
    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "unknown"
    interval = df["interval"].iloc[0] if "interval" in df.columns else "unknown"

    # We need pairs of matched pivots to form a divergence
    for i in range(1, len(matched_pivots)):
        curr_price_p, curr_ind_p = matched_pivots[i]

        # Look back for a previous matching pivot
        for j in range(i - 1, -1, -1):
            prev_price_p, prev_ind_p = matched_pivots[j]

            # Must be same pivot type
            if curr_price_p.pivot_type != prev_price_p.pivot_type:
                continue

            dist_bars = curr_price_p.index - prev_price_p.index

            if dist_bars < cfg.min_pivot_distance:
                continue

            if dist_bars > cfg.max_pivot_pair_distance:
                break  # sorted by index, so older ones are even further

            p_curr = curr_price_p.value
            p_prev = prev_price_p.value
            i_curr = curr_ind_p.value
            i_prev = prev_ind_p.value

            p_delta_pct = (p_curr - p_prev) / abs(p_prev) if p_prev != 0 else 0
            i_delta_pct = (i_curr - i_prev) / abs(i_prev) if i_prev != 0 else 0

            div_type = None

            if curr_price_p.pivot_type == PivotType.low:
                if cfg.detect_regular and p_curr < p_prev and i_curr > i_prev:
                    div_type = DivergenceType.regular_bullish
                elif cfg.detect_hidden and p_curr > p_prev and i_curr < i_prev:
                    div_type = DivergenceType.hidden_bullish
            elif curr_price_p.pivot_type == PivotType.high:
                if cfg.detect_regular and p_curr > p_prev and i_curr < i_prev:
                    div_type = DivergenceType.regular_bearish
                elif cfg.detect_hidden and p_curr < p_prev and i_curr > i_prev:
                    div_type = DivergenceType.hidden_bearish

            if div_type and (
                abs(p_delta_pct) >= cfg.min_price_delta_pct
                and abs(i_delta_pct) >= cfg.min_indicator_delta_pct
            ):
                cand = DivergenceSignalCandidate(
                    candidate_id=uuid.uuid4().hex,
                    symbol=symbol,
                    interval=interval,
                    divergence_type=div_type,
                    price_source=price_source,
                    indicator_source=indicator_source,
                    first_pivot_time=prev_price_p.open_time,
                    second_pivot_time=curr_price_p.open_time,
                    first_price_value=p_prev,
                    second_price_value=p_curr,
                    first_indicator_value=i_prev,
                    second_indicator_value=i_curr,
                    price_delta_pct=p_delta_pct,
                    indicator_delta_pct=i_delta_pct,
                    pivot_distance_bars=dist_bars,
                    score=0.0,
                )
                if cfg.score_enabled:
                    cand.score = score_divergence(cand, config)
                candidates.append(cand)
                break  # Found the most recent divergence for this point

    return candidates


def score_divergence(candidate: DivergenceSignalCandidate, config: AppConfig) -> float:
    # A simple scoring based on delta magnitudes and distance. Max 100.
    p_mag = abs(candidate.price_delta_pct)
    i_mag = abs(candidate.indicator_delta_pct)

    # Normalize heavily to keep it 0-100
    score = (p_mag * 100) + (i_mag * 100)

    # Penalty for distance
    if candidate.pivot_distance_bars > 10:
        score = score * (10 / candidate.pivot_distance_bars)

    return min(100.0, score)


def detect_all_divergences(df: pd.DataFrame, config: AppConfig) -> list[DivergenceSignalCandidate]:
    cfg = config.indicator_v2.divergence
    if not cfg.enabled:
        return []

    all_cands = []

    for ind_source in cfg.indicator_sources:
        if ind_source in df.columns:
            all_cands.extend(
                detect_divergences_for_indicator(df, cfg.price_source, ind_source, config)
            )

    return all_cands


def divergences_to_dataframe(candidates: list[DivergenceSignalCandidate]) -> pd.DataFrame:
    if not candidates:
        return pd.DataFrame()

    return pd.DataFrame([c.model_dump() for c in candidates])


def add_divergence_features(
    df: pd.DataFrame, candidates: list[DivergenceSignalCandidate], config: AppConfig
) -> pd.DataFrame:
    df = df.copy()
    cfg = config.indicator_v2.divergence

    if not candidates:
        return df

    # div_regular_bullish_rsi_14_flag

    for cand in candidates:
        base_name = f"div_{cand.divergence_type.value}_{cand.indicator_source}"
        flag_col = f"{base_name}_flag"
        score_col = f"{base_name}_score"

        if flag_col not in df.columns:
            df[flag_col] = False
        if cfg.output_scores and score_col not in df.columns:
            df[score_col] = 0.0

        # The divergence is detected at the second pivot
        idx = (
            df.index[df["open_time"] == cand.second_pivot_time]
            if "open_time" in df.columns
            else df.index[df.index == cand.second_pivot_time]
        )

        if len(idx) > 0:
            df.loc[idx, flag_col] = True
            if cfg.output_scores:
                df.loc[idx, score_col] = cand.score

    return df
