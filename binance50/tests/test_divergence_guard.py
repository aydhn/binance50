import pytest

from binance50.config.models import AppConfig
from binance50.safety.divergence_guard import assert_divergence_config_safe


def test_divergence_guard_safe(config: AppConfig):
    # Default is safe
    assert_divergence_config_safe(config)


def test_divergence_guard_centered_pivot(config: AppConfig):
    with pytest.raises(ValueError):
        from binance50.config.models import PivotConfig

        PivotConfig(use_centered_window=True)


def test_divergence_guard_repainting(config: AppConfig):
    with pytest.raises(ValueError):
        from binance50.config.models import PivotConfig

        PivotConfig(allow_repainting=True)


def test_divergence_guard_confirm(config: AppConfig):
    with pytest.raises(ValueError):
        from binance50.config.models import PivotConfig

        PivotConfig(confirm_after_bars=5)
