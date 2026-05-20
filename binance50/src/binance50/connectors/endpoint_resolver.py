from pydantic import BaseModel

from binance50.config.models import AppConfig
from binance50.core.enums import EnvironmentProfileName
from binance50.core.exceptions import ConfigValidationError
from binance50.core.network import is_https_url, is_wss_url


class EndpointInfo(BaseModel):
    rest_base_url: str | None = None
    rest_fallback_urls: list[str] = []
    websocket_market_base_url: str | None = None
    websocket_user_base_url: str | None = None
    websocket_api_base_url: str | None = None
    futures_public_ws_base_url: str | None = None
    futures_market_ws_base_url: str | None = None
    futures_private_ws_base_url: str | None = None
    is_testnet: bool = False
    is_mainnet: bool = False
    is_paper: bool = False
    source_profile: EnvironmentProfileName


def validate_endpoint_scheme(url: str | None) -> None:
    if not url:
        return
    if "ws://" in url or "wss://" in url:
        if not is_wss_url(url):
            raise ConfigValidationError(f"Invalid websocket URL scheme: {url}")
    elif ("http://" in url or "https://" in url) and not is_https_url(url):
        raise ConfigValidationError(f"Invalid REST URL scheme: {url}")


def assert_no_endpoint_for_paper_if_disabled(config: AppConfig) -> None:
    pass  # Implementation depending on strictness


def resolve_rest_base_url(config: AppConfig) -> str | None:
    profile = config.selected_environment_profile
    url = profile.endpoints.rest_base_url
    validate_endpoint_scheme(url)
    return url


def resolve_rest_fallback_urls(config: AppConfig) -> list[str]:
    profile = config.selected_environment_profile
    urls = profile.endpoints.rest_fallback_urls
    for url in urls:
        validate_endpoint_scheme(url)
    return urls


def resolve_websocket_market_base_url(config: AppConfig) -> str | None:
    profile = config.selected_environment_profile
    url = profile.endpoints.websocket_market_base_url
    validate_endpoint_scheme(url)
    return url


def resolve_websocket_user_base_url(config: AppConfig) -> str | None:
    profile = config.selected_environment_profile
    url = profile.endpoints.websocket_user_base_url
    validate_endpoint_scheme(url)
    return url


def resolve_futures_routed_ws_base(config: AppConfig, route: str) -> str | None:
    profile = config.selected_environment_profile
    if profile.is_testnet:
        url = "wss://fstream.binancefuture.com"
        validate_endpoint_scheme(url)
        return url
    if route == "public":
        url = "wss://fstream.binance.com/public"
    elif route == "market":
        url = "wss://fstream.binance.com/market"
    elif route == "private":
        url = "wss://fstream.binance.com/private"
    else:
        url = ""
    validate_endpoint_scheme(url)
    return url


def build_endpoint_info(config: AppConfig) -> EndpointInfo:
    profile = config.selected_environment_profile
    info = EndpointInfo(
        rest_base_url=resolve_rest_base_url(config),
        rest_fallback_urls=resolve_rest_fallback_urls(config),
        websocket_market_base_url=resolve_websocket_market_base_url(config),
        websocket_user_base_url=resolve_websocket_user_base_url(config),
        is_testnet=profile.is_testnet,
        is_mainnet=profile.is_mainnet,
        is_paper=profile.is_paper,
        source_profile=profile.profile_name,
    )
    if profile.profile_name == EnvironmentProfileName.COINM_FUTURES_PLACEHOLDER:
        # coinm placeholder endpoints
        pass
    return info
