import inspect
from typing import Any

import pandas as pd

from binance50.core.exceptions import UnsupportedFeatureError
from binance50.indicators.adapters.base import IndicatorBackendAdapter
from binance50.indicators.context import IndicatorContext
from binance50.indicators.models import IndicatorSpec
from binance50.indicators.registry import IndicatorRegistry


class NativeIndicatorAdapter(IndicatorBackendAdapter):
    def __init__(self, registry: IndicatorRegistry):
        self.registry = registry

    @property
    def name(self) -> str:
        return "native"

    def is_available(self) -> bool:
        return True

    def availability_report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": True,
            "version": "1.0.0",
            "supported_functions_count": len(self.registry._specs)
        }

    def supports_indicator(self, name: str) -> bool:
        return name in self.registry._specs

    def compute(self, spec: IndicatorSpec, df: pd.DataFrame, context: IndicatorContext) -> pd.DataFrame:
        func = self.registry.get_func(spec.name)
        if not func:
            raise UnsupportedFeatureError(f"Native implementation not found for {spec.name}")

        kwargs = {}
        sig = inspect.signature(func)

        # Map DataFrame columns to function arguments based on input_columns
        # For simplicity, if input_columns is ["close"], we pass df["close"] as first arg.
        # If it's ["high", "low", "close"], we pass df["high"], df["low"], df["close"].
        # Actually better to rely on parameter matching or explicit input_columns order:
        args = [df[col] for col in spec.input_columns]

        # Add the rest of the parameters from spec.parameters
        for k, v in spec.parameters.items():
            if k in sig.parameters:
                kwargs[k] = v

        res = func(*args, **kwargs)

        if isinstance(res, pd.Series):
            res = res.to_frame(name=spec.output_columns[0])

        return res
