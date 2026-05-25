from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig


class WalkForwardWindow(BaseModel):
    window_id: int
    train_start: int | None = None
    train_end: int | None = None
    validation_start: int | None = None
    validation_end: int | None = None
    test_start: int | None = None
    test_end: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WalkForwardPlan(BaseModel):
    plan_id: str
    windows: list[WalkForwardWindow]
    full_run_deferred: bool = True
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_walk_forward_plan(df: pd.DataFrame, config: AppConfig) -> WalkForwardPlan:
    if not config.optimizer.data_split.walk_forward_skeleton_enabled:
        return WalkForwardPlan(plan_id="disabled", windows=[], full_run_deferred=True)

    # Placeholder for actual window calculation logic (e.g. rolling expanding window)
    windows = [
        WalkForwardWindow(
            window_id=1,
            train_start=0,
            train_end=1000,
            validation_start=1000,
            validation_end=1500,
            test_start=1500,
            test_end=2000,
        )
    ]

    plan = WalkForwardPlan(
        plan_id="wf_plan_v1",
        windows=windows,
        full_run_deferred=config.optimizer.data_split.walk_forward_full_run_deferred,
    )

    validate_walk_forward_plan(plan, config)
    return plan


def validate_walk_forward_plan(plan: WalkForwardPlan, config: AppConfig) -> None:
    for window in plan.windows:
        if (
            window.train_end
            and window.validation_start
            and window.train_end >= window.validation_start
        ):
            raise ValueError(f"Overlap in window {window.window_id}: train_end >= validation_start")
        if (
            window.validation_end
            and window.test_start
            and window.validation_end >= window.test_start
        ):
            raise ValueError(f"Overlap in window {window.window_id}: validation_end >= test_start")


def summarize_walk_forward_plan(plan: WalkForwardPlan) -> dict:
    return plan.model_dump()
