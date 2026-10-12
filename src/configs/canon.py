"""Canonical version recipe bundles for the ``--canon`` selector (traceback to v11..v16).

The ``mtl_improvement`` study repeatedly flipped train.py's effective recipe (v11 paper
canon → v12 log_T-KD → v15 C25-unweighted → v16 champion **G**). Each version is a *bundle*
of CLI flags. ``--canon vXX`` (default **v18**, the delivered generation on the leak-free
substrate; every earlier version stays reachable, e.g. v17 via ``--canon v17``) injects that bundle BEFORE the
user's own flags so that **explicit flags always override the bundle** (argparse "last value
wins" for store actions). This makes the champion the default while keeping every prior
version reproducible forever with a single ``--canon vNN``.

Scope: ``--canon`` only injects for ``--task mtl`` (the versions are MTL recipes) and is a
no-op when ``--config`` is given. ``--canon none`` disables injection (bare smoke defaults).

**Append-only.** Never edit a frozen bundle (it would silently break that version's
reproduction). Add a new key when a new version is pinned, and update
``docs/results/CANONICAL_VERSIONS.md`` + ``tests/test_configs/test_canon.py``.

Authoritative source for each bundle: ``docs/results/CANONICAL_VERSIONS.md`` (the §vNN blocks
and reproduction maps) + ``docs/NORTH_STAR.md`` (the B9 invocation). The regression test
asserts each bundle resolves to the documented config field-by-field.
"""

from __future__ import annotations

from typing import List

DEFAULT_CANON = "v18"   # delivered generation (2026-09-08): v17's recipe on the leak-free substrate.
                        # Was "v17" from 2026-07-01 to 2026-09-08. v17 pinned check2hgi_design_k_resln_mae_l0_1
                        # (the v14 substrate), so a bare `train.py --task mtl` — or even `train.py --state X`,
                        # since the pre-parser defaults a missing --task to mtl — silently selected a substrate
                        # carrying the consecutive-visit leak, without the user ever typing --engine.
                        # Every prior version stays reproducible: `--canon v11`..`--canon v17`, unchanged.
                        # ⚠ The default reproduces NO published cell: see the v18 note in CANON_BUNDLES below.

# The shared cross-attn "B9" recipe underlying v11/v12/v15 (NORTH_STAR §Champion / CANONICAL_VERSIONS §v12).
_CROSSATTN_B9: List[str] = [
    "--task-set", "check2hgi_next_region",
    "--model", "mtlnet_crossattn",
    "--mtl-loss", "static_weight", "--category-weight", "0.75",
    "--scheduler", "cosine", "--max-lr", "3e-3",
    "--cat-lr", "1e-3", "--reg-lr", "3e-3", "--shared-lr", "1e-3",
    "--alternating-optimizer-step", "--alpha-no-weight-decay", "--min-best-epoch", "5",
    "--cat-head", "next_gru", "--reg-head", "next_getnext_hard",
    "--task-a-input-type", "checkin", "--task-b-input-type", "region",
    "--engine", "check2hgi",                       # frozen GCN paper substrate
    "--folds", "5", "--epochs", "50", "--batch-size", "2048",
]

# v16 champion-G recipe (shared base for v16 + the v17 candidate). Editing this changes BOTH —
# keep it byte-identical to the frozen §0.1-adjacent v16 resolved recipe.
_V16: List[str] = [
    "--task-set", "check2hgi_next_region",
    "--model", "mtlnet_crossattn_dualtower",
    "--reg-head", "next_stan_flow_dualtower",
    "--reg-head-param", "raw_embed_dim=64",
    "--reg-head-param", "fusion_mode=aux",
    "--reg-head-param", "freeze_alpha=True",
    "--reg-head-param", "alpha_init=0.0",
    "--cat-head", "next_gru",
    "--mtl-loss", "static_weight", "--category-weight", "0.75",
    "--scheduler", "onecycle", "--max-lr", "3e-3",
    "--cat-lr", "1e-3", "--reg-lr", "3e-3", "--shared-lr", "1e-3",
    "--log-t-kd-weight", "0.0",
    "--checkpoint-selector", "geom_simple",   # pin explicitly (was the argparse default; identity-preserving)
    "--no-reg-class-weights", "--no-cat-class-weights",
    "--task-a-input-type", "checkin", "--task-b-input-type", "region",
    "--engine", "check2hgi_design_k_resln_mae_l0_1",   # v14 substrate
    "--folds", "5", "--epochs", "50", "--batch-size", "2048",
]

CANON_BUNDLES: dict[str, List[str]] = {
    # v11 — BRACIS paper canon: GCN substrate, log_T-KD OFF, CLASS-WEIGHTED (pre-C25),
    # old joint selector (0.5*(cat+reg)). CANONICAL_VERSIONS §v11 + §v12 reproduction map.
    "v11": _CROSSATTN_B9 + [
        "--log-t-kd-weight", "0.0",
        "--checkpoint-selector", "joint_f1_mean",
        "--reg-class-weights", "--cat-class-weights",
    ],
    # v12 — v11 + log_T-KD W=0.2 ON; still class-WEIGHTED (predates C25); geom_simple selector.
    "v12": _CROSSATTN_B9 + [
        "--log-t-kd-weight", "0.2",
        "--checkpoint-selector", "geom_simple",   # pin explicitly (was the argparse default; identity-preserving)
        "--reg-class-weights", "--cat-class-weights",
    ],
    # v15 — v12 recipe + the C25 fix: BOTH heads UNWEIGHTED (the current bare code default).
    "v15": _CROSSATTN_B9 + [
        "--log-t-kd-weight", "0.2",
        "--checkpoint-selector", "geom_simple",   # pin explicitly (identity-preserving)
        "--no-reg-class-weights", "--no-cat-class-weights",
    ],
    # v16 — CHAMPION "G": reg-private dual-tower (aux fusion, α·log_T prior OFF), v14 substrate,
    # onecycle (NO alt-opt), unweighted, KD OFF, geom_simple selector. CANONICAL_VERSIONS §v16.
    "v16": _V16,
    # v17 — CHAMPION CANDIDATE (n=20-confirmed AL/AZ/FL; CA/TX PENDING): v16 + bs=8192 + per-head
    # cat-lr 1e-3 actually applied (--onecycle-per-head-lr → MTL_ONECYCLE_PER_HEAD_LR). The v16
    # --cat-lr 1e-3 is INERT under onecycle without the flag; the flag is what makes it effective.
    # Beats v16 board-wide (AL +1.0/AZ +2.3 cat; FL +0.17cat/+0.20reg, ~7% faster). Opt-in:
    # v17 is now DEFAULT_CANON (2026-07-01); the env stays default-OFF (v17 sets --onecycle-per-head-lr). CANONICAL_VERSIONS §v17.
    "v17": _V16 + ["--batch-size", "8192", "--onecycle-per-head-lr"],
    # v18 — DELIVERED GENERATION (2026-09-08). v17's recipe moved onto the leak-free substrate,
    # plus the two loss changes the v18 retune settled. This is the first bundle whose --engine
    # is NOT a pre-v18 build: check2hgi_v18 has forward-only consecutive-visit edges, so a node
    # never carries a feature of the target it predicts. v11..v17 all pin leaked substrates and
    # stay that way ON PURPOSE — they reproduce their own versions.
    # Deltas vs v17 (append-only: overrides ride AFTER _V16, argparse last-wins):
    #   --engine            check2hgi_design_k_resln_mae_l0_1 → check2hgi_v18
    #   --category-weight   0.75 → 0.50
    #   --logit-adjust-tau  (absent → 0.0) → 0.5      ← MTL applies it to the CATEGORY head only
    # ⚠ THIS BUNDLE DOES NOT REPRODUCE A DELIVERED CELL, and cannot. Three things a static token
    # list cannot express, all required by docs/studies/closing_data/v18/run_wave.sh:
    #   1. --cat-lr is PER STATE: 1e-3 at AL/AZ/Istanbul, 2e-3 at FL/CA/TX. The 1e-3 below is the
    #      small-state value; large states must pass --cat-lr 2e-3 explicitly.
    #   2. fp32 is set by ENV (MTL_DISABLE_AMP=1); there is no CLI flag for precision, and without
    #      it the CUDA trainer runs fp16 autocast with no GradScaler.
    #   3. Reported cells are seeds {0,1,7,100} × 5 folds; a bare run takes the dev seed 42.
    # Also absent by policy: --compile and --tf32 (DEFAULTS_AND_GUARDS.md forbids them as global
    # defaults). The delivered driver passes --canon none with every flag written out; keep it so.
    "v18": _V16 + [
        "--batch-size", "8192", "--onecycle-per-head-lr",
        "--engine", "check2hgi_v18",
        "--category-weight", "0.50",
        "--logit-adjust-tau", "0.5",
    ],
}

CANON_CHOICES = sorted(CANON_BUNDLES) + ["none"]


def resolve_canon_argv(canon: str | None, argv: List[str]) -> List[str]:
    """Return the effective argv = ``bundle(canon) + argv``.

    The bundle is PREPENDED so the user's own flags (later in argv) override it via
    argparse last-wins. ``canon`` in ``{None, "none"}`` returns argv unchanged.
    """
    if canon in (None, "none"):
        return list(argv)
    if canon not in CANON_BUNDLES:
        raise SystemExit(
            f"--canon: unknown version {canon!r}; choose from {sorted(CANON_BUNDLES)} or 'none'"
        )
    return list(CANON_BUNDLES[canon]) + list(argv)


__all__ = ["DEFAULT_CANON", "CANON_BUNDLES", "CANON_CHOICES", "resolve_canon_argv"]
