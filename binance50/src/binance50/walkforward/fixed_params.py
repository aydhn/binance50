import hashlib
import json
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.models import (
    WalkForwardWindow,
    WalkForwardWindowResult,
    WalkForwardWindowStatus,
)


class FixedParameterRunConfig(BaseModel):
    parameter_set: dict[str, Any]
    source: str = "manual"
    description: str = ""
    hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.hash:
            param_str = json.dumps(self.parameter_set, sort_keys=True)
            self.hash = hashlib.sha256(param_str.encode("utf-8")).hexdigest()


def build_fixed_parameter_set_from_config(
    config: AppConfig, parameter_set: dict[str, Any]
) -> FixedParameterRunConfig:
    validate_fixed_parameter_set(parameter_set, config)
    return FixedParameterRunConfig(parameter_set=parameter_set)


def run_fixed_params_for_window(
    window: WalkForwardWindow,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_request: Any,
    config: AppConfig,
) -> WalkForwardWindowResult:
    # Dummy implementation - in a real scenario this would execute the strategy logic with the fixed parameters
    return WalkForwardWindowResult(
        window_id=window.window_id,
        status=WalkForwardWindowStatus.completed,
        selected_parameter_set=base_request.parameter_set
        if hasattr(base_request, "parameter_set")
        else {},
        metadata={"fixed_params": True},
    )


def validate_fixed_parameter_set(parameter_set: dict[str, Any], config: AppConfig) -> None:
    forbidden_keys = [
        "order_id",
        "client_order_id",
        "exchange_order_id",
        "api_key",
        "signature",
        "listenKey",
        "live_order",
        "testnet_order",
        "paper_order",
        "real_order",
        "execution_gateway",
    ]
    for key in forbidden_keys:
        if key in parameter_set:
            raise ValueError(f"Fixed parameter set cannot contain execution parameter: {key}")
