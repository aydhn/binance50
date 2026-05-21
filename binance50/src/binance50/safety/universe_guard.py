from typing import Any

from binance50.config.models import AppConfig
from binance50.universe.filters import is_stablecoin_pair
from binance50.universe.models import SymbolRejectionReason, UniverseSelectionResult


class UniverseSafetyError(Exception):
    pass


def assert_universe_config_safe(config: AppConfig) -> None:
    u_config = config.universe
    if not u_config.enabled:
        return

    if u_config.max_symbols_initial > 50:
        raise UniverseSafetyError(
            f"max_symbols_initial ({u_config.max_symbols_initial}) is unsafely high (> 50)"
        )

    if u_config.max_symbols_allowed > 50:
        raise UniverseSafetyError(
            f"max_symbols_allowed ({u_config.max_symbols_allowed}) is unsafely high (> 50)"
        )

    if float(u_config.min_quote_volume_24h_usdt) < 1000000.0:
        raise UniverseSafetyError(
            f"min_quote_volume_24h_usdt ({u_config.min_quote_volume_24h_usdt}) is unsafely low (< 1,000,000)"
        )

    if float(u_config.max_spread_bps) > 20.0:
        raise UniverseSafetyError(
            f"max_spread_bps ({u_config.max_spread_bps}) is unsafely high (> 20.0 bps)"
        )

    if u_config.allow_stablecoin_pairs:
        raise UniverseSafetyError("allow_stablecoin_pairs is unsafely set to True")


def assert_universe_result_safe(result: UniverseSelectionResult, config: AppConfig) -> None:
    if not config.universe.enabled:
        return

    if not result.selected_symbols:
        raise UniverseSafetyError("No symbols selected in universe result")

    for symbol in result.selected_symbols:
        candidate = result.candidates.get(symbol)
        if not candidate:
            raise UniverseSafetyError(f"Selected symbol {symbol} missing candidate details")

        if is_stablecoin_pair(candidate.metadata.base_asset, candidate.metadata.quote_asset):
            raise UniverseSafetyError(f"Stablecoin pair selected: {symbol}")

        if SymbolRejectionReason.BLACKLISTED in candidate.rejection_reasons:
            raise UniverseSafetyError(f"Blacklisted symbol selected: {symbol}")

        if SymbolRejectionReason.MISSING_FILTERS in candidate.rejection_reasons:
            raise UniverseSafetyError(f"Symbol with missing filters selected: {symbol}")


def build_universe_safety_report(
    config: AppConfig, result: UniverseSelectionResult | None = None
) -> dict[str, Any]:
    report = {
        "config_status": "safe",
        "result_status": "safe" if result else "not_evaluated",
        "errors": [],
    }

    try:
        assert_universe_config_safe(config)
    except UniverseSafetyError as e:
        report["config_status"] = "unsafe"
        report["errors"].append(str(e))

    if result:
        try:
            assert_universe_result_safe(result, config)
        except UniverseSafetyError as e:
            report["result_status"] = "unsafe"
            report["errors"].append(str(e))

    report["overall_status"] = "safe" if not report["errors"] else "unsafe"
    return report
