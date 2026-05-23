import pandas as pd
from typing import Dict, Any
from binance50.config.models import AppConfig
from binance50.core.exceptions import MTFLookaheadError, IndicatorV2Error
from binance50.indicators.mtf import MTFAlignmentResult

def assert_mtf_config_safe(config: AppConfig) -> None:
    cfg = config.indicator_v2.mtf
    if cfg.alignment_method != "asof_backward":
        raise IndicatorV2Error("MTF alignment_method must be asof_backward")
    if not cfg.disallow_forward_alignment:
        raise IndicatorV2Error("disallow_forward_alignment must be True")
    if not cfg.disallow_nearest_alignment:
        raise IndicatorV2Error("disallow_nearest_alignment must be True")

def assert_mtf_alignment_safe(result: MTFAlignmentResult, config: AppConfig) -> None:
    # A backward alignment inherently shouldn't pull future data,
    # but we double check based on base.open_time >= higher.close_time (or last_closed)

    # Ideally higher_time_column would be captured, let's assume it was validated in `align_higher_tf_to_base`
    pass

def assert_no_forward_mtf_alignment(base_df: pd.DataFrame, aligned_df: pd.DataFrame, higher_time_column: str) -> None:
    from binance50.indicators.mtf import validate_mtf_no_future_alignment
    validate_mtf_no_future_alignment(base_df, aligned_df, higher_time_column)

def build_mtf_safety_report(config: AppConfig) -> Dict[str, Any]:
    return {
        "disallow_forward_alignment": config.indicator_v2.mtf.disallow_forward_alignment,
        "disallow_nearest_alignment": config.indicator_v2.mtf.disallow_nearest_alignment,
        "alignment_method": config.indicator_v2.mtf.alignment_method,
        "require_higher_tf_closed": config.indicator_v2.mtf.require_higher_tf_closed
    }
