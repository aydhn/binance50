import pytest
from binance50.config.models import AppConfig
from binance50.ml.training.model_card import (
    build_model_card, validate_model_card, model_card_to_markdown
)

class MockResult:
    model_id = "1"
    model_name = "name"
    class _TaskType:
        value = "classification"
    task_type = _TaskType()

def test_model_card():
    config = AppConfig()
    res = MockResult()
    manifest = {"dataset_id": "d1"}

    card = build_model_card(res, manifest, config)
    assert card.model_id == "1"
    assert "Research" in card.intended_use

    validate_model_card(card, config)
    md = model_card_to_markdown(card)
    assert "# Model Card" in md
