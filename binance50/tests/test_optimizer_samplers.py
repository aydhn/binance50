from binance50.config.models import AppConfig
from binance50.optimizer.models import ParameterSpec
from binance50.optimizer.samplers import GridParameterSampler, RandomParameterSampler


def test_grid_sampler_deterministic():
    config = AppConfig()
    specs = [
        ParameterSpec(name="p1", path="p1", value_type="int", values=[1, 2], description="test")
    ]
    sampler = GridParameterSampler()
    sets1 = sampler.generate(specs, config)
    sets2 = sampler.generate(specs, config)
    assert [s.hash for s in sets1] == [s.hash for s in sets2]


def test_random_sampler_deterministic():
    config = AppConfig()
    specs = [
        ParameterSpec(
            name="p1", path="p1", value_type="int", values=[1, 2, 3, 4, 5], description="test"
        )
    ]
    sampler = RandomParameterSampler()
    sets1 = sampler.generate(specs, config)
    sets2 = sampler.generate(specs, config)
    assert [s.hash for s in sets1] == [s.hash for s in sets2]


def test_estimate_trial_count():
    config = AppConfig()
    specs = [
        ParameterSpec(name="p1", path="p1", value_type="int", values=[1, 2], description="test"),
        ParameterSpec(name="p2", path="p2", value_type="int", values=[1, 2, 3], description="test"),
    ]
    sampler = GridParameterSampler()
    assert sampler.estimate_trial_count(specs, config) == 6
