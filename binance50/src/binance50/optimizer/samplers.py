import random
from typing import Protocol

from binance50.config.models import AppConfig
from binance50.optimizer.models import ParameterSet, ParameterSpec
from binance50.optimizer.search_space import expand_grid_search_space, sample_random_parameter_set


class BaseParameterSampler(Protocol):
    def generate(self, specs: list[ParameterSpec], config: AppConfig) -> list[ParameterSet]: ...

    def estimate_trial_count(self, specs: list[ParameterSpec], config: AppConfig) -> int: ...


class GridParameterSampler:
    def generate(self, specs: list[ParameterSpec], config: AppConfig) -> list[ParameterSet]:
        return expand_grid_search_space(specs, config)

    def estimate_trial_count(self, specs: list[ParameterSpec], config: AppConfig) -> int:
        count = 1
        for spec in specs:
            if spec.values:
                count *= len(spec.values)
        return count


class RandomParameterSampler:
    def generate(self, specs: list[ParameterSpec], config: AppConfig) -> list[ParameterSet]:
        rng = random.Random(
            config.optimizer.mode.random_seed if config.optimizer.mode.deterministic else None
        )

        max_trials = config.optimizer.mode.max_trials
        parameter_sets = []
        seen_hashes = set()

        attempts = 0
        max_attempts = max_trials * 10

        while len(parameter_sets) < max_trials and attempts < max_attempts:
            attempts += 1
            param_set = sample_random_parameter_set(
                specs, rng, config, f"random_{len(parameter_sets)}"
            )

            if param_set.hash not in seen_hashes:
                seen_hashes.add(param_set.hash)
                parameter_sets.append(param_set)

        return parameter_sets

    def estimate_trial_count(self, specs: list[ParameterSpec], config: AppConfig) -> int:
        return config.optimizer.mode.max_trials
