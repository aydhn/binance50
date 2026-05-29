import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.loaders import PortfolioCandidateLoader
from binance50.portfolio.sandbox.models import PortfolioCandidateInput, CandidateSourceType
from binance50.core.exceptions import PortfolioCandidateInputError

def test_validate_candidate_sources_rejects_execution_fields():
    config = AppConfig()
    loader = PortfolioCandidateLoader()

    candidate = PortfolioCandidateInput(
        candidate_id="1",
        source_type=CandidateSourceType.scored_signal,
        source_ids=["src_1"],
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        direction="long",
        source_trace={"id": "1"},
        explanation="Test",
        metadata={"order_id": "12345"} # Forbidden
    )

    with pytest.raises(PortfolioCandidateInputError, match="Execution fields detected"):
        loader.validate_candidate_sources([candidate], config)
