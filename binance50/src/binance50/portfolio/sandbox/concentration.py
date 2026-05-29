from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioConcentrationReport(BaseModel):
    run_id: str
    symbol_concentration: dict[str, float] = Field(default_factory=dict)
    top_3_symbol_weight_pct: float
    same_regime_ratio: float
    same_direction_ratio: float
    same_strategy_plugin_ratio: float
    concentration_score: float
    concentration_warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def analyze_symbol_concentration(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> tuple[dict, float]:
    if not candidates:
        return {}, 0.0

    counts = {}
    for c in candidates:
        counts[c.symbol] = counts.get(c.symbol, 0) + 1

    ratios = {s: c / len(candidates) for s, c in counts.items()}
    sorted_vals = sorted(ratios.values(), reverse=True)
    top_3 = sum(sorted_vals[:3]) * 100.0

    return ratios, top_3


def analyze_regime_concentration(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> float:
    if not candidates:
        return 0.0

    counts = {}
    for c in candidates:
        r = c.regime or "unknown"
        counts[r] = counts.get(r, 0) + 1

    if counts:
        return max(counts.values()) / len(candidates)
    return 0.0


def analyze_direction_concentration(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> float:
    if not candidates:
        return 0.0

    counts = {}
    for c in candidates:
        counts[c.direction] = counts.get(c.direction, 0) + 1

    if counts:
        return max(counts.values()) / len(candidates)
    return 0.0


def analyze_strategy_plugin_concentration(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> float:
    # In a full implementation, you would extract plugin ids from source_trace
    return 0.0


def compute_concentration_penalty(
    candidate: PortfolioCandidateInput, context: dict, config: AppConfig
) -> float:
    c_config = config.portfolio_sandbox.concentration
    if not c_config.enabled:
        return 0.0

    penalty = 0.0

    # If this candidate's symbol is heavily concentrated in context
    symbol_ratio = context.get("symbol_concentration", {}).get(candidate.symbol, 0.0)
    if symbol_ratio > (c_config.max_single_symbol_weight_pct / 100.0):
        penalty += c_config.concentration_penalty

    return penalty


def build_concentration_report(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioConcentrationReport:
    c_config = config.portfolio_sandbox.concentration

    report = PortfolioConcentrationReport(
        run_id="unknown",
        top_3_symbol_weight_pct=0.0,
        same_regime_ratio=0.0,
        same_direction_ratio=0.0,
        same_strategy_plugin_ratio=0.0,
        concentration_score=0.0,
    )

    if not c_config.enabled or not candidates:
        return report

    sym_ratios, top_3 = analyze_symbol_concentration(candidates, config)
    regime_ratio = analyze_regime_concentration(candidates, config)
    dir_ratio = analyze_direction_concentration(candidates, config)
    strat_ratio = analyze_strategy_plugin_concentration(candidates, config)

    report.symbol_concentration = sym_ratios
    report.top_3_symbol_weight_pct = top_3
    report.same_regime_ratio = regime_ratio
    report.same_direction_ratio = dir_ratio
    report.same_strategy_plugin_ratio = strat_ratio

    # Check warnings
    if top_3 > c_config.max_top_3_symbol_weight_pct:
        report.concentration_warnings.append(
            f"Top 3 symbols weight ({top_3:.1f}%) exceeds limit ({c_config.max_top_3_symbol_weight_pct}%)"
        )

    if regime_ratio > c_config.max_same_regime_ratio:
        report.concentration_warnings.append(
            f"Regime concentration ({regime_ratio * 100:.1f}%) exceeds limit ({c_config.max_same_regime_ratio * 100}%)"
        )

    if dir_ratio > c_config.max_same_direction_ratio:
        report.concentration_warnings.append(
            f"Direction concentration ({dir_ratio * 100:.1f}%) exceeds limit ({c_config.max_same_direction_ratio * 100}%)"
        )

    # Rough score: lower is better
    report.concentration_score = top_3 + (regime_ratio + dir_ratio + strat_ratio) * 100.0

    return report
