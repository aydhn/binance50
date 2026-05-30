import pytest
from binance50.core.error_classifier import classify_paper_error
from binance50.core.exceptions import PaperIntentError, PaperGatewayError, PaperBalanceError

def test_classify_paper_error():
    assert isinstance(classify_paper_error("some testnet intent error"), PaperIntentError)
    assert isinstance(classify_paper_error("bad network call"), PaperGatewayError)
    assert isinstance(classify_paper_error("negative cash detected"), PaperBalanceError)
    assert isinstance(classify_paper_error("unknown error"), Exception)
