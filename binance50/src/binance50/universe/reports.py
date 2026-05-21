from collections import Counter
from typing import Any

from binance50.config.models import UniverseConfig
from binance50.universe.models import UniverseSelectionResult


def build_universe_summary(result: UniverseSelectionResult) -> dict[str, Any]:
    return {
        "selected_count": len(result.selected_symbols),
        "rejected_count": len(result.rejected_symbols),
        "total_candidates": len(result.candidates),
        "top_selected": result.selected_symbols[:10] if result.selected_symbols else [],
        "generated_at_utc": result.generated_at_utc.isoformat(),
        "source_snapshot": result.source_snapshot_id,
    }


def build_rejection_reason_report(result: UniverseSelectionResult) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for _, candidate in result.candidates.items():
        for reason in candidate.rejection_reasons:
            counter[reason.value] += 1
    return dict(counter)


def build_symbol_explanation(symbol: str, result: UniverseSelectionResult) -> dict[str, Any]:
    if symbol not in result.candidates:
        return {"symbol": symbol, "found": False}

    candidate = result.candidates[symbol]
    return {
        "symbol": symbol,
        "found": True,
        "decision_status": candidate.decision_status.value,
        "score": candidate.score,
        "rejection_reasons": [r.value for r in candidate.rejection_reasons],
        "warnings": candidate.warnings,
        "market_scope": candidate.market_scope.value,
        "liquidity_quote_vol": (
            float(candidate.liquidity.quote_volume_24h) if candidate.liquidity else None
        ),
        "spread_bps": float(candidate.spread.spread_bps) if candidate.spread else None,
    }


def format_universe_table(result: UniverseSelectionResult) -> list[dict[str, Any]]:
    rows = []
    for symbol in result.selected_symbols:
        c = result.candidates[symbol]
        rows.append(
            {
                "symbol": symbol,
                "score": f"{c.score:.1f}",
                "quote_vol": f"{float(c.liquidity.quote_volume_24h):.0f}" if c.liquidity else "N/A",
                "spread_bps": f"{float(c.spread.spread_bps):.1f}" if c.spread else "N/A",
                "warnings": len(c.warnings),
            }
        )
    return rows


def build_universe_health_report(
    result: UniverseSelectionResult, config: UniverseConfig
) -> dict[str, Any]:
    summary = build_universe_summary(result)
    rejections = build_rejection_reason_report(result)

    avg_spread = 0.0
    avg_score = 0.0
    if result.selected_symbols:
        spreads = [
            float(result.candidates[s].spread.spread_bps)
            for s in result.selected_symbols
            if result.candidates[s].spread
        ]
        if spreads:
            avg_spread = sum(spreads) / len(spreads)

        scores = [result.candidates[s].score for s in result.selected_symbols]
        if scores:
            avg_score = sum(scores) / len(scores)

    return {
        "summary": summary,
        "rejection_reasons": rejections,
        "metrics": {
            "avg_spread_bps": avg_spread,
            "avg_score": avg_score,
            "min_symbols_met": len(result.selected_symbols) >= config.min_symbols_required,
        },
        "config_snapshot": {
            "max_initial": config.max_symbols_initial,
            "min_required": config.min_symbols_required,
            "min_quote_vol": float(config.min_quote_volume_24h_usdt),
            "max_spread_bps": float(config.max_spread_bps),
        },
    }
