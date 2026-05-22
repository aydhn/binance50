from typing import Any, Protocol

import pandas as pd

from binance50.indicators.context import IndicatorContext
from binance50.indicators.models import IndicatorSpec


class IndicatorBackendAdapter(Protocol):
    @property
    def name(self) -> str:
        ...

    def is_available(self) -> bool:
        ...

    def availability_report(self) -> dict[str, Any]:
        ...

    def supports_indicator(self, name: str) -> bool:
        ...

    def compute(self, spec: IndicatorSpec, df: pd.DataFrame, context: IndicatorContext) -> pd.DataFrame:
        ...
