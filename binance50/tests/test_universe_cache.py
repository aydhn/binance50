import tempfile
from datetime import UTC, datetime

from binance50.config.models import UniverseConfig
from binance50.universe.cache import UniverseCache
from binance50.universe.models import UniverseSelectionResult


def test_universe_cache():
    with tempfile.TemporaryDirectory() as d:
        c = UniverseConfig()
        c.cache_dir = d
        cache = UniverseCache(c)

        result = UniverseSelectionResult(
            selected_symbols=["BTCUSDT"], generated_at_utc=datetime.now(UTC)
        )

        # Test save
        path = cache.save_selection(result, "spot")
        assert path.exists()

        # Test load
        loaded = cache.load_latest_selection("spot")
        assert loaded is not None
        assert loaded.selected_symbols == ["BTCUSDT"]

        # Test list
        files = cache.list_cached_selections()
        assert len(files) == 1

        # Test clear
        cache.clear_cache()
        files = cache.list_cached_selections()
        assert len(files) == 0
