import pytest
from binance50.config.models import AppConfig
from binance50.ml.blending.integration_contract import build_ml_blending_integration_contract, validate_ml_blending_integration_contract

def test_contract_build():
    config = AppConfig()
    contract = build_ml_blending_integration_contract(config)
    assert contract.sandbox_only is True
    assert contract.production_write_forbidden is True
    assert "order_id" in contract.forbidden_outputs

def test_validate_contract():
    config = AppConfig()
    contract = build_ml_blending_integration_contract(config)
    validate_ml_blending_integration_contract(contract, config)
    contract.sandbox_only = False
    with pytest.raises(ValueError):
        validate_ml_blending_integration_contract(contract, config)
