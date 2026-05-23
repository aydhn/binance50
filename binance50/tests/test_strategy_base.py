from binance50.strategies.base import StrategyPluginProtocol


class DummyPlugin(StrategyPluginProtocol):
    name = "dummy"
    plugin_type = "trend_following"
    version = "1.0"
    required_features = []
    required_prefixes = []
    description = ""

    def is_enabled(self, config):
        return True

    def validate_config(self, config):
        pass

    def validate_input(self, df, config):
        pass

    def evaluate_row(self, row, context):
        return None

    def evaluate(self, df, context):
        return []

    def explain(self, candidate):
        return None

    def health_check(self, config):
        return {}


def test_strategy_plugin_protocol():
    plugin = DummyPlugin()
    assert plugin.name == "dummy"
    assert hasattr(plugin, "evaluate")
