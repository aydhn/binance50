import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import StoragePathError
from binance50.storage.paths import (
    assert_path_inside_storage,
    build_dataset_partition_path,
    get_storage_root,
    sanitize_path_component,
)


def test_sanitize_path_component():
    assert sanitize_path_component("test") == "test"
    assert sanitize_path_component("test-123_abc") == "test-123_abc"
    with pytest.raises(StoragePathError):
        sanitize_path_component("")
    with pytest.raises(StoragePathError):
        sanitize_path_component(".hidden")
    with pytest.raises(StoragePathError):
        sanitize_path_component("my_api_key_123")


def test_assert_path_inside_storage():
    config = AppConfig()
    root = get_storage_root(config)
    safe_path = root / "safe"
    unsafe_path = root.parent / "unsafe"

    assert_path_inside_storage(safe_path, config)

    with pytest.raises(StoragePathError):
        assert_path_inside_storage(unsafe_path, config)


def test_build_dataset_partition_path():
    config = AppConfig()
    path = build_dataset_partition_path(config, "ohlcv", "spot", "BTCUSDT", "1m", 2024, 5, 22)
    assert "dataset=ohlcv" in str(path)
    assert "market_scope=spot" in str(path)
    assert "symbol=BTCUSDT" in str(path)
    assert "interval=1m" in str(path)
    assert "year=2024" in str(path)
    assert "month=05" in str(path)
