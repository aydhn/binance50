from typing import Any, Protocol

import pandas as pd

from binance50.indicators.pattern_base import IndicatorContext, PatternCandidate


class PatternBackendAdapter(Protocol):
    def is_available(self) -> bool: ...

    def list_patterns(self) -> list[str]: ...

    def detect_patterns(
        self, df: pd.DataFrame, context: IndicatorContext
    ) -> list[PatternCandidate]: ...

    def availability_report(self) -> dict[str, Any]: ...
