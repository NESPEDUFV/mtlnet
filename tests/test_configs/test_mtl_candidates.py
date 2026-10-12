"""Tests for reusable MTL candidate matrix."""

import pytest
import torch

from ablation.candidates import get_candidate, iter_candidates
from models.registry import create_model


def test_phase1_candidates_include_simple_weighting_grid():
    names = {candidate.name for candidate in iter_candidates("phase1")}

    assert "baseline_nash" in names
    assert "equal_weight" in names
    assert "static_cat_025" in names
    assert "static_cat_050" in names
    assert "static_cat_075" in names
    assert "uncertainty_weighting" in names
    assert "uw_so_t05" in names
    assert "uw_so_t10" in names
    assert "uw_so_t20" in names
    assert "famo" in names
    assert "random_weight" in names
    assert "fairgrad_a10" in names
    assert "fairgrad_a20" in names
    assert "bayesagg_mtl" in names
    assert "go4align" in names
    assert "excess_mtl" in names
    assert "stch" in names
    assert "db_mtl" in names


def test_phase2_candidates_include_architecture_grid():
    names = {candidate.name for candidate in iter_candidates("phase2")}

    assert "mmoe_equal" in names
    assert "cgc_equal" in names
    assert "cgc_equal_s1t1" in names
    assert "cgc_equal_s2t2" in names
    assert "cgc_equal_s4t1" in names
    assert "arch_mtlnet_equal" in names
    assert "arch_mmoe_e4_equal" in names
    assert "arch_cgc_s2t1_equal" in names
    assert "arch_dselectk_e4k2_equal" in names


def test_candidate_builds_config_with_overrides():
    candidate = get_candidate("cgc_equal")

    config = candidate.build_config(
        state="alabama",
        engine="dgi",
        epochs=3,
        folds=1,
    )

    assert config.name == "cgc_equal_alabama_dgi"
    assert config.state == "alabama"
    assert config.embedding_engine == "dgi"
    assert config.model_name == "mtlnet_cgc"
    assert config.model_params["num_shared_experts"] == 2
    assert config.model_params["num_task_experts"] == 1
    assert config.mtl_loss == "equal_weight"
    assert config.k_folds == 2


def test_candidate_command_uses_canonical_cli_flags():
    candidate = get_candidate("static_cat_075")

    command = candidate.command(
        state="alabama",
        engine="dgi",
        epochs=3,
        folds=1,
    )

    assert "scripts/train.py" in command
    assert "--mtl-loss static_weight" in command
    assert "--category-weight 0.75" in command


def test_unknown_candidate_raises():
    with pytest.raises(KeyError, match="Unknown MTL candidate"):
        get_candidate("does_not_exist")


def test_dselectk_candidate_builds_config_with_model_params():
    candidate = get_candidate("arch_dselectk_e4k2_db_mtl")

    config = candidate.build_config(
        state="alabama",
        engine="dgi",
        epochs=3,
        folds=1,
    )

    assert config.model_name == "mtlnet_dselectk"
    assert config.model_params["num_experts"] == 4
    assert config.model_params["num_selectors"] == 2
    assert config.model_params["temperature"] == 0.5
    assert config.mtl_loss == "db_mtl"
    assert config.mtl_loss_params["beta"] == pytest.approx(0.9)


def _all_candidate_names():
    """Collect all candidate names across all phases."""
    names = []
    for c in iter_candidates("all"):
        names.append(c.name)
    return names


@pytest.mark.parametrize("candidate_name", _all_candidate_names())
def test_candidate_instantiates_model_and_forward_passes(candidate_name):
    """Each candidate must produce a config that builds a working model."""
    candidate = get_candidate(candidate_name)
    config = candidate.build_config(
        state="florida", engine="dgi", epochs=1, folds=1,
    )

    model = create_model(config.model_name, **config.model_params)
    model.eval()

    # Synthetic inputs matching the expected shapes
    batch = 4
    feature_size = config.model_params.get("feature_size", 64)
    seq_len = config.model_params.get("seq_length", 9)

    cat_input = torch.randn(batch, feature_size)
    next_input = torch.randn(batch, seq_len, feature_size)

    with torch.no_grad():
        cat_out, next_out = model((cat_input, next_input))

    num_classes = config.model_params.get("num_classes", 7)
    assert cat_out.shape == (batch, num_classes)
    assert next_out.shape == (batch, num_classes)
