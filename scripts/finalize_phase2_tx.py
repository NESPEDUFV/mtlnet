"""Finalize Phase 2 TX after orchestrator run.

Extracts per-fold metrics from run dirs, writes TX_* per-fold JSONs in the
`phase1_perfold` directory, and runs the substrate paired tests for cat F1,
reg Acc@10, and reg MRR (TOST δ=2pp).

Usage::

    python3 scripts/finalize_phase2_tx.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "results"
PERFOLD = REPO / "docs" / "studies" / "check2hgi" / "results" / "phase1_perfold"
P1 = REPO / "docs" / "studies" / "check2hgi" / "results" / "P1"
PAIRED = REPO / "docs" / "studies" / "check2hgi" / "results" / "paired_tests"
PERFOLD.mkdir(parents=True, exist_ok=True)
PAIRED.mkdir(parents=True, exist_ok=True)


def _latest_run_dir(engine: str, state: str, prefix: str) -> Path | None:
    base = RESULTS / engine / state
    if not base.exists():
        return None
    candidates = sorted(base.glob(f"{prefix}_*"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def extract_cat_perfold(engine: str, state: str = "texas") -> Path | None:
    """Extract cat-task per-fold f1/accuracy from latest next_* run dir."""
    rd = _latest_run_dir(engine, state, "next")
    if not rd:
        print(f"  [extract_cat] no run dir for {engine}/{state}")
        return None
    out = {}
    folds_dir = rd / "folds"
    # Storage uses 1-indexed files (fold1_info.json..fold5_info.json) but
    # the per-fold JSON keys are 0-indexed (fold_0..fold_4) for compatibility
    # with the existing AL/AZ/FL/CA per-fold files in the repo.
    for fold_idx in range(5):
        fp = folds_dir / f"fold{fold_idx + 1}_info.json"
        if not fp.exists():
            print(f"  [extract_cat] missing {fp}")
            return None
        m = json.load(fp.open())["diagnostic_best_epochs"]["next"]["metrics"]
        out[f"fold_{fold_idx}"] = {"f1": m["f1"], "accuracy": m["accuracy"]}
    dest = PERFOLD / f"TX_{engine}_cat_gru_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"  [extract_cat] wrote {dest.name} (run_dir={rd.name})")
    return dest


def reg_p1_path(engine: str, state: str = "texas") -> Path | None:
    """Locate the reg-STL P1 JSON written by p1_region_head_ablation.py."""
    upstate = state.upper()
    tag = f"STL_{upstate}_{engine}_reg_gethard_5f50ep"
    candidates = list(P1.glob(f"region_head_{state}_region_5f_50ep_{tag}.json"))
    if candidates:
        return candidates[0]
    print(f"  [reg_p1_path] not found for {tag}")
    return None


def run_paired(check2hgi_path: Path, hgi_path: Path, metric: str, task: str,
               state: str = "texas", tost: float | None = None) -> None:
    cmd = [
        sys.executable, str(REPO / "scripts/analysis/substrate_paired_test.py"),
        "--check2hgi", str(check2hgi_path),
        "--hgi", str(hgi_path),
        "--metric", metric,
        "--task", task,
        "--state", state,
        "--out-dir", str(PAIRED),
    ]
    if tost is not None:
        cmd += ["--tost-margin", str(tost)]
    print(f"\n  [paired] {' '.join(cmd[1:])}")
    subprocess.run(cmd, check=True)


def main():
    print("== TX Phase 2 finalization ==\n")
    print("[1/3] Extract cat per-fold...")
    cat_c2 = extract_cat_perfold("check2hgi")
    cat_hgi = extract_cat_perfold("hgi")

    print("\n[2/3] Locate reg P1 JSONs...")
    reg_c2 = reg_p1_path("check2hgi")
    reg_hgi = reg_p1_path("hgi")
    print(f"  c2hgi reg P1: {reg_c2}")
    print(f"  hgi   reg P1: {reg_hgi}")

    print("\n[3/3] Run paired tests...")
    if cat_c2 and cat_hgi:
        run_paired(cat_c2, cat_hgi, "f1", "cat")
    else:
        print("  [skip] cat paired — missing per-fold JSON")

    if reg_c2 and reg_hgi:
        run_paired(reg_c2, reg_hgi, "acc10", "reg", tost=0.02)
        run_paired(reg_c2, reg_hgi, "mrr", "reg", tost=0.02)
    else:
        print("  [skip] reg paired — missing P1 JSON")

    print("\n== Done ==")


if __name__ == "__main__":
    main()
