import pytest

from binance50.config.models import AppConfig
from binance50.optimizer.search_space import (
    ParameterSpec,
    build_config_patch,
    build_default_search_space,
    compute_search_space_hash,
    expand_grid_search_space,
    validate_search_space,
)


def test_default_search_space_build():
    config = AppConfig()
    specs = build_default_search_space(config)
    assert len(specs) > 0
    assert any(s.name == "min_adx" for s in specs)
    assert any(s.name == "rsi_oversold" for s in specs)


def test_search_space_hash_deterministic():
    config = AppConfig()
    specs = build_default_search_space(config)
    hash1 = compute_search_space_hash(specs)
    hash2 = compute_search_space_hash(specs)
    assert hash1 == hash2


def test_empty_space_reject():
    config = AppConfig()
    with pytest.raises(ValueError):
        validate_search_space([], config)


def test_unbounded_space_reject():
    config = AppConfig()
    specs = [ParameterSpec(name="test", path="test", value_type="int", description="test")]
    with pytest.raises(ValueError, match="Unbounded"):
        validate_search_space(specs, config)


def test_missing_description_reject():
    config = AppConfig()
    specs = [
        ParameterSpec(name="test", path="test", value_type="int", values=[1, 2], description="")
    ]
    with pytest.raises(ValueError, match="description required"):
        validate_search_space(specs, config)


def test_execution_param_reject():
    config = AppConfig()
    specs = [
        ParameterSpec(
            name="execution_quantity",
            path="execution.quantity",
            value_type="int",
            values=[1, 2],
            description="test",
        )
    ]
    with pytest.raises(ValueError, match="Execution parameters are not allowed"):
        validate_search_space(specs, config)


def test_grid_expansion():
    config = AppConfig()
    specs = [
        ParameterSpec(name="p1", path="a.p1", value_type="int", values=[1, 2], description="test"),
        ParameterSpec(name="p2", path="a.p2", value_type="int", values=[3, 4], description="test"),
    ]
    sets = expand_grid_search_space(specs, config)
    assert len(sets) == 4


def test_build_config_patch():
    patch = build_config_patch({"strategy.min_adx": 20.0})
    assert patch == {"strategy": {"min_adx": 20.0}}
