from typing import Any

from binance50.config.models import AppConfig
from binance50.strategies.base import StrategyPluginProtocol


class StrategyRegistry:
    def __init__(self, config: AppConfig):
        self.config = config
        self._plugins: dict[str, StrategyPluginProtocol] = {}

    def register(self, plugin: StrategyPluginProtocol) -> None:
        if plugin.name in self._plugins:
            from binance50.core.exceptions import StrategyRegistryError

            raise StrategyRegistryError(f"Plugin {plugin.name} already registered")

        try:
            plugin.validate_config(self.config)
        except Exception as e:
            from binance50.core.exceptions import StrategyConfigError

            raise StrategyConfigError(f"Plugin {plugin.name} failed config validation: {e}")

        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> StrategyPluginProtocol:
        if name not in self._plugins:
            from binance50.core.exceptions import StrategyRegistryError

            raise StrategyRegistryError(f"Plugin {name} not found")
        return self._plugins[name]

    def list_plugins(
        self, enabled_only: bool = False, config: AppConfig | None = None
    ) -> list[StrategyPluginProtocol]:
        cfg = config or self.config
        if not enabled_only:
            return list(self._plugins.values())
        return [p for p in self._plugins.values() if p.is_enabled(cfg)]

    def validate_plugins(self, config: AppConfig) -> None:
        for _name, plugin in self._plugins.items():
            if plugin.is_enabled(config):
                plugin.validate_config(config)

    def health_report(self, config: AppConfig) -> dict[str, Any]:
        report = {
            "total_registered": len(self._plugins),
            "enabled": 0,
            "disabled": 0,
            "plugins": {},
        }
        for name, plugin in self._plugins.items():
            enabled = plugin.is_enabled(config)
            if enabled:
                report["enabled"] += 1
            else:
                report["disabled"] += 1

            try:
                health = plugin.health_check(config)
            except Exception as e:
                health = {"status": "fail", "error": str(e)}

            report["plugins"][name] = {
                "type": plugin.plugin_type.value,
                "version": plugin.version,
                "enabled": enabled,
                "health": health,
            }
        return report


def build_default_registry(config: AppConfig) -> StrategyRegistry:
    from binance50.strategies.plugin_loader import load_builtin_plugins

    registry = StrategyRegistry(config)
    plugins = load_builtin_plugins(config)
    for p in plugins:
        registry.register(p)
    return registry
