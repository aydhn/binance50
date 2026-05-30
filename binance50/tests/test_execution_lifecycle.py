import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionLifecycleError
from binance50.execution.lifecycle import validate_lifecycle_transition, reject_exchange_lifecycle_state

def test_validate_lifecycle_transition():
    config = get_config()
    validate_lifecycle_transition("draft_created", "safety_scanned", config)

    with pytest.raises(ExecutionLifecycleError, match="is forbidden"):
        validate_lifecycle_transition("draft_created", "submitted", config)

def test_reject_exchange_lifecycle_state():
    config = get_config()
    with pytest.raises(ExecutionLifecycleError, match="strictly forbidden"):
        reject_exchange_lifecycle_state("filled", config)
