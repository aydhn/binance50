import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorRegistryError
from binance50.indicators.models import IndicatorBackend, IndicatorGroup, IndicatorSpec
from binance50.indicators.registry import IndicatorRegistry


def test_registry_default_build():
    config = AppConfig()
    registry = IndicatorRegistry(config)

    specs = registry.list_specs()
    assert len(specs) > 0

    # Check some defaults exist
    assert registry.get("sma_20").name == "sma_20"
    assert registry.get("macd_12_26_9").name == "macd_12_26_9"
    assert registry.get("rsi_14").name == "rsi_14"

def test_registry_duplicate_register():
    config = AppConfig()
    registry = IndicatorRegistry(config)

    spec = IndicatorSpec("test_ind", IndicatorGroup.TREND, IndicatorBackend.NATIVE, {}, [], [], 10)
    registry.register(spec)

    with pytest.raises(IndicatorRegistryError):
        registry.register(spec)

def test_registry_get_not_found():
    config = AppConfig()
    registry = IndicatorRegistry(config)

    with pytest.raises(IndicatorRegistryError):
        registry.get("nonexistent")

def test_registry_filters():
    config = AppConfig()
    registry = IndicatorRegistry(config)

    trend_specs = registry.list_specs(group=IndicatorGroup.TREND)
    assert all(s.group == IndicatorGroup.TREND for s in trend_specs)

    native_specs = registry.list_specs(backend=IndicatorBackend.NATIVE)
    assert len(native_specs) > 0

def test_registry_max_specs():
    config = AppConfig()
    config.indicators.max_indicator_specs_per_run = 0
    with pytest.raises(IndicatorRegistryError):
        IndicatorRegistry(config) # Fails during default build

def test_registry_validate_specs():
    config = AppConfig()
    registry = IndicatorRegistry(config)

    specs = registry.list_specs()

    # Should pass
    registry.validate_specs(specs, config)

    # Exceed columns
    config.indicators.max_columns_allowed = 1
    with pytest.raises(IndicatorRegistryError):
        registry.validate_specs(specs, config)
