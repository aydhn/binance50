from datetime import UTC, datetime
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.universe.blacklist import SymbolListPolicy
from binance50.universe.filters import (
    evaluate_candidate,
    evaluate_market_data,
    evaluate_symbol_metadata,
)
from binance50.universe.liquidity import compute_liquidity_metrics
from binance50.universe.models import (
    BookTicker,
    SymbolDecisionStatus,
    SymbolMetadata,
    Ticker24h,
    UniverseCandidate,
    UniverseSelectionResult,
)
from binance50.universe.reports import build_symbol_explanation, build_universe_health_report
from binance50.universe.scoring import compute_candidate_score, rank_candidates
from binance50.universe.snapshots import UniverseSnapshot, validate_snapshot
from binance50.universe.spread import compute_spread_metrics
from binance50.universe.symbol_rules import evaluate_symbol_rule_quality
from binance50.universe.whitelist import apply_whitelist_preference


class UniverseSelectorError(Exception):
    pass


class UniverseSelector:
    def __init__(
        self,
        config: AppConfig,
        blacklist_policy: SymbolListPolicy,
        whitelist_policy: SymbolListPolicy,
    ):
        self.app_config = config
        self.config = config.universe
        self.blacklist_policy = blacklist_policy
        self.whitelist_policy = whitelist_policy

    def build_candidates(
        self,
        metadata_list: list[SymbolMetadata],
        tickers: dict[str, Ticker24h],
        book_tickers: dict[str, BookTicker],
        market_scope: MarketScope,
    ) -> list[UniverseCandidate]:
        candidates = []
        for metadata in metadata_list:
            if metadata.market_scope != market_scope:
                continue

            symbol = metadata.symbol
            ticker = tickers.get(symbol)
            book = book_tickers.get(symbol)

            # Initial evaluation based on metadata
            meta_reasons, meta_warnings = evaluate_symbol_metadata(
                metadata, self.config, self.blacklist_policy, self.whitelist_policy
            )

            # Additional evaluations if ticker and book present
            market_reasons, market_warnings = evaluate_market_data(ticker, book, self.config)

            all_reasons = meta_reasons + market_reasons
            all_warnings = meta_warnings + market_warnings

            candidate = UniverseCandidate(
                symbol=symbol,
                market_scope=market_scope,
                metadata=metadata,
                ticker_24h=ticker,
                book_ticker=book,
                rejection_reasons=list(set(all_reasons)),
                warnings=all_warnings,
                decision_status=(
                    SymbolDecisionStatus.REJECTED if all_reasons else SymbolDecisionStatus.WARNING
                ),
            )

            # Proceed with metrics if data is available
            if ticker and book:
                candidate.spread = compute_spread_metrics(book)
                candidate.liquidity = compute_liquidity_metrics(ticker, book)
                candidate.rule_quality = evaluate_symbol_rule_quality(metadata, ticker, self.config)

            candidates.append(candidate)

        return candidates

    def select_universe(
        self,
        metadata_list: list[SymbolMetadata],
        tickers: dict[str, Ticker24h],
        book_tickers: dict[str, BookTicker],
        market_scope: MarketScope,
        source_snapshot_id: str | None = None,
    ) -> UniverseSelectionResult:
        if not self.config.enabled:
            return UniverseSelectionResult()

        candidates = self.build_candidates(metadata_list, tickers, book_tickers, market_scope)

        # Evaluate and score candidates
        for c in candidates:
            c = evaluate_candidate(c, self.config)
            if c.decision_status != SymbolDecisionStatus.REJECTED:
                c = apply_whitelist_preference(c, self.config)
                c.score = compute_candidate_score(c, self.config, self.whitelist_policy)
            # Re-evaluate based on score threshold
            c = evaluate_candidate(c, self.config)

        # Rank candidates
        ranked = rank_candidates(candidates, self.config)

        # Select top candidates up to max_symbols_initial
        selected: list[str] = []
        rejected = []
        candidate_dict = {}

        for c in ranked:
            candidate_dict[c.symbol] = c
            if (
                c.decision_status == SymbolDecisionStatus.ACCEPTED
                and len(selected) < self.config.max_symbols_initial
            ):
                selected.append(c.symbol)
            else:
                if c.decision_status == SymbolDecisionStatus.ACCEPTED:
                    # Ranked out
                    c.decision_status = SymbolDecisionStatus.REJECTED
                    c.rejection_reasons.append("ranked_out")  # type: ignore
                rejected.append(c.symbol)

        if len(selected) < self.config.min_symbols_required:
            raise UniverseSelectorError(
                f"Could not select minimum required symbols ({self.config.min_symbols_required}). "
                f"Selected only {len(selected)}."
            )

        result = UniverseSelectionResult(
            selected_symbols=selected,
            rejected_symbols=rejected,
            candidates=candidate_dict,
            generated_at_utc=datetime.now(UTC),
            config_summary={
                "max_initial": self.config.max_symbols_initial,
                "min_required": self.config.min_symbols_required,
                "quote_assets": self.config.quote_assets,
            },
            source_snapshot_id=source_snapshot_id,
        )

        result.report = build_universe_health_report(result, self.config)
        return result

    def select_from_snapshot(self, snapshot: UniverseSnapshot) -> UniverseSelectionResult:
        validate_snapshot(snapshot)
        from binance50.universe.parser import (
            parse_24h_tickers,
            parse_book_tickers,
            parse_spot_exchange_info,
            parse_usdm_exchange_info,
        )

        market_scope = snapshot.market_scope
        if market_scope == MarketScope.SPOT:
            metadata_list = parse_spot_exchange_info(snapshot.exchange_info_payload)
        else:
            metadata_list = parse_usdm_exchange_info(snapshot.exchange_info_payload)

        tickers = parse_24h_tickers(snapshot.ticker_24h_payload, market_scope)
        book_tickers = parse_book_tickers(snapshot.book_ticker_payload, market_scope)

        return self.select_universe(
            metadata_list, tickers, book_tickers, market_scope, snapshot.snapshot_id
        )

    def explain_symbol(self, symbol: str, result: UniverseSelectionResult) -> dict[str, Any]:
        return build_symbol_explanation(symbol, result)

    def to_report(self, result: UniverseSelectionResult) -> dict[str, Any]:
        return result.report
