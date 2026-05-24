import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import RegimeValidationError
from binance50.safety.regime_guard import assert_regime_config_safe


def test_regime_execution_forbidden():
    config = AppConfig()
    config.regimes.execution_forbidden = False
    with pytest.raises(RegimeValidationError):
        assert_regime_config_safe(config)
