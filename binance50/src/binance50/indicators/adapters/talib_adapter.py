from typing import Any

import pandas as pd

from binance50.core.exceptions import UnsupportedFeatureError
from binance50.indicators.adapters.base import IndicatorBackendAdapter
from binance50.indicators.context import IndicatorContext
from binance50.indicators.models import IndicatorSpec


class TalibIndicatorAdapter(IndicatorBackendAdapter):
    def __init__(self):
        self._available = False
        self._version = "unknown"
        self._talib = None

        try:
            import talib
            self._available = True
            self._version = talib.__version__
            self._talib = talib
        except ImportError:
            pass

    @property
    def name(self) -> str:
        return "talib_optional"

    def is_available(self) -> bool:
        return self._available

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self._available,
            "version": self._version,
            "supported_functions_count": len(self._talib.get_functions()) if self._available else 0
        }

    def supports_indicator(self, name: str) -> bool:
        if not self._available:
            return False
        # Simplistic mapping or true if we support fallback mapping
        return False # Not implemented fully in Phase 11

    def compute(self, spec: IndicatorSpec, df: pd.DataFrame, context: IndicatorContext) -> pd.DataFrame:
        if not self._available:
             from binance50.core.exceptions import OptionalIndicatorBackendMissingError
             raise OptionalIndicatorBackendMissingError("TA-Lib is not installed")

        raise UnsupportedFeatureError(f"TA-Lib computation not fully mapped for {spec.name} in Phase 11")
