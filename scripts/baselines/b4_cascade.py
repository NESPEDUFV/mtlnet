#!/usr/bin/env python
"""B4 — Cascade baseline (CSLSL / CatDM pattern), PINNED SC variant.

==============================================================================
WHAT THIS BASELINE IS
==============================================================================
B4 is a class-(C) CASCADE baseline (per the board integration guide). It
isolates the single factor **"cascade vs parallel"** on the FROZEN champion
substrate and the FROZEN matched heads.

The champion (G / Check2HGI) couples the two tasks SYMMETRICALLY: the
``mtlnet_crossattn`` backbone runs bidirectional cross-attention between the
category stream and the region stream, so information flows cat<->region in
both directions before either head reads it. A CASCADE baseline instead wires a
*directed* edge cat -> region: stage-1 predicts the category, and stage-2
predicts the region CONDITIONED ON the stage-1 prediction, with NO reverse
(region -> cat) path. That directionality IS the baseline's claim (CSLSL
when->what->where; CatDM cat-encoder -> POI-encoder).

This is implemented by REUSING the exact champion heads as the two cascade
stages and reusing the entire frozen training/eval/fold/metric stack — only the
COUPLING changes:

  * Stage-1 (category)  = champion cat head  ``next_gru``.
  * Stage-2 (region)    = champion reg head  ``next_stan_flow_dualtower``,
        but CONDITIONED on stage-1's posterior via the head's already-wired
        ``cond_coupling`` path (the predicted-category signal is injected as an
        input feature of the region head).
  * The symmetric cross-attention backbone is DISABLED
        (``--model-param disable_cross_attn=true``) so the ONLY cat<->region
        information channel is the directed cat -> region cascade edge.
        Without this, the run would be "champion + extra cat->reg edge"
        (a coupling ablation), NOT a cascade. Disabling cross-attn makes the
        comparison a clean cascade-vs-parallel contrast.

PINNED SC variant: a single fixed configuration (no sweep). The pin is
  cond_coupling=posterior  cond_signal=softmax  cond_inject=add
  cond_detach=true         (directed/feed-forward cascade: the region stage
                            READS a category prediction; gradients do NOT flow
                            back cat<-reg through the coupling, matching the
                            staged CSLSL/CatDM training where the upstream
                            "what" stage is not driven by the downstream loss)
  disable_cross_attn=true  (sever the symmetric channel)

==============================================================================
FAITHFULNESS + DEVIATIONS (cite the papers; document every deviation)
==============================================================================
References:
  * CSLSL  (when->what->where): Wang et al., EPJ Data Science 2024.
           https://link.springer.com/article/10.1140/epjds/s13688-024-00460-7
  * CatDM  (two-encoder cat-pref -> POI-pref): Yu et al., WWW 2020.
           https://dl.acm.org/doi/abs/10.1145/3366423.3380202

This is explicitly NOT a faithful CSLSL/CatDM re-implementation (that is
DEFERRED). It is a PATTERN port that isolates the cascade coupling on our board.
Deviations from the source papers (document for the audit log):
  D1. Heads. CSLSL uses three coupled RNN decoders (time->category->location);
      CatDM uses two stacked LSTM preference encoders + a memory module. We
      reuse OUR champion heads (next_gru for cat, next_stan_flow_dualtower for
      reg) as the cascade stages so the ONLY varying factor vs champion G is
      the cat<->reg coupling topology. We do NOT reproduce their decoders.
  D2. No next-POI head. CSLSL/CatDM predict the next POI. Our board's stage-2
      target is the next REGION (TIGER tract), not the POI. So B4 cascades
      cat -> REGION, and there is no POI head. (Region label = the shared
      check2hgi geographic partition, substrate-independent.)
  D3. Labels. Category = 7 Gowalla root classes (not the source papers'
      category vocab). Region = TIGER census tract.
  D4. Substrate. The cascade runs OVER the frozen Check2HGI substrate +
      matched heads, not the source papers' raw-trajectory encoders.
  D5. Coupling injection. We use the head's additive posterior injection
      (zero-init cond_proj, so the untrained cascade head == champion G; the
      coupling is learned from there). This is the iMTL/GETNext input-feature
      coupling form, a faithful realization of "downstream stage reads the
      upstream prediction", but not bit-identical to either paper's gate.

==============================================================================
LEAK-SAFETY (HARD REQUIREMENT)
==============================================================================
B4 has NO pretraining of its own — it is a cascade OVER the frozen substrate
and reuses the champion matched-head MTL pipeline verbatim. Therefore the
train-only-per-fold guarantee is INHERITED structurally:
  * Folds are user-disjoint StratifiedGroupKFold(groups=userid, y=next_cat),
    built by ``FoldCreator._create_check2hgi_mtl_folds`` (same seed, same algo
    as the champion). No baseline-specific resplit.
  * The ONLY fold-sensitive learned artifact is the reg ranking prior log_T,
    which is PER-FOLD PER-SEED (``region_transition_log_seed{S}_fold{N}.pt``)
    built from TRAIN-fold transitions only by
    ``scripts/compute_region_transition.py --per-fold``.
  * This driver PREFLIGHTS the seeded per-fold log_T files (existence + the
    STALE-log_T mtime check vs next_region.parquet) before any scored run and
    REFUSES to launch if they are missing/stale (a stale prior silently
    inflates reg Acc@10 by up to +12pp — CLAUDE.md lesson).
  * SC columns row-alignment is enforced by the pipeline's own hard asserts
    (``len(region_df)==len(X)`` in ``_create_check2hgi_mtl_folds``).
The cat-condition fed to the reg head is the model's OWN predicted-category
posterior computed inside the forward pass on the SAME rows — it carries no
label/val information, so the directed coupling introduces no leak.

==============================================================================
WINDOWING (board adopts overlapping stride-1 for the paper)
==============================================================================
B4 reads the SAME substrate columns the champion reads; it does NOT build its
own sequences. So NOW it runs on the current substrate windowing (whatever
``output/<engine>/<state>/input/next_region.parquet`` was built at). The
paper-grade n=20 stride-1 run is POST-FREEZE (P3) and is produced by pointing
``--engine`` at the stride-1 (overlap) substrate — no change to this driver.

==============================================================================
USAGE
==============================================================================
  # Print the exact pinned cascade command (dry-run, no GPU):
  PYTHONPATH=src python scripts/baselines/b4_cascade.py --print-cmd \
      --state alabama --seed 0

  # Tiny smoke (AL, 1 fold, 2 epochs) — proves plumbing + leak-clean wiring:
  PYTHONPATH=src python scripts/baselines/b4_cascade.py --smoke

  # A scored cell (do NOT run full n=20 from here; the workflow fans this out):
  PYTHONPATH=src python scripts/baselines/b4_cascade.py \
      --state florida --seed 0 --folds 5 --epochs 50
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# --- import the frozen path layer (read-only) -------------------------------
_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
sys.path.insert(0, str(_REPO / "src"))

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR  # noqa: E402

# ---------------------------------------------------------------------------
# The PINNED cascade configuration. These are the only knobs that differ from
# the champion-G matched-head invocation; everything else is the frozen recipe.
# ---------------------------------------------------------------------------
CASCADE_REG_HEAD_PARAMS = {
    # directed cat -> region coupling, realized via the dual-tower head's
    # already-wired conditional-coupling path (zero-init -> == champion G at init).
    "cond_coupling": "posterior",   # inject softmax(cat_logits) into the reg head
    "cond_signal": "softmax",       # posterior signal (CSLSL/CatDM "what" -> "where")
    "cond_inject": "add",           # additive into the fused pooled feature
    # NOTE: capitalized "True" so train.py's _coerce_cli_value maps it to a real
    # bool (lowercase "true" would stay a string).
    "cond_detach": "True",          # FEED-FORWARD cascade: no reverse cat<-reg grad
}
# Sever the symmetric cat<->region channel so the directed cascade edge is the
# ONLY coupling. This is what makes B4 a *cascade* rather than a coupling-ablation.
CASCADE_MODEL_PARAMS = {
    "disable_cross_attn": "True",
}

# Frozen champion / matched-head recipe (B9-style; see CLAUDE.md NORTH_STAR).
CAT_HEAD = "next_gru"
REG_HEAD = "next_stan_flow_dualtower"
MODEL = "mtlnet_crossattn_dualtower"
TASK_SET = "check2hgi_next_region"
DEFAULT_ENGINE = "check2hgi_design_k_resln_mae_l0_1"  # [AUDIT-FIX B4] v14 = the champion-G (v16) substrate
# per RUN_MATRIX L15 + canon.py v16 bundle; makes the cascade coupling the ONLY varying factor vs G.
# _logT_dir() derives --per-fold-transition-dir from args.engine, so this auto-points log_T at the v14 dir.
# (Override with --engine check2hgi only for an explicit GCN substrate-ablation variant.)


def _logT_dir(state: str, engine: str) -> Path:
    return OUTPUT_DIR / engine / state.lower()


def preflight_leak_safe(state: str, seed: int, engine: str, n_folds: int) -> list[str]:
    """Verify the per-fold seeded log_T exists and is NOT stale.

    Returns a list of human-readable problems (empty == OK). A stale or missing
    prior would silently bias reg Acc@10 — we refuse to launch a SCORED run.
    """
    problems: list[str] = []
    d = _logT_dir(state, engine)
    nr = None
    if engine in {e.value for e in EmbeddingEngine}:
        try:
            nr = IoPaths.get_next_region(state, EmbeddingEngine(engine))
        except Exception:
            nr = None
    nr_mtime = nr.stat().st_mtime if (nr and nr.exists()) else None
    for fold in range(1, n_folds + 1):
        f = d / f"region_transition_log_seed{seed}_fold{fold}.pt"
        if not f.exists():
            problems.append(
                f"MISSING per-fold log_T: {f} — build with "
                f"`python scripts/compute_region_transition.py --state {state} "
                f"--per-fold --seed {seed}`"
            )
            continue
        if nr_mtime is not None and f.stat().st_mtime < nr_mtime:
            problems.append(
                f"STALE per-fold log_T: {f} (mtime < next_region.parquet) — "
                f"rebuild with `python scripts/compute_region_transition.py "
                f"--state {state} --per-fold --seed {seed}`"
            )
    return problems


def build_cmd(args) -> list[str]:
    """Assemble the pinned-cascade train.py invocation."""
    engine = args.engine
    logt_dir = str(_logT_dir(args.state, engine))
    cmd = [
        args.python, "scripts/train.py",
        "--task", "mtl",
        "--task-set", TASK_SET,
        "--engine", engine,
        "--state", args.state,
        "--seed", str(args.seed),
        "--folds", str(args.folds),
        "--epochs", str(args.epochs),
        "--batch-size", str(args.batch_size),
        "--model", MODEL,
        "--cat-head", CAT_HEAD,
        "--reg-head", REG_HEAD,
        "--task-a-input-type", "checkin",
        "--task-b-input-type", "region",
        "--per-fold-transition-dir", logt_dir,
        "--checkpoint-selector", "geom_simple",
    ]
    # PIN the cascade coupling (directed cat -> region) on the reg head.
    for k, v in CASCADE_REG_HEAD_PARAMS.items():
        cmd += ["--reg-head-param", f"{k}={v}"]
    # PIN the disabled symmetric channel.
    for k, v in CASCADE_MODEL_PARAMS.items():
        cmd += ["--model-param", f"{k}={v}"]
    if args.no_checkpoints:
        cmd += ["--no-checkpoints"]
    if args.extra:
        # argparse.REMAINDER keeps a leading "--"; drop it for a clean passthrough
        extra = args.extra[1:] if args.extra and args.extra[0] == "--" else args.extra
        cmd += extra
    return cmd


def main() -> int:
    p = argparse.ArgumentParser(description="B4 cascade baseline (PINNED SC variant)")
    p.add_argument("--state", default="alabama")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=2048)
    p.add_argument("--engine", default=DEFAULT_ENGINE,
                   help="substrate engine the cascade runs OVER (default: frozen check2hgi)")
    p.add_argument("--python", default=".venv/bin/python",
                   help="python used to launch train.py (relative to repo root)")
    p.add_argument("--no-checkpoints", action="store_true",
                   help="do not write checkpoints (use for sweeps/smoke)")
    p.add_argument("--print-cmd", action="store_true",
                   help="print the pinned cascade command and exit (dry-run, no GPU)")
    p.add_argument("--smoke", action="store_true",
                   help="tiny AL / 1-fold / 2-epoch / seed-0 smoke run")
    p.add_argument("--skip-leak-preflight", action="store_true",
                   help="(smoke/dev only) skip the per-fold log_T preflight")
    p.add_argument("extra", nargs=argparse.REMAINDER,
                   help="extra args passed through to train.py (after --)")
    args = p.parse_args()

    if args.smoke:
        args.state = "alabama"
        args.seed = 0
        args.folds = 1
        args.epochs = 2
        args.no_checkpoints = True

    cmd = build_cmd(args)

    # Leak-safety preflight (skipped for --print-cmd; the workflow runs it for
    # scored cells). Smoke runs preflight too unless explicitly skipped.
    if not args.print_cmd and not args.skip_leak_preflight:
        problems = preflight_leak_safe(args.state, args.seed, args.engine, args.folds)
        if problems:
            print("LEAK-SAFETY PREFLIGHT FAILED:", file=sys.stderr)
            for prob in problems:
                print(f"  - {prob}", file=sys.stderr)
            print(
                "Refusing to launch a region run with a missing/stale per-fold "
                "log_T prior. Build it, or pass --skip-leak-preflight for a "
                "non-scored dry smoke.",
                file=sys.stderr,
            )
            return 2

    print("=== B4 cascade (PINNED SC) ===")
    print(f"  state={args.state} seed={args.seed} folds={args.folds} "
          f"epochs={args.epochs} engine={args.engine}")
    print(f"  cascade coupling: {CASCADE_REG_HEAD_PARAMS}")
    print(f"  symmetric channel: {CASCADE_MODEL_PARAMS}")
    print("  command:")
    print("    " + " ".join(cmd))

    if args.print_cmd:
        return 0

    return subprocess.call(cmd, cwd=str(_REPO))


if __name__ == "__main__":
    raise SystemExit(main())
