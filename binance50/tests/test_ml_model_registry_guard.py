import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_model_registry_guard import (
    assert_model_registry_config_safe, assert_no_serving_promotion_attempt,
    assert_untrusted_artifact_load_blocked
)

def test_ml_model_registry_guard():
    config = AppConfig()
    assert_model_registry_config_safe(config)

    config.ml_training.registry.auto_promote_forbidden = False
    with pytest.raises(ValueError, match="auto_promote_forbidden must be True"):
        assert_model_registry_config_safe(config)

    config = AppConfig()
    with pytest.raises(ValueError, match="Serving promotion attempt forbidden"):
        assert_no_serving_promotion_attempt("1", config)

    config.ml_training.registry.allow_loading_untrusted_artifacts = True
    with pytest.raises(ValueError, match="Loading untrusted artifacts must be blocked"):
        assert_untrusted_artifact_load_blocked(config)
