from collections.abc import Callable

from binance50.config.models import AppConfig
from binance50.connectors.base import ExchangeAdapterProtocol
from binance50.core.enums import MarketScope
from binance50.core.exceptions import UnsupportedFeatureError

_REGISTRY: dict[str, Callable[[AppConfig], ExchangeAdapterProtocol]] = {}


def get_supported_adapters() -> list[str]:
    return list(_REGISTRY.keys())


def resolve_adapter_key(config: AppConfig) -> str:
    profile = config.selected_environment_profile
    return f"{profile.exchange.value}:{profile.market_scope.value}"


def assert_adapter_supported(config: AppConfig) -> None:
    key = resolve_adapter_key(config)
    if key not in _REGISTRY:
        raise UnsupportedFeatureError(f"Adapter not supported: {key}")
    if config.selected_environment_profile.market_scope == MarketScope.COINM_FUTURES:
        raise UnsupportedFeatureError("COIN-M futures are not implemented")


def register_adapter(key: str, factory: Callable[[AppConfig], ExchangeAdapterProtocol]) -> None:
    _REGISTRY[key] = factory


def get_adapter_factory(key: str) -> Callable[[AppConfig], ExchangeAdapterProtocol]:
    if key not in _REGISTRY:
        raise UnsupportedFeatureError(f"Adapter not found: {key}")
    return _REGISTRY[key]


# Import to register them if needed, we'll do this carefully to avoid circular imports.
# In a real app we might register them in binance/__init__.py
