from binance50.config.models import UniverseConfig
from binance50.universe.blacklist import SymbolListPolicy, is_symbol_blacklisted
from binance50.universe.models import (
    SymbolDecisionStatus,
    UniverseCandidate,
    UniverseSelectionResult,
)


class UniverseValidationError(Exception):
    pass


def validate_symbol_format(symbol: str) -> None:
    if not symbol or not symbol.isupper() or not symbol.isalnum():
        raise UniverseValidationError(f"Invalid symbol format: {symbol}")


def validate_quote_asset(symbol: str, quote_asset: str) -> None:
    if not symbol.endswith(quote_asset):
        raise UniverseValidationError(
            f"Symbol {symbol} does not end with quote asset {quote_asset}"
        )


def validate_candidate_metadata(candidate: UniverseCandidate) -> None:
    if not candidate.metadata:
        raise UniverseValidationError(f"Candidate {candidate.symbol} missing metadata")
    validate_symbol_format(candidate.symbol)


def assert_selected_symbols_unique(result: UniverseSelectionResult) -> None:
    if len(result.selected_symbols) != len(set(result.selected_symbols)):
        raise UniverseValidationError("Selected symbols list contains duplicates")


def assert_no_blacklisted_symbols_selected(
    result: UniverseSelectionResult, blacklist_policy: SymbolListPolicy, config: UniverseConfig
) -> None:
    for symbol in result.selected_symbols:
        if is_symbol_blacklisted(symbol, blacklist_policy, config):
            raise UniverseValidationError(f"Blacklisted symbol selected: {symbol}")


def validate_universe_result(result: UniverseSelectionResult, config: UniverseConfig) -> None:
    assert_selected_symbols_unique(result)

    if len(result.selected_symbols) > config.max_symbols_allowed:
        raise UniverseValidationError(
            f"Selected symbols ({len(result.selected_symbols)}) exceed max allowed ({config.max_symbols_allowed})"
        )

    for symbol in result.selected_symbols:
        candidate = result.candidates.get(symbol)
        if not candidate:
            raise UniverseValidationError(
                f"Selected symbol {symbol} missing in candidates dictionary"
            )
        if candidate.decision_status != SymbolDecisionStatus.ACCEPTED:
            raise UniverseValidationError(f"Selected symbol {symbol} does not have ACCEPTED status")
