"""Finalize Phase 3 Scope D — leakage-free reg STL + MTL CH18 across all states.

Extracts per-fold metrics from run dirs (using TAG suffix _pf), writes per-fold
JSONs with `_pf` suffix to preserve the legacy leaky data, runs paired tests,
prints cross-state status board for both reg-STL and MTL.

Acceptance criteria:
  - CH16 reg-component: not directly tested (cat F1 only) — leakage-free reg
    STL data tightens absolute Acc@10 numbers.
  - CH15 reframing leakage-free: substrate-equivalence on reg under matched MTL
    head, TOST δ=2pp non-inferior at all 5 states.
  - CH18 leakage-free: MTL+C2HGI > MTL+HGI on cat F1 + reg Acc@10 per state,
    Wilcoxon p<0.05.

Usage:
    python3 scripts/finalize_phase3.py
    STATES="alabama arizona" python3 scripts/finalize_phase3.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "results"
DOCS_RES = REPO / "docs" / "studies" / "check2hgi" / "results"
PERFOLD = DOCS_RES / "phase1_perfold"
P1 = DOCS_RES / "P1"
PAIRED = DOCS_RES / "paired_tests"
PERFOLD.mkdir(parents=True, exist_ok=True)
PAIRED.mkdir(parents=True, exist_ok=True)


STATE_CODE = {"alabama": "AL", "arizona": "AZ", "florida": "FL",
              "california": "CA", "texas": "TX"}


def _latest_run_dir(engine: str, state: str, prefix: str) -> Path | None:
    """Find the latest <results>/<engine>/<state>/<prefix>_* run dir."""
    base = RESULTS / engine / state
    if not base.exists():
        return None
    candidates = sorted(base.glob(f"{prefix}_*"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


# ───────────────────────────────────────────────────────────────────────
# Reg STL extraction (output of p1_region_head_ablation.py)
# ───────────────────────────────────────────────────────────────────────

def extract_reg_stl_pf(state: str, engine: str) -> Path | None:
    """Read the Phase 3 reg-STL P1 JSON and write per-fold."""
    upstate = state.upper()
    tag = f"STL_{upstate}_{engine}_reg_gethard_pf_5f50ep"
    p1_path = P1 / f"region_head_{state}_region_5f_50ep_{tag}.json"
    if not p1_path.exists():
        print(f"  [reg_stl] missing {p1_path.name}")
        return None
    d = json.load(p1_path.open())
    pf = d["heads"]["next_getnext_hard"]["per_fold"]
    out = {}
    for i, f in enumerate(pf):
        out[f"fold_{i}"] = {
            "f1": f.get("f1"),
            "acc1": f.get("accuracy"),
            "acc5": f.get("top5_acc"),
            "acc10": f.get("top10_acc"),
            "mrr": f.get("mrr"),
        }
    code = STATE_CODE.get(state, state[:2].upper())
    dest = PERFOLD / f"{code}_{engine}_reg_gethard_pf_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"  [reg_stl] {state}/{engine} → {dest.name}")
    return dest


# ───────────────────────────────────────────────────────────────────────
# MTL extraction (output of train.py --task mtl)
# ───────────────────────────────────────────────────────────────────────

def extract_mtl_pf(state: str, engine: str) -> dict | None:
    """Extract MTL per-fold cat + reg from latest mtlnet_* run dir."""
    rd = _latest_run_dir(engine, state, "mtlnet")
    if not rd:
        print(f"  [mtl] no run dir for {engine}/{state}")
        return None
    cat_out, reg_out = {}, {}
    folds_dir = rd / "folds"
    for fold_idx in range(5):
        fp = folds_dir / f"fold{fold_idx + 1}_info.json"
        if not fp.exists():
            print(f"  [mtl] missing {fp}")
            return None
        be = json.load(fp.open())["diagnostic_best_epochs"]
        cat_m = be["next_category"]["metrics"]
        reg_m = be["next_region"]["metrics"]
        cat_out[f"fold_{fold_idx}"] = {
            "f1": cat_m["f1"],
            "accuracy": cat_m["accuracy"],
        }
        reg_out[f"fold_{fold_idx}"] = {
            "f1": reg_m.get("f1"),
            "acc1": reg_m.get("top1_acc"),
            "acc5": reg_m.get("top5_acc"),
            "acc10": reg_m.get("top10_acc_indist", reg_m.get("top10_acc")),
            "mrr": reg_m.get("mrr_indist", reg_m.get("mrr")),
        }
    code = STATE_CODE.get(state, state[:2].upper())
    cat_path = PERFOLD / f"{code}_{engine}_mtl_cat_pf.json"
    reg_path = PERFOLD / f"{code}_{engine}_mtl_reg_pf.json"
    cat_path.write_text(json.dumps(cat_out, indent=2))
    reg_path.write_text(json.dumps(reg_out, indent=2))
    print(f"  [mtl] {state}/{engine} → {cat_path.name}, {reg_path.name} (run={rd.name})")
    return {"cat": cat_path, "reg": reg_path, "run_dir": rd}


# ───────────────────────────────────────────────────────────────────────
# Paired tests
# ───────────────────────────────────────────────────────────────────────

def run_paired(c2_path: Path, hgi_path: Path, metric: str, task: str,
               state: str, tost: float | None = None,
               out_suffix: str = "_pf") -> Path:
    """Run paired test; outputs to paired_tests/<state>_<task>_<metric>_pf.json.

    ``task`` here is the *output label* (e.g. ``mtl_cat``, ``reg``); the
    underlying ``substrate_paired_test.py`` only accepts the bare
    ``{cat,reg}`` choices, so we strip a leading ``mtl_`` prefix before
    passing it on the CLI.

    We route the script's output through a per-call temp dir so the bare
    ``<state>_<cli_task>_<metric>.json`` filename never collides with
    Phase 2 leaky paired-test JSONs of the same shape that already live
    in ``paired_tests/`` (those are git-tracked historical references
    and MUST NOT be overwritten — see Phase 3 closure 2026-04-30).
    """
    import tempfile, shutil
    cli_task = task[4:] if task.startswith("mtl_") else task
    out_dir = PAIRED
    out_dir.mkdir(parents=True, exist_ok=True)
    final_path = out_dir / f"{state}_{task}_{metric}{out_suffix}.json"

    with tempfile.TemporaryDirectory(prefix=f"phase3_paired_{state}_{task}_{metric}_") as td:
        td_path = Path(td)
        cmd = [
            sys.executable, str(REPO / "scripts/analysis/substrate_paired_test.py"),
            "--check2hgi", str(c2_path),
            "--hgi", str(hgi_path),
            "--metric", metric,
            "--task", cli_task,
            "--state", state,
            "--out-dir", str(td_path),
        ]
        if tost is not None:
            cmd += ["--tost-margin", str(tost)]
        print(f"\n  [paired] state={state} task={task} metric={metric}")
        subprocess.run(cmd, check=True)
        produced = td_path / f"{state}_{cli_task}_{metric}.json"
        if not produced.exists():
            raise FileNotFoundError(
                f"substrate_paired_test.py did not produce {produced.name} "
                f"in {td_path}; check the script's --out-dir handling."
            )
        shutil.move(str(produced), str(final_path))
    return final_path


# ───────────────────────────────────────────────────────────────────────
# Status board
# ───────────────────────────────────────────────────────────────────────

def _load_per_fold(p: Path, key: str) -> np.ndarray | None:
    if not p.exists():
        return None
    d = json.load(p.open())
    return np.array([d[f"fold_{i}"][key] for i in range(5)])


def status_board(states: list[str]) -> None:
    print("\n" + "=" * 78)
    print("=== Cross-state STATUS BOARD (leakage-free, per-fold transitions) ===")
    print("=" * 78)

    print("\n--- Reg STL Acc@10 (CH15 reframing, leakage-free) ---")
    print(f"{'State':<5}  {'C2HGI':>14}  {'HGI':>14}  {'Δ':>7}  {'TOST non-inf':>14}")
    for state in states:
        code = STATE_CODE.get(state, state[:2].upper())
        c = PERFOLD / f"{code}_check2hgi_reg_gethard_pf_5f50ep.json"
        h = PERFOLD / f"{code}_hgi_reg_gethard_pf_5f50ep.json"
        cf = _load_per_fold(c, "acc10"); hf = _load_per_fold(h, "acc10")
        if cf is None or hf is None:
            print(f"{code:<5}  reg STL per-fold JSONs missing — skipping")
            continue
        pt = PAIRED / f"{state}_reg_acc10_pf.json"
        nti = "?"
        if pt.exists():
            nti = json.load(pt.open()).get("non_inferiority_tost", {}).get("non_inferior_at_alpha_0.05", "?")
            nti = "✓ non-inf" if nti is True else nti
        print(f"{code:<5}  {cf.mean()*100:>5.2f} ± {cf.std()*100:.2f}  {hf.mean()*100:>5.2f} ± {hf.std()*100:.2f}  {(cf-hf).mean()*100:+5.2f}  {nti:>14}")

    print("\n--- MTL B3 cat F1 (CH18 leakage-free) ---")
    print(f"{'State':<5}  {'C2HGI':>14}  {'HGI':>14}  {'Δ':>7}  {'Wilcoxon p':>10}")
    for state in states:
        code = STATE_CODE.get(state, state[:2].upper())
        c = PERFOLD / f"{code}_check2hgi_mtl_cat_pf.json"
        h = PERFOLD / f"{code}_hgi_mtl_cat_pf.json"
        cf = _load_per_fold(c, "f1"); hf = _load_per_fold(h, "f1")
        if cf is None or hf is None:
            print(f"{code:<5}  MTL cat per-fold JSONs missing — skipping")
            continue
        pt = PAIRED / f"{state}_mtl_cat_f1_pf.json"
        p = "?"
        if pt.exists():
            p = f"{json.load(pt.open())['superiority']['wilcoxon_p_greater']:.4f}"
        print(f"{code:<5}  {cf.mean()*100:>5.2f} ± {cf.std()*100:.2f}  {hf.mean()*100:>5.2f} ± {hf.std()*100:.2f}  {(cf-hf).mean()*100:+5.2f}  {p:>10}")

    print("\n--- MTL B3 reg Acc@10 (CH18 leakage-free) ---")
    print(f"{'State':<5}  {'C2HGI':>14}  {'HGI':>14}  {'Δ':>7}  {'Wilcoxon p':>10}")
    for state in states:
        code = STATE_CODE.get(state, state[:2].upper())
        c = PERFOLD / f"{code}_check2hgi_mtl_reg_pf.json"
        h = PERFOLD / f"{code}_hgi_mtl_reg_pf.json"
        cf = _load_per_fold(c, "acc10"); hf = _load_per_fold(h, "acc10")
        if cf is None or hf is None:
            print(f"{code:<5}  MTL reg per-fold JSONs missing — skipping")
            continue
        pt = PAIRED / f"{state}_mtl_reg_acc10_pf.json"
        p = "?"
        if pt.exists():
            p = f"{json.load(pt.open())['superiority']['wilcoxon_p_greater']:.4f}"
        print(f"{code:<5}  {cf.mean()*100:>5.2f} ± {cf.std()*100:.2f}  {hf.mean()*100:>5.2f} ± {hf.std()*100:.2f}  {(cf-hf).mean()*100:+5.2f}  {p:>10}")


# ───────────────────────────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────────────────────────

def main():
    states = os.environ.get("STATES", "alabama arizona florida california texas").split()
    print(f"=== Phase 3 Scope D finalization (states: {states}) ===\n")

    print("[1/4] Extracting reg STL per-fold...")
    for state in states:
        for engine in ("check2hgi", "hgi"):
            extract_reg_stl_pf(state, engine)

    print("\n[2/4] Extracting MTL per-fold...")
    extracted: dict = {}
    for state in states:
        for engine in ("check2hgi", "hgi"):
            r = extract_mtl_pf(state, engine)
            if r:
                extracted[(state, engine)] = r

    print("\n[3/4] Running paired tests...")
    for state in states:
        # reg STL
        code = STATE_CODE.get(state, state[:2].upper())
        c2_reg = PERFOLD / f"{code}_check2hgi_reg_gethard_pf_5f50ep.json"
        h_reg = PERFOLD / f"{code}_hgi_reg_gethard_pf_5f50ep.json"
        if c2_reg.exists() and h_reg.exists():
            run_paired(c2_reg, h_reg, "acc10", "reg", state, tost=0.02)
            run_paired(c2_reg, h_reg, "mrr",   "reg", state, tost=0.02)
        # MTL
        c2 = extracted.get((state, "check2hgi"))
        h = extracted.get((state, "hgi"))
        if c2 and h:
            run_paired(c2["cat"], h["cat"], "f1",    "mtl_cat", state)
            run_paired(c2["reg"], h["reg"], "acc10", "mtl_reg", state)
            run_paired(c2["reg"], h["reg"], "mrr",   "mtl_reg", state)

    print("\n[4/4] Status board:")
    status_board(states)

    print("\n=== Done ===")
    print("Artefacts:")
    print(f"  per-fold:    {PERFOLD}/*_pf*.json")
    print(f"  paired tests: {PAIRED}/*_pf.json")
    print("Update PHASE3_TRACKER.md + SUBSTRATE_COMPARISON_FINDINGS.md, then commit + push.")


if __name__ == "__main__":
    main()
