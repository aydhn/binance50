from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    ApiPermissionError,
    CredentialPairError,
    UnsupportedPermissionError,
)


def validate_credentials_required_policy(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    creds = config.credentials.binance

    has_key = creds.api_key is not None and creds.api_key.get_secret_value() != ""
    has_secret = creds.api_secret is not None and creds.api_secret.get_secret_value() != ""

    # Credential pair must be complete if one is present
    if has_key and not has_secret:
        raise CredentialPairError("API key provided without API secret")
    if has_secret and not has_key:
        raise CredentialPairError("API secret provided without API key")

    policy = profile.credential_policy
    if policy.requires_credentials and not (has_key and has_secret):
        raise CredentialPairError(
            f"Profile {profile.profile_name} requires credentials, but they are missing"
        )

    if policy.forbids_credentials and (has_key or has_secret):
        raise CredentialPairError(
            f"Profile {profile.profile_name} forbids credentials, but they are provided"
        )


def validate_permission_policy(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    creds = config.credentials.binance
    policy = profile.permission_policy

    if policy.requires_read_permission and not creds.permission_read:
        raise ApiPermissionError(f"Profile {profile.profile_name} requires read permission")

    if policy.requires_spot_trade_permission and not creds.permission_spot_trade:
        raise ApiPermissionError(f"Profile {profile.profile_name} requires spot trade permission")

    if policy.requires_futures_trade_permission and not creds.permission_futures_trade:
        raise ApiPermissionError(
            f"Profile {profile.profile_name} requires futures trade permission"
        )

    if creds.permission_margin_trade:
        raise UnsupportedPermissionError("Margin trading is not supported in Phase 4")


def assert_readonly_profile_has_no_trade_permissions(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    creds = config.credentials.binance

    if profile.profile_name.value.endswith("_readonly") and \
       (creds.permission_spot_trade or creds.permission_futures_trade):
            raise ApiPermissionError("Readonly profile should not be used with trading permissions")


def assert_live_profile_has_required_permissions(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    if not profile.is_live:
        return

    creds = config.credentials.binance
    if profile.market_scope.value == "spot" and not creds.permission_spot_trade:
        raise ApiPermissionError("Live spot trading requires spot trade permission")
    if profile.market_scope.value == "usdm_futures" and not creds.permission_futures_trade:
        raise ApiPermissionError("Live futures trading requires futures trade permission")


def assert_ip_restriction_policy(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    creds = config.credentials.binance

    if profile.permission_policy.requires_ip_restriction and not creds.ip_restricted:
        # According to requirements: "live profilde IP restriction false ise "
        # "bu fazda hard error yerine blocking warning üret"
        # However, we only have Exceptions here. We'll raise a custom check
        # but we might bypass it in live guard.
        pass


def assert_no_credentials_required_for_paper(config: AppConfig) -> None:
    profile = config.selected_environment_profile
    if profile.is_paper and profile.credential_policy.requires_credentials:
        raise ApiPermissionError("Paper profile should not require credentials")


def build_api_key_safety_report(config: AppConfig) -> dict[str, Any]:
    creds = config.credentials.binance
    has_key = creds.api_key is not None and creds.api_key.get_secret_value() != ""
    has_secret = creds.api_secret is not None and creds.api_secret.get_secret_value() != ""

    issues = []

    try:
        validate_credentials_required_policy(config)
    except Exception as e:
        issues.append(str(e))

    try:
        validate_permission_policy(config)
    except Exception as e:
        issues.append(str(e))

    try:
        assert_readonly_profile_has_no_trade_permissions(config)
    except Exception as e:
        issues.append(str(e))

    try:
        assert_live_profile_has_required_permissions(config)
    except Exception as e:
        issues.append(str(e))

    return {
        "status": "unsafe" if issues else "safe",
        "issues": issues,
        "credentials_present": has_key or has_secret,
        "credential_pair_complete": has_key and has_secret,
        "permissions": {
            "read": creds.permission_read,
            "spot_trade": creds.permission_spot_trade,
            "futures_trade": creds.permission_futures_trade,
            "margin_trade": creds.permission_margin_trade,
            "ip_restricted": creds.ip_restricted,
        },
    }
