from typing import Any

import pandas as pd

from binance50.core.exceptions import UnsupportedFeatureError
from binance50.indicators.adapters.base import IndicatorBackendAdapter
from binance50.indicators.context import IndicatorContext
from binance50.indicators.models import IndicatorSpec


class PandasTaIndicatorAdapter(IndicatorBackendAdapter):
    def __init__(self):
        self._available = False
        self._version = "unknown"
        self._pta = None

        try:
            import pandas_ta
            self._available = True
            self._version = pandas_ta.version
            self._pta = pandas_ta
        except ImportError:
            pass

    @property
    def name(self) -> str:
        return "pandas_ta_optional"

    def is_available(self) -> bool:
        return self._available

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self._available,
            "version": self._version,
            "supported_functions_count": 0 # Not queried easily without parsing the module
        }

    def supports_indicator(self, name: str) -> bool:
        if not self._available:
            return False
        return False # Not mapped in Phase 11

    def compute(self, spec: IndicatorSpec, df: pd.DataFrame, context: IndicatorContext) -> pd.DataFrame:
        if not self._available:
             from binance50.core.exceptions import OptionalIndicatorBackendMissingError
             raise OptionalIndicatorBackendMissingError("pandas-ta is not installed")

        raise UnsupportedFeatureError(f"pandas-ta computation not fully mapped for {spec.name} in Phase 11")
