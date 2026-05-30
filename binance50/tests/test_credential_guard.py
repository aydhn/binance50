import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import CredentialDetectedError
from binance50.safety.credential_guard import assert_no_api_credentials_in_payload

def test_no_api_credentials_in_payload():
    with pytest.raises(CredentialDetectedError):
        assert_no_api_credentials_in_payload({"api_key": "123"})
