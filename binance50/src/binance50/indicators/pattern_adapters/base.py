import pandas as pd
from typing import List, Dict, Any, Protocol
from binance50.indicators.pattern_base import PatternCandidate, IndicatorContext

class PatternBackendAdapter(Protocol):
    def is_available(self) -> bool:
        ...

    def list_patterns(self) -> List[str]:
        ...

    def detect_patterns(self, df: pd.DataFrame, context: IndicatorContext) -> List[PatternCandidate]:
        ...

    def availability_report(self) -> Dict[str, Any]:
        ...
