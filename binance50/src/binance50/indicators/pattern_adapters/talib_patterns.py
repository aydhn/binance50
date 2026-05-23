import pandas as pd
from typing import List, Dict, Any

from .base import PatternBackendAdapter
from binance50.indicators.pattern_base import PatternCandidate, IndicatorContext

class TaLibPatternAdapter(PatternBackendAdapter):
    def __init__(self):
        self._talib = None
        self._available = False
        self._check_availability()

    @property
    def name(self) -> str:
        return "talib_adapter"

    def _check_availability(self):
        try:
            import talib
            self._talib = talib
            self._available = True
        except ImportError:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def list_patterns(self) -> List[str]:
        if not self._available:
            return []
        # Return a sample
        return ["CDLDOJI", "CDLENGULFING", "CDLHAMMER"]

    def detect_patterns(self, df: pd.DataFrame, context: IndicatorContext) -> List[PatternCandidate]:
        if not self._available or not context.config.indicator_v2.patterns.talib_pattern_adapter_enabled:
            if context.config.indicator_v2.patterns.fail_if_talib_missing:
                from binance50.core.exceptions import PatternAdapterError
                raise PatternAdapterError("TA-Lib is not available but fail_if_talib_missing is True")
            return []

        # Return empty for skeleton
        return []

    def availability_report(self) -> Dict[str, Any]:
        return {
            "available": self._available,
            "pattern_count": len(self.list_patterns()),
            "sample_patterns": self.list_patterns()[:3]
        }
