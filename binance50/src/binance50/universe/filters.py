from decimal import Decimal

from binance50.config.models import UniverseConfig
from binance50.universe.blacklist import SymbolListPolicy, is_asset_excluded, is_symbol_blacklisted
from binance50.universe.liquidity import is_liquidity_acceptable
from binance50.universe.models import (
    BookTicker,
    SymbolDecisionStatus,
    SymbolMetadata,
    SymbolRejectionReason,
    SymbolStatus,
    Ticker24h,
    UniverseCandidate,
)
from binance50.universe.spread import is_spread_acceptable
from binance50.universe.symbol_rules import validate_symbol_order_filters


def is_stablecoin_pair(base_asset: str, quote_asset: str) -> bool:
    stablecoins = {"USDT", "USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "EUR", "TRY"}
    return base_asset in stablecoins and quote_asset in stablecoins


def is_leveraged_token_symbol(symbol: str, base_asset: str | None = None) -> bool:
    # simple pattern matching to avoid leveraged tokens like BTCUP, BTCDOWN
    leveraged_suffixes = ["UP", "DOWN", "BULL", "BEAR"]
    if base_asset:
        for suf in leveraged_suffixes:
            if base_asset.endswith(suf):
                return True
    else:
        for suf in leveraged_suffixes:
            if suf in symbol:
                return True
    return False


def is_fan_token_candidate(symbol: str, base_asset: str | None = None) -> bool:
    # We can rely on external configuration to ban specific fan tokens, or blacklist.
    # Currently just returning False unless configured otherwise.
    return False


def evaluate_symbol_metadata(
    metadata: SymbolMetadata,
    config: UniverseConfig,
    blacklist_policy: SymbolListPolicy,
    whitelist_policy: SymbolListPolicy,
) -> tuple[list[SymbolRejectionReason], list[str]]:
    reasons = []
    warnings: list[str] = []

    if config.require_trading_status and metadata.status != SymbolStatus.TRADING:
        reasons.append(SymbolRejectionReason.NOT_TRADING)

    if metadata.quote_asset not in config.quote_assets:
        reasons.append(SymbolRejectionReason.QUOTE_ASSET_NOT_ALLOWED)

    if metadata.market_scope not in config.market_scopes:
        reasons.append(SymbolRejectionReason.UNSUPPORTED_MARKET_SCOPE)

    if is_symbol_blacklisted(metadata.symbol, blacklist_policy, config) or is_asset_excluded(
        metadata.base_asset, metadata.quote_asset, config
    ):
        reasons.append(SymbolRejectionReason.BLACKLISTED)

    if not config.allow_stablecoin_pairs and is_stablecoin_pair(
        metadata.base_asset, metadata.quote_asset
    ):
        reasons.append(SymbolRejectionReason.STABLECOIN_PAIR)

    if not config.allow_leveraged_tokens and is_leveraged_token_symbol(
        metadata.symbol, metadata.base_asset
    ):
        reasons.append(SymbolRejectionReason.LEVERAGED_TOKEN)

    if not config.allow_fan_tokens and is_fan_token_candidate(metadata.symbol, metadata.base_asset):
        reasons.append(SymbolRejectionReason.FAN_TOKEN)

    filter_reasons = validate_symbol_order_filters(metadata, config)
    reasons.extend(filter_reasons)

    return reasons, warnings


def evaluate_market_data(
    ticker: Ticker24h | None, book: BookTicker | None, config: UniverseConfig
) -> tuple[list[SymbolRejectionReason], list[str]]:
    reasons = []
    warnings: list[str] = []

    if config.require_quote_volume and not ticker:
        reasons.append(SymbolRejectionReason.MISSING_24H_TICKER)

    if config.require_book_ticker and not book:
        reasons.append(SymbolRejectionReason.MISSING_BOOK_TICKER)

    return reasons, warnings


def evaluate_candidate(candidate: UniverseCandidate, config: UniverseConfig) -> UniverseCandidate:
    # If it's already rejected from metadata, stop early
    if SymbolDecisionStatus.REJECTED in [candidate.decision_status] and candidate.rejection_reasons:
        return candidate

    reasons = list(candidate.rejection_reasons)

    if candidate.ticker_24h is None and config.require_quote_volume:
        reasons.append(SymbolRejectionReason.MISSING_24H_TICKER)

    if candidate.book_ticker is None and config.require_book_ticker:
        reasons.append(SymbolRejectionReason.MISSING_BOOK_TICKER)

    if candidate.liquidity and not is_liquidity_acceptable(candidate.liquidity, config):
        if candidate.liquidity.quote_volume_24h < Decimal(str(config.min_quote_volume_24h_usdt)):
            reasons.append(SymbolRejectionReason.LOW_QUOTE_VOLUME)
        if candidate.liquidity.trade_count_24h < config.min_trade_count_24h:
            reasons.append(SymbolRejectionReason.LOW_TRADE_COUNT)

    if candidate.spread and not is_spread_acceptable(candidate.spread, config.max_spread_bps):
        reasons.append(SymbolRejectionReason.HIGH_SPREAD)

    candidate.rejection_reasons = list(set(reasons))

    if reasons:
        candidate.decision_status = SymbolDecisionStatus.REJECTED
    elif candidate.score > 0 and candidate.score < config.scoring.min_score:
        # Only reject for low score if it's actually been scored (score > 0)
        candidate.rejection_reasons.append(SymbolRejectionReason.SCORE_BELOW_THRESHOLD)
        candidate.decision_status = SymbolDecisionStatus.REJECTED
    else:
        candidate.decision_status = SymbolDecisionStatus.ACCEPTED

    return candidate
