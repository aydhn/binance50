from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime
from binance50.regimes.stability import compute_stability_score_for_window


def test_stability_scoring():
    config = AppConfig()
    labels = [MarketRegime.trend_up] * 10
    score = compute_stability_score_for_window(labels, config)
    assert score == 100.0

    labels_mixed = [MarketRegime.trend_up] * 5 + [MarketRegime.trend_down] * 5
    score2 = compute_stability_score_for_window(labels_mixed, config)
    assert score2 == 50.0
