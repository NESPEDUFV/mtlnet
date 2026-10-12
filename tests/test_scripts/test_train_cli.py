"""Tests for canonical training CLI experiment overrides."""

import pytest

from configs.experiment import ExperimentConfig
from scripts.train import _apply_cli_overrides, _parse_args


def test_cli_overrides_mtl_model_loss_and_params():
    args = _parse_args([
        "--state", "alabama",
        "--engine", "dgi",
        "--model", "mtlnet_cgc",
        "--model-param", "num_shared_experts=3",
        "--model-param", "num_task_experts=2",
        "--mtl-loss", "static_weight",
        "--category-weight", "0.75",
        "--gradient-accumulation-steps", "4",
    ])
    config = ExperimentConfig.default_mtl("test", "florida", "hgi")

    updated = _apply_cli_overrides(config, args)

    assert updated.state == "alabama"
    assert updated.embedding_engine == "dgi"
    assert updated.model_name == "mtlnet_cgc"
    assert updated.model_params["num_shared_experts"] == 3
    assert updated.model_params["num_task_experts"] == 2
    assert updated.mtl_loss == "static_weight"
    assert updated.mtl_loss_params["category_weight"] == pytest.approx(0.75)
    assert updated.gradient_accumulation_steps == 4


def test_cli_candidate_expands_to_model_loss_and_params():
    args = _parse_args([
        "--candidate", "cgc_equal",
    ])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    updated = _apply_cli_overrides(config, args)

    assert updated.model_name == "mtlnet_cgc"
    assert updated.model_params["num_shared_experts"] == 2
    assert updated.model_params["num_task_experts"] == 1
    assert updated.mtl_loss == "equal_weight"
    assert updated.mtl_loss_params == {}


def test_cli_explicit_flags_override_candidate_defaults():
    args = _parse_args([
        "--candidate", "cgc_equal",
        "--model-param", "num_shared_experts=4",
        "--mtl-loss", "famo",
    ])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    updated = _apply_cli_overrides(config, args)

    assert updated.model_name == "mtlnet_cgc"
    assert updated.model_params["num_shared_experts"] == 4
    assert updated.model_params["num_task_experts"] == 1
    assert updated.mtl_loss == "famo"
    assert updated.mtl_loss_params == {}


def test_cli_candidate_requires_mtl_task():
    args = _parse_args([
        "--candidate", "cgc_equal",
    ])
    config = ExperimentConfig.default_category("test", "florida", "dgi")

    with pytest.raises(ValueError, match="--candidate"):
        _apply_cli_overrides(config, args)


def test_unknown_candidate_reports_available_names():
    args = _parse_args([
        "--candidate", "does_not_exist",
    ])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    with pytest.raises(ValueError, match="Unknown MTL candidate"):
        _apply_cli_overrides(config, args)


def test_cli_does_not_override_config_task_when_task_is_omitted():
    args = _parse_args(["--epochs", "3"])
    config = ExperimentConfig.default_category("test", "florida", "dgi")

    updated = _apply_cli_overrides(config, args)

    assert updated.task_type == "category"
    assert updated.epochs == 3


def test_cli_seed_override():
    args = _parse_args(["--seed", "123"])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    updated = _apply_cli_overrides(config, args)

    assert updated.seed == 123


def test_category_weight_requires_static_weight_loss():
    args = _parse_args(["--category-weight", "0.75"])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    with pytest.raises(ValueError, match="static_weight"):
        _apply_cli_overrides(config, args)


def test_key_value_override_requires_equals():
    args = _parse_args(["--model-param", "bad"])
    config = ExperimentConfig.default_mtl("test", "florida", "dgi")

    with pytest.raises(ValueError, match="KEY=VALUE"):
        _apply_cli_overrides(config, args)
