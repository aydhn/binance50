import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import IntentPromotionForbiddenError
from binance50.execution.promotion import validate_promotion_request, IntentPromotionRequest
from datetime import datetime, timezone

def test_promotion_validation():
    config = get_config()
    req = IntentPromotionRequest("1", "sandbox", "", "test", "test", datetime.now(timezone.utc), {})
    with pytest.raises(IntentPromotionForbiddenError, match="Target mode is missing"):
        validate_promotion_request(req, config)
