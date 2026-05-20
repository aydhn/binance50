import logging
from typing import Any

logger = logging.getLogger(__name__)


def is_spot_sdk_available() -> bool:
    try:
        import binance.spot

        return True
    except ImportError:
        return False


def is_usdm_futures_sdk_available() -> bool:
    try:
        import binance.um_futures

        return True
    except ImportError:
        return False


def is_unofficial_sdk_installed() -> bool:
    try:
        import binance.client

        # python-binance typically has binance.client
        return True
    except ImportError:
        return False


def detect_official_binance_sdks() -> dict[str, Any]:
    return {
        "spot_sdk": is_spot_sdk_available(),
        "usdm_futures_sdk": is_usdm_futures_sdk_available(),
        "unofficial_python_binance": is_unofficial_sdk_installed(),
    }


def build_sdk_availability_report() -> dict[str, Any]:
    res = detect_official_binance_sdks()
    warnings = []
    if res["unofficial_python_binance"]:
        warnings.append(
            "Unofficial python-binance package detected. We recommend official binance-connector-python."
        )
    res["warnings"] = warnings
    return res
