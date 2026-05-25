import hashlib
import json
import random
from typing import Any

from binance50.config.models import AppConfig
from binance50.optimizer.models import ParameterSet, ParameterSpec


def build_default_search_space(config: AppConfig) -> list[ParameterSpec]:
    specs = []
    default_spaces = config.optimizer.default_search_spaces
    for category, params in default_spaces.items():
        for param_path, values in params.items():
            specs.append(
                ParameterSpec(
                    name=param_path.split(".")[-1],
                    path=f"{category}.{param_path}",
                    value_type=type(values[0]).__name__ if values else "str",
                    values=values,
                    description=f"Default search space parameter for {param_path}",
                )
            )
    return specs


def build_search_space_from_config(
    config_section: dict[str, Any], config: AppConfig
) -> list[ParameterSpec]:
    specs = []
    for param_path, values in config_section.items():
        specs.append(
            ParameterSpec(
                name=param_path.split(".")[-1],
                path=param_path,
                value_type=type(values[0]).__name__ if values else "str",
                values=values,
                description=f"Search space parameter from config for {param_path}",
            )
        )
    return specs


def validate_search_space(specs: list[ParameterSpec], config: AppConfig) -> None:
    if not specs and config.optimizer.search_space.reject_empty_space:
        raise ValueError("Search space cannot be empty")

    for spec in specs:
        if (
            config.optimizer.search_space.reject_unbounded_space
            and not spec.values
            and spec.min_value is None
            and spec.max_value is None
        ):
            raise ValueError(f"Unbounded search space for parameter {spec.name}")
        if config.optimizer.search_space.require_parameter_descriptions and not spec.description:
            raise ValueError(f"Parameter description required for {spec.name}")

        # Check execution params
        if not config.optimizer.search_space.allow_execution_params:
            if "execution" in spec.path.lower() or "order" in spec.path.lower():
                raise ValueError(f"Execution parameters are not allowed: {spec.path}")

        # Check live params
        if not config.optimizer.search_space.allow_live_params:
            if "live" in spec.path.lower() or "paper" in spec.path.lower():
                raise ValueError(f"Live/Paper parameters are not allowed: {spec.path}")


def expand_grid_search_space(specs: list[ParameterSpec], config: AppConfig) -> list[ParameterSet]:
    import itertools

    validate_search_space(specs, config)

    keys = [spec.path for spec in specs]
    value_lists = [spec.values for spec in specs]

    combinations = list(itertools.product(*value_lists))

    if len(combinations) > config.optimizer.mode.max_grid_combinations:
        raise ValueError(
            f"Grid search combinations ({len(combinations)}) exceed max limit ({config.optimizer.mode.max_grid_combinations})"
        )

    parameter_sets = []
    for i, combination in enumerate(combinations):
        values = dict(zip(keys, combination, strict=False))

        param_set = ParameterSet(
            parameter_set_id=f"grid_{i}",
            values=values,
            config_patch=build_config_patch(values),
            hash=compute_parameter_set_hash(values),
        )
        parameter_sets.append(param_set)

    return parameter_sets


def sample_random_parameter_set(
    specs: list[ParameterSpec], rng: random.Random, config: AppConfig, set_id: str
) -> ParameterSet:
    values = {}
    for spec in specs:
        if spec.values:
            values[spec.path] = rng.choice(spec.values)
        elif spec.min_value is not None and spec.max_value is not None:
            if spec.value_type == "int":
                values[spec.path] = rng.randint(int(spec.min_value), int(spec.max_value))
            else:
                values[spec.path] = rng.uniform(float(spec.min_value), float(spec.max_value))

    return ParameterSet(
        parameter_set_id=set_id,
        values=values,
        config_patch=build_config_patch(values),
        hash=compute_parameter_set_hash(values),
    )


def compute_search_space_hash(specs: list[ParameterSpec]) -> str:
    spec_dicts = [spec.model_dump(mode="json") for spec in specs]
    spec_str = json.dumps(spec_dicts, sort_keys=True)
    return hashlib.sha256(spec_str.encode()).hexdigest()


def compute_parameter_set_hash(values: dict[str, Any]) -> str:
    values_str = json.dumps(values, sort_keys=True)
    return hashlib.sha256(values_str.encode()).hexdigest()


def build_config_patch(values: dict[str, Any]) -> dict[str, Any]:
    patch = {}
    for path, value in values.items():
        parts = path.split(".")
        current = patch
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
    return patch
