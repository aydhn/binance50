from binance50.config.models import AppConfig
from binance50.regimes.adapters.gmm_adapter import GMMAdapter
from binance50.regimes.adapters.hmm_adapter import HMMAdapter


def test_gmm_adapter_availability():
    config = AppConfig()
    config.regimes.optional_models["gmm"].enabled = True
    adapter = GMMAdapter(config)
    # Shouldn't crash even if sklearn not installed, just is_installed=False
    report = adapter.availability_report()
    assert report["name"] == "gmm_optional"


def test_hmm_adapter_availability():
    config = AppConfig()
    config.regimes.optional_models["hmm"].enabled = True
    adapter = HMMAdapter(config)
    report = adapter.availability_report()
    assert report["name"] == "hmm_optional"
