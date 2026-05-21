from pathlib import Path

from binance50.config.loader import load_config
from binance50.core.enums import MarketScope
from binance50.universe.blacklist import load_blacklist
from binance50.universe.selector import UniverseSelector
from binance50.universe.snapshots import load_snapshot_from_files
from binance50.universe.whitelist import load_whitelist


def test_selector_spot_fixture():
    config = load_config()
    repo_root = Path(__file__).resolve().parent.parent

    fixture_dir = repo_root / "src" / "binance50" / "data" / "fixtures"
    info_file = fixture_dir / "spot_exchange_info_sample.json"
    ticker_file = fixture_dir / "spot_ticker_24hr_sample.json"
    book_file = fixture_dir / "spot_book_ticker_sample.json"

    snapshot = load_snapshot_from_files(info_file, ticker_file, book_file, MarketScope.SPOT)
    blacklist = load_blacklist(repo_root / config.universe.blacklist_file)
    whitelist = load_whitelist(repo_root / config.universe.whitelist_file)

    selector = UniverseSelector(config, blacklist, whitelist)
    result = selector.select_from_snapshot(snapshot)

    assert len(result.selected_symbols) >= config.universe.min_symbols_required
    assert len(result.selected_symbols) <= config.universe.max_symbols_initial
    assert "BTCUSDT" in result.selected_symbols
    assert "ETHUSDT" in result.selected_symbols

    assert "HALTUSDT" not in result.selected_symbols
    assert "USDCUSDT" not in result.selected_symbols
    assert "TOKENUPUSDT" not in result.selected_symbols


def test_explain_symbol():
    config = load_config()
    repo_root = Path(__file__).resolve().parent.parent

    fixture_dir = repo_root / "src" / "binance50" / "data" / "fixtures"
    info_file = fixture_dir / "spot_exchange_info_sample.json"
    ticker_file = fixture_dir / "spot_ticker_24hr_sample.json"
    book_file = fixture_dir / "spot_book_ticker_sample.json"

    snapshot = load_snapshot_from_files(info_file, ticker_file, book_file, MarketScope.SPOT)
    blacklist = load_blacklist(repo_root / config.universe.blacklist_file)
    whitelist = load_whitelist(repo_root / config.universe.whitelist_file)

    selector = UniverseSelector(config, blacklist, whitelist)
    result = selector.select_from_snapshot(snapshot)

    exp = selector.explain_symbol("HALTUSDT", result)
    assert exp["found"] is True
    assert exp["decision_status"] == "rejected"
    assert "not_trading" in exp["rejection_reasons"]

    exp = selector.explain_symbol("BTCUSDT", result)
    assert exp["found"] is True
    assert exp["decision_status"] == "accepted"
