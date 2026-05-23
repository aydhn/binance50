import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import StrategyRegistryError
from binance50.strategies.registry import StrategyRegistry


class Dummy1:
    name = "d1"
    plugin_type = "type"
    version = "1.0"

    def validate_config(self, c):
        pass

    def is_enabled(self, c):
        return True


class Dummy2:
    name = "d1"
    plugin_type = "type"
    version = "1.0"

    def validate_config(self, c):
        pass


def test_registry_uniqueness():
    config = AppConfig()
    reg = StrategyRegistry(config)
    reg.register(Dummy1())

    with pytest.raises(StrategyRegistryError):
        reg.register(Dummy2())
