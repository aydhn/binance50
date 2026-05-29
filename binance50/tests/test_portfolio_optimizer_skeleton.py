import pytest
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.optimizer_skeleton import run_optional_optimizer_skeleton

def test_run_optional_optimizer_skeleton():
    config = AppConfig()
    report = run_optional_optimizer_skeleton([], {}, config)
    assert report.success is False
