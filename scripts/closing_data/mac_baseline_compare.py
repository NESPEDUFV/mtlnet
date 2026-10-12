#!/usr/bin/env python3
"""Mac (MPS) matched-head STL baseline comparison driver (closing_data board §3).

For one (state, baseline): train our STL cat head (next_gru) and STL reg head
(next_stan_flow) on the baseline embedding, seed 0 x 5 folds, DEVICE-INTERNAL on MPS
(fp32). The Check2HGI(dk_ovl) side is run separately (same recipe, --engine
check2hgi_dk_ovl); the board Δ = baseline vs that.

Per fold f:
  1. stage the per-fold leak-safe cell embedding -> output/<engine>/<state>/embeddings.parquet
     (b2c is fold-independent -> staged once); symlink region/poi from check2hgi.
  2. build the engine's stride-1 inputs: generate_next_input_from_checkins(stride=1)
     + build_next_region_for  (windowing-matched to the board base).
  3. stage+freshen the seeded per-fold log_T (canonical region prior) into the engine dir.
  4. CAT:  train.py --task next --cat-head next_gru   --only-fold f   -> macro-F1 (fold f)
     REG:  p1_region_head_ablation.py next_stan_flow --input-type region --only-fold f -> Acc@10 (fold f)
Writes docs/results/closing_data/baseline_compare/<state>_<baseline>.json (per-fold + aggregate).

NOT a rebuild: reuses the pulled board cells. b2c is the only one cheap to regenerate, but we
stage it too for uniformity. Run ONE baseline at a time (MPS); the driver serializes cat then reg
per fold by default (--parallel-heads to overlap on small states).

Usage:
  PYTHONPATH=src MTL_RAM_HEADROOM_GB=2 .venv/bin/python scripts/closing_data/mac_baseline_compare.py \
      --state alabama --baseline b2c --cells-root "/Volumes/Vitor's SSD/ingred/output"
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
for p in (str(_root), str(_root / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

ENGINE = {  # baseline key -> EmbeddingEngine value + on-disk board dir
    "b2c": ("baseline_b2c_onehot64", "baseline_b2c_onehot64", False),  # (engine, dir, per_fold?)
    "b2b": ("baseline_geotree_skipgram", "board_baselines/b2b", True),
    "ctle": ("check2hgi_ctle", "board_baselines/ctle", True),
    "poi2vec": ("baseline_b2a_poi2vec", "board_baselines/poi2vec", True),
}
REPO = _root
# OUTPUT_DIR-aware so parallel single-fold runs can isolate each fold in its own output
# tree (OUTPUT_DIR=output_f{f}) without clobbering the shared engine dir. Default = output/.
OUT = Path(os.environ.get("OUTPUT_DIR", REPO / "output"))
CANON = "output/check2hgi/{state}"  # graph maps + log_T source
# Child subprocesses must use the SAME interpreter as this parent. On the Mac board
# that is .venv/bin/python; on the H100/A40 conda boards there is no .venv, so default
# to sys.executable (universally correct). BASELINE_PY overrides if ever needed.
PY = os.environ.get("BASELINE_PY") or sys.executable


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def cell_emb(cells_root: Path, baseline: str, state: str, fold: int) -> Path:
    engine, bdir, per_fold = ENGINE[baseline]
    if not per_fold:
        return cells_root / bdir / state / "embeddings.parquet"
    return cells_root / bdir / state / f"s0_f{fold}" / "embeddings.parquet"


def stage(baseline: str, state: str, src_emb: Path):
    """Stage embeddings.parquet + region/poi symlinks into output/<engine>/<state>/."""
    engine, _, _ = ENGINE[baseline]
    dst = OUT / engine / state
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_emb, dst / "embeddings.parquet")
    for f in ("region_embeddings.parquet", "poi_embeddings.parquet"):
        s = OUT / "check2hgi" / state / f
        d = dst / f
        if d.exists() or d.is_symlink():
            d.unlink()
        if s.exists():
            d.symlink_to(s.resolve())


def build_inputs(baseline: str, state: str):
    from configs.paths import EmbeddingEngine
    from data.inputs.builders import generate_next_input_from_checkins
    from scripts.baselines.build_b2c_onehot64_substrate import build_next_region_for
    engine = EmbeddingEngine(ENGINE[baseline][0])
    # min_sequence_length=10 to MATCH the dk_ovl board base (build_overlap_probe_engine
    # BOARD_MIN_SEQ=10). The default is 5; for the board states it happens to emit the
    # same rows (gated window=9 ⇒ users with <10 ck emit 0 windows), but pinning 10
    # GUARANTEES the baseline and the Check2HGI-SC comparand are scored on the identical
    # row set + fold partition — required for a valid CTLE-SC vs Check2HGI-SC Δ.
    generate_next_input_from_checkins(state, engine, stride=1, min_sequence_length=10)
    build_next_region_for(state, engine)


def stage_logt(baseline: str, state: str):
    """Build the per-fold seeded log_T over THIS engine's OWN stride-1 partition (C29
    engine-aware) -> output/<engine>/<state>/, NOT a copy of the canonical stride-9 prior.
    Copying the canonical prior leaks (its user->fold partition differs from the trainer's
    stride-1 split). Must run AFTER build_inputs (so the engine has input/next.parquet ->
    _resolve_split_engine uses the engine's own stride-1 split, not canonical fallback).
    The build writes after next_region -> mtime-fresh; payload carries engine provenance."""
    engine, _, _ = ENGINE[baseline]
    env = {**os.environ, "PYTHONPATH": "src", "MTL_RAM_HEADROOM_GB": "2", "OMP_NUM_THREADS": "4"}
    cmd = [PY, "scripts/compute_region_transition.py", "--state", state,
           "--engine", engine, "--per-fold", "--seed", "0", "--n-splits", "5"]
    subprocess.run(cmd, env=env, cwd=str(REPO), check=True)


def run_cat(engine: str, state: str, fold: int) -> dict:
    env = {**os.environ, "PYTHONPATH": "src", "MTL_RAM_HEADROOM_GB": "2", "OMP_NUM_THREADS": "4"}
    cmd = [PY, "scripts/train.py", "--task", "next", "--engine", engine, "--state", state,
           "--seed", "0", "--only-fold", str(fold), "--cat-head", "next_gru",
           "--epochs", "50", "--batch-size", "2048"]
    subprocess.run(cmd, env=env, cwd=str(REPO), check=True)
    # read the newest rundir's fold report
    rdir = REPO / "results" / engine / state
    runs = sorted([p for p in rdir.glob("next_*") if p.is_dir()], key=lambda p: p.stat().st_mtime)
    # --only-fold writes a single report named fold1_* (loop position, not true index); grab it.
    reps = sorted((runs[-1] / "folds").glob("fold*_next_report.json"))
    # an --only-fold run writes EXACTLY one report; fail loud if not (don't silently mis-score).
    if len(reps) != 1:
        raise RuntimeError(f"expected exactly 1 fold report in {runs[-1]}/folds, found {len(reps)}: {reps}")
    d = json.loads(reps[0].read_text())
    return {"macro_f1": float(d["macro avg"]["f1-score"]) * 100.0}


def run_reg(engine: str, state: str, fold: int) -> dict:
    env = {**os.environ, "PYTHONPATH": "src", "MTL_RAM_HEADROOM_GB": "2", "OMP_NUM_THREADS": "4"}
    tag = f"blcmp_{engine}_f{fold}"
    # ⚠ --input-type CHECKIN (not region): with --input-type region p1 hardcodes the check2hgi
    # region embedding (_load_region_embeddings source="check2hgi"), so --engine only swaps
    # sequences/labels and EVERY baseline gets identical reg (2026-06-23 bug). checkin feeds the
    # baseline's OWN per-visit embedding to the reg head -> substrate-sensitive. The Check2HGI reg
    # ceiling must be recomputed with --input-type checkin too for a matched Δ.
    cmd = [PY, "scripts/p1_region_head_ablation.py", "--engine", engine, "--state", state,
           "--seed", "0", "--only-fold", str(fold), "--heads", "next_stan_flow",
           "--input-type", "checkin", "--epochs", "50",
           "--per-fold-transition-dir", str(OUT / engine / state), "--tag", tag, "--no-resume"]
    subprocess.run(cmd, env=env, cwd=str(REPO), check=True)
    # p1 names the json by input_type; we run --input-type checkin (not region) → read THAT file
    # (reading the "region" name would silently pick up a stale region-modality run with the same tag).
    j = REPO / "docs/results/P1" / f"region_head_{state}_checkin_1f_50ep_{tag}.json"
    d = json.loads(j.read_text())
    pf = d["heads"]["next_stan_flow"]["per_fold"][0]
    return {"top10_acc": float(pf["top10_acc"]) * 100.0, "mrr": float(pf.get("mrr", 0)) * 100.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--baseline", required=True, choices=list(ENGINE))
    ap.add_argument("--cells-root", required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--only-fold", type=int, default=None,
                    help="run a single fold (for parallel per-fold runs w/ isolated OUTPUT_DIR); "
                         "writes <state>_<baseline>_f{fold}.json instead of the aggregate")
    ap.add_argument("--heads", nargs="+", default=["cat", "reg"], choices=["cat", "reg"])
    a = ap.parse_args()

    engine, _, per_fold = ENGINE[a.baseline]
    cells_root = Path(a.cells_root)
    outdir = REPO / "docs/results/closing_data/baseline_compare"
    outdir.mkdir(parents=True, exist_ok=True)
    results = {"state": a.state, "baseline": a.baseline, "engine": engine, "per_fold": []}

    if not per_fold:  # b2c: stage + build inputs ONCE
        stage(a.baseline, a.state, cell_emb(cells_root, a.baseline, a.state, 0))
        build_inputs(a.baseline, a.state)
        stage_logt(a.baseline, a.state)

    _folds = [a.only_fold] if a.only_fold is not None else list(range(a.folds))
    for f in _folds:
        log(f"=== {a.baseline}/{a.state} fold {f} ===")
        if per_fold:  # restage the leak-safe per-fold cell + rebuild inputs
            stage(a.baseline, a.state, cell_emb(cells_root, a.baseline, a.state, f))
            build_inputs(a.baseline, a.state)
            stage_logt(a.baseline, a.state)
        rec = {"fold": f}
        if "cat" in a.heads:
            rec.update(run_cat(engine, a.state, f)); log(f"  cat macro-F1={rec['macro_f1']:.2f}")
        if "reg" in a.heads:
            rec.update(run_reg(engine, a.state, f)); log(f"  reg Acc@10={rec['top10_acc']:.2f}")
        results["per_fold"].append(rec)

    import statistics as st
    for key in ("macro_f1", "top10_acc", "mrr"):
        vals = [r[key] for r in results["per_fold"] if key in r]
        if vals:
            results[f"{key}_mean"] = round(st.mean(vals), 3)
            results[f"{key}_std"] = round(st.stdev(vals), 3) if len(vals) > 1 else 0.0
    _suffix = f"_f{a.only_fold}" if a.only_fold is not None else ""
    out = outdir / f"{a.state}_{a.baseline}{_suffix}.json"
    out.write_text(json.dumps(results, indent=2))
    log(f"DONE -> {out}")
    log(f"  cat macro-F1={results.get('macro_f1_mean')} reg Acc@10={results.get('top10_acc_mean')}")


if __name__ == "__main__":
    main()
