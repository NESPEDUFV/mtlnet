"""Coverage for the log_T-inert predicate behind the MTL_SKIP_INERT_LOGT opt-in
(``_log_t_is_inert`` in mtl_cv). Inert ⟺ the reg head's α·log_T prior is OFF
(freeze_alpha=True AND alpha_init=0.0) AND every KD route (log_T / log_C / cat) is
off — exactly the champion. Only then can the per-fold log_T load be skipped without
changing the loss (the head folds log_T into an α=0 multiply).
"""

from types import SimpleNamespace

import pytest

from training.runners.mtl_cv import _log_t_is_inert, _resolve_per_fold_priors


def _cfg(**kw):
    base = dict(log_t_kd_weight=0.0, log_c_kd_weight=0.0, cat_kd_weight=0.0)
    base.update(kw)
    return SimpleNamespace(**base)


def _ts(head_params):
    return SimpleNamespace(task_b=SimpleNamespace(head_params=head_params))


def test_champion_is_inert():
    # freeze_alpha=True + alpha_init=0.0 + KD off → inert (the closing_data champion)
    assert _log_t_is_inert(_cfg(), _ts({"freeze_alpha": True, "alpha_init": 0.0})) is True


def test_alpha_prior_on_is_not_inert():
    # alpha_init != 0 → the head prior is live
    assert _log_t_is_inert(_cfg(), _ts({"freeze_alpha": True, "alpha_init": 0.1})) is False
    # learnable α (not frozen) → live even if it starts at 0
    assert _log_t_is_inert(_cfg(), _ts({"freeze_alpha": False, "alpha_init": 0.0})) is False


def test_any_kd_route_blocks_inert():
    ts = _ts({"freeze_alpha": True, "alpha_init": 0.0})
    # the KD teacher IS the per-fold log_T / log_C buffer → not inert when any KD is on
    assert _log_t_is_inert(_cfg(log_t_kd_weight=0.2), ts) is False
    assert _log_t_is_inert(_cfg(log_c_kd_weight=0.5), ts) is False
    assert _log_t_is_inert(_cfg(cat_kd_weight=0.5), ts) is False


def test_default_alpha_init_is_conservative():
    # No alpha_init key → default 0.1 (the head's default) → treated as ACTIVE, not inert.
    assert _log_t_is_inert(_cfg(), _ts({"freeze_alpha": True})) is False
    # No freeze_alpha key → learnable α → active.
    assert _log_t_is_inert(_cfg(), _ts({"alpha_init": 0.0})) is False


def test_missing_task_b_is_not_inert():
    assert _log_t_is_inert(_cfg(), SimpleNamespace(task_b=None)) is False


# --- the MTL_SKIP_INERT_LOGT opt-in inside _resolve_per_fold_priors ----------------

def _resolver_cfg(per_fold_dir):
    ts = _ts({"freeze_alpha": True, "alpha_init": 0.0})  # inert (champion)
    return SimpleNamespace(
        model_params={"task_set": ts},
        per_fold_transition_dir=str(per_fold_dir),
        seed=0, k_folds=2, state="alabama", embedding_engine="check2hgi_dk_ovl",
        log_t_kd_weight=0.0, log_c_kd_weight=0.0, cat_kd_weight=0.0,
    )


def test_inert_skip_is_the_DEFAULT(monkeypatch, tmp_path):
    """DEFAULT (env unset): an inert champion skips the load + guards and returns the SAME
    model_params — even when the per-fold dir holds NO log_T files (the champion no longer
    needs them). This is the flipped default (2026-06-26)."""
    cfg = _resolver_cfg(tmp_path / "no_such_dir")  # dir does not exist / is empty
    monkeypatch.delenv("MTL_SKIP_INERT_LOGT", raising=False)  # default
    out = _resolve_per_fold_priors(cfg, 0)
    assert out is cfg.model_params  # unchanged, no swap, no file access
    # explicit =1 is equivalent to the default
    monkeypatch.setenv("MTL_SKIP_INERT_LOGT", "1")
    assert _resolve_per_fold_priors(cfg, 0) is cfg.model_params


def test_optout_zero_restores_the_legacy_guard(monkeypatch, tmp_path):
    """MTL_SKIP_INERT_LOGT=0 opts OUT → even an inert config hits the leak-guard
    file-resolution and raises on the missing per-fold log_T (legacy behaviour on demand)."""
    cfg = _resolver_cfg(tmp_path)  # exists but empty → file missing
    monkeypatch.setenv("MTL_SKIP_INERT_LOGT", "0")
    with pytest.raises(FileNotFoundError):
        _resolve_per_fold_priors(cfg, 0)


def test_active_prior_never_skips_even_by_default(monkeypatch, tmp_path):
    """Default-on, but the prior is ACTIVE (α-prior live) → must NOT skip; the guard fires
    (the skip only ever applies to a provably-inert prior)."""
    ts = _ts({"freeze_alpha": True, "alpha_init": 0.1})  # active → not inert
    cfg = SimpleNamespace(
        model_params={"task_set": ts},
        per_fold_transition_dir=str(tmp_path),
        seed=0, k_folds=2, state="alabama", embedding_engine="check2hgi_dk_ovl",
        log_t_kd_weight=0.0, log_c_kd_weight=0.0, cat_kd_weight=0.0,
    )
    monkeypatch.delenv("MTL_SKIP_INERT_LOGT", raising=False)  # default-on
    with pytest.raises(FileNotFoundError):
        _resolve_per_fold_priors(cfg, 0)
