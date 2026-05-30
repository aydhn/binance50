from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import CredentialDetectedError, SignedPayloadDetectedError

from binance50.execution.payloads import detect_api_credentials, detect_signed_payload


def assert_no_api_credentials_in_config(config: AppConfig) -> None:
    if config.execution.global_.allow_api_credentials:
        raise CredentialDetectedError("allow_api_credentials must be False in Phase 28 configuration.")


def assert_no_api_credentials_in_payload(payload: dict[str, Any]) -> None:
    creds = detect_api_credentials(payload)
    if creds:
        raise CredentialDetectedError(f"API credentials detected in payload: {creds}")


def assert_no_signed_request_payload(payload: dict[str, Any]) -> None:
    signed = detect_signed_payload(payload)
    if signed:
        raise SignedPayloadDetectedError(f"Signed request detected in payload: {signed}")


def assert_no_secret_like_values(payload: dict[str, Any]) -> None:
    # Basic check, similar to detect_api_credentials
    assert_no_api_credentials_in_payload(payload)


def build_credential_safety_report(config: AppConfig) -> dict[str, Any]:
    return {
        "allow_api_credentials": config.execution.global_.allow_api_credentials,
        "reject_api_key_payload": config.execution.payload_safety.reject_api_key,
        "reject_secret_payload": config.execution.payload_safety.reject_secret,
        "reject_signature_payload": config.execution.payload_safety.reject_signature
    }
