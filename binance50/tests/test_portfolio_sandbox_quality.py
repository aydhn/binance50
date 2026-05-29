import pytest
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.quality import build_portfolio_sandbox_quality_report
from binance50.portfolio.sandbox.models import PortfolioSelectionRunResult, PortfolioSelectionRunRequest, PortfolioSandboxStatus

def test_build_portfolio_sandbox_quality_report():
    config = AppConfig()
    req = PortfolioSelectionRunRequest()
    result = PortfolioSelectionRunResult(request=req, run_id="1", status=PortfolioSandboxStatus.completed)
    report = build_portfolio_sandbox_quality_report(result, config)
    assert report.missing_hash_count == 1 # Since there are no hashes in the empty result
