import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import IntentPromotionForbiddenError
from binance50.safety.intent_promotion_guard import assert_promotion_disabled

def test_promotion_disabled():
    config = get_config()
    assert_promotion_disabled(config)
