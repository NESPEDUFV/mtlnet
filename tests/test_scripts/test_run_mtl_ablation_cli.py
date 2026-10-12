"""Tests for staged ablation CLI control-surface defaults."""

from scripts.run_mtl_ablation import _build_config, _parse_args


def test_manual_profile_preserves_historical_defaults():
    args = _parse_args([])
    config = _build_config(args)

    assert config.epochs == 10
    assert config.folds == 1
    assert config.promote_top == 0
    assert config.promote_epochs == 15
    assert config.promote_folds == 2


def test_quick_profile_applies_preset_values():
    args = _parse_args(["--profile", "quick"])
    config = _build_config(args)

    assert config.epochs == 3
    assert config.folds == 1
    assert config.promote_top == 0
    assert config.promote_epochs == 5
    assert config.promote_folds == 2


def test_explicit_overrides_take_precedence_over_profile():
    args = _parse_args(
        [
            "--profile",
            "staged",
            "--epochs",
            "7",
            "--promote-top",
            "5",
            "--candidate",
            "equal_weight",
            "--candidate",
            "famo",
        ]
    )
    config = _build_config(args)

    assert config.epochs == 7
    assert config.promote_top == 5
    assert config.candidate_names == ("equal_weight", "famo")
