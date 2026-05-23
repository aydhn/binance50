"""Safety module."""

from .divergence_guard import (
    assert_divergence_candidates_safe,
    assert_divergence_config_safe,
    build_divergence_safety_report,
)
from .feature_guard import (
    assert_feature_config_safe,
    assert_feature_count_within_limit,
    assert_feature_dataframe_safe,
    assert_feature_groups_safe,
    assert_no_target_or_future_features,
    build_feature_safety_report,
)
from .mtf_guard import (
    assert_mtf_alignment_safe,
    assert_mtf_config_safe,
    assert_no_forward_mtf_alignment,
    build_mtf_safety_report,
)
