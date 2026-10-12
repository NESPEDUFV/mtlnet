"""Tests for standalone head ablation candidates and CLI."""

import pytest
import torch

from ablation.candidates import (
    HeadCandidate,
    get_head_candidate,
    iter_head_candidates,
)
from models.registry import create_model
from scripts.run_head_ablation import _parse_args


# -- Candidate enumeration --

def test_category_candidates_exist():
    cat_candidates = iter_head_candidates("category")
    names = {c.name for c in cat_candidates}
    assert "cat_ensemble" in names
    assert "cat_single" in names
    assert "cat_attention" in names
    assert "cat_transformer" in names
    assert "cat_gated" in names
    assert "cat_residual" in names
    assert "cat_dcn" in names
    assert "cat_se" in names
    assert "cat_linear" in names
    assert len(names) == 9


def test_next_candidates_exist():
    next_candidates = iter_head_candidates("next")
    names = {c.name for c in next_candidates}
    assert "next_single" in names
    assert "next_mtl" in names
    assert "next_lstm" in names
    assert "next_gru" in names
    assert "next_temporal_cnn" in names
    assert "next_hybrid" in names
    assert "next_transformer_opt" in names
    assert "next_tcn_residual" in names
    assert "next_conv_attn" in names
    assert "next_transformer_relpos" in names
    assert len(names) == 10


def test_iter_all_returns_both_tasks():
    all_candidates = iter_head_candidates("all")
    tasks = {c.task for c in all_candidates}
    assert tasks == {"category", "next"}
    assert len(all_candidates) == 19


def test_unknown_head_candidate_raises():
    with pytest.raises(KeyError, match="Unknown head candidate"):
        get_head_candidate("does_not_exist")


# -- Config building --

def test_category_candidate_builds_config():
    candidate = get_head_candidate("cat_gated")
    config = candidate.build_config("florida", "dgi", epochs=3, folds=1)
    assert config.task_type == "category"
    assert config.model_name == "category_gated"
    assert config.state == "florida"
    assert config.epochs == 3


def test_next_candidate_builds_config():
    candidate = get_head_candidate("next_lstm")
    config = candidate.build_config("florida", "hgi", epochs=5, folds=2)
    assert config.task_type == "next"
    assert config.model_name == "next_lstm"
    assert config.epochs == 5


# -- Model instantiation + forward pass for all candidates --

def _all_head_candidate_names():
    return [c.name for c in iter_head_candidates("all")]


@pytest.mark.parametrize("candidate_name", _all_head_candidate_names())
def test_head_candidate_instantiates_and_forward_passes(candidate_name):
    """Each head candidate must build a model that forward-passes."""
    candidate = get_head_candidate(candidate_name)
    config = candidate.build_config("florida", "dgi", epochs=1, folds=1)

    model = create_model(config.model_name, **config.model_params)
    model.eval()

    batch = 4
    num_classes = config.model_params.get("num_classes", 7)

    if candidate.task == "category":
        input_dim = config.model_params.get("input_dim", 64)
        x = torch.randn(batch, input_dim)
    else:
        embed_dim = config.model_params.get("embed_dim", 64)
        seq_length = config.model_params.get("seq_length", 9)
        x = torch.randn(batch, seq_length, embed_dim)

    with torch.no_grad():
        out = model(x) if candidate.task == "category" else model(x)
        # Some next models return (logits, attention), handle both
        if isinstance(out, tuple):
            out = out[0]

    assert out.shape == (batch, num_classes)


# -- Command generation --

def test_command_uses_correct_task():
    candidate = get_head_candidate("next_gru")
    cmd = candidate.command("florida", "hgi", epochs=10, folds=2)
    assert "--task next" in cmd
    assert "--model next_gru" in cmd


def test_command_includes_model_params():
    candidate = get_head_candidate("cat_single")
    cmd = candidate.command("florida", "dgi", epochs=5, folds=1)
    assert "--model-param" in cmd
    assert "hidden_dims" in cmd


# -- CLI parsing --

def test_cli_defaults():
    args = _parse_args([])
    assert args.task == "category"
    assert args.state == "alabama"
    assert args.engine == "dgi"
    assert args.epochs == 10
    assert args.folds == 1
    assert args.candidate == []


def test_cli_task_and_candidates():
    args = _parse_args([
        "--task", "next",
        "--candidate", "next_lstm",
        "--candidate", "next_gru",
        "--epochs", "20",
    ])
    assert args.task == "next"
    assert args.candidate == ["next_lstm", "next_gru"]
    assert args.epochs == 20
