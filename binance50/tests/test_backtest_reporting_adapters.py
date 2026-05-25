import pytest

from binance50.backtest.analytics.adapters.empyrical_adapter import EmpyricalAdapter
from binance50.backtest.analytics.adapters.quantstats_adapter import QuantStatsAdapter
from binance50.config.models import AppConfig


def test_empyrical_adapter_safe_failure():
    adapter = EmpyricalAdapter()
    assert adapter.name == "empyrical"
    assert not adapter.is_available()

    report = adapter.availability_report()
    assert report["available"] is False

    config = AppConfig()
    config.backtest_reporting.adapters.empyrical_optional.fail_if_missing = False
    assert adapter.compute_metrics({}, config) == {}

    config.backtest_reporting.adapters.empyrical_optional.fail_if_missing = True
    with pytest.raises(ImportError):
        adapter.compute_metrics({}, config)


def test_quantstats_adapter_safe_failure():
    adapter = QuantStatsAdapter()
    assert adapter.name == "quantstats"
    assert not adapter.is_available()

    report = adapter.availability_report()
    assert report["available"] is False

    config = AppConfig()
    config.backtest_reporting.adapters.quantstats_optional.fail_if_missing = False
    assert adapter.compute_metrics({}, config) == {}

    config.backtest_reporting.adapters.quantstats_optional.fail_if_missing = True
    with pytest.raises(ImportError):
        adapter.compute_metrics({}, config)
