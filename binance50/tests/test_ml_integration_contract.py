import pytest
from pathlib import Path
from binance50.config.models import AppConfig
from binance50.ml.inference.integration_contract import (
    build_ml_signal_integration_contract,
    validate_integration_contract,
    export_integration_contract
)
from binance50.core.exceptions import MLSandboxIntegrationError

def test_build_ml_signal_integration_contract():
    config = AppConfig()
    contract = build_ml_signal_integration_contract(config)
    assert contract.sandbox_only is True
    assert contract.production_write_forbidden is True
    assert "order_id" in contract.forbidden_output_fields
    assert "assert_signal_auto_write_forbidden" in contract.required_guards

def test_validate_integration_contract():
    config = AppConfig()
    contract = build_ml_signal_integration_contract(config)

    # Should pass
    validate_integration_contract(contract, config)

    contract.production_write_forbidden = False
    with pytest.raises(MLSandboxIntegrationError, match="production write is forbidden"):
        validate_integration_contract(contract, config)

    contract.production_write_forbidden = True
    contract.forbidden_output_fields = []
    with pytest.raises(MLSandboxIntegrationError, match="missing required forbidden"):
        validate_integration_contract(contract, config)

def test_export_integration_contract(tmp_path):
    config = AppConfig()
    contract = build_ml_signal_integration_contract(config)

    p = tmp_path / "contract.json"
    exported_path = export_integration_contract(contract, p)

    assert exported_path.exists()
    import json
    data = json.loads(exported_path.read_text())
    assert data["contract_id"] == "ml_signal_contract_v1"
