import pytest
from binance50.config.models import AppConfig
from binance50.safety.ml_blending_leakage_guard import assert_no_forward_or_nearest_alignment, assert_no_label_future_target_columns
from binance50.core.exceptions import MLBlendingLeakageError

def test_forward_alignment_error():
    with pytest.raises(MLBlendingLeakageError):
        assert_no_forward_or_nearest_alignment({"method": "forward"})

def test_label_future_error():
    with pytest.raises(MLBlendingLeakageError):
        assert_no_label_future_target_columns({"label_y": 1})
