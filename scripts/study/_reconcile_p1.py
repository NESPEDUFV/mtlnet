"""One-off: reconcile P1 screen run_dirs on disk back into state.json.

Scans `results/fusion/{alabama,arizona}/mtlnet_*/`, parses each run's arch.txt
+ model_params.json to derive (state, arch_id, loss_id), maps to the expected
test_id `P1_<STATE>_screen_<arch>_<loss>_seed42`, and calls archive_result.py
+ analyze_test.py for each match. Retries (same test_id, multiple run_dirs)
are resolved by keeping the newest timestamp.

Usage:
    python scripts/study/_reconcile_p1.py [--dry-run] [--state alabama|arizona]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STUDY = REPO_ROOT / "scripts" / "study" / "study.py"
PY = sys.executable

STATE_ABBREV = {"alabama": "AL", "arizona": "AZ"}

# MTL loss class → canonical id (from _LOSS_REGISTRY)
LOSS_CLASS_TO_ID = {
    "AlignedMTLLoss": "aligned_mtl",
    "BayesAggMTLLoss": "bayesagg_mtl",
    "CAGradLoss": "cagrad",
    "DBMTLLoss": "db_mtl",
    "DWALoss": "dwa",
    "EqualWeightLoss": "equal_weight",
    "ExcessMTLLoss": "excess_mtl",
    "FairGradLoss": "fairgrad",
    "FAMOLoss": "famo",
    "GradNormLoss": "gradnorm",
    "NashMTL": "nash_mtl",
    "PCGrad": "pcgrad",
    "StaticWeightLoss": "static_weight",
    "STCHLoss": "stch",
    "UncertaintyWeightingLoss": "uncertainty_weighting",
}

# Arch class (+ expert count) → canonical arch id
# Ambiguity resolution uses category_experts count: cgc21=1, cgc22=2.


def _parse_arch(run_dir: Path) -> str | None:
    arch_path = run_dir / "model" / "arch.txt"
    if not arch_path.exists():
        return None
    text = arch_path.read_text()
    first = text.splitlines()[0] if text else ""
    if first.startswith("MTLnetDSelectK"):
        return "dsk42"
    if first.startswith("MTLnetMMoE"):
        return "mmoe4"
    if first.startswith("MTLnetCGC"):
        # Distinguish cgc21 vs cgc22 by category_experts count.
        pattern = r'\(category_experts\): ModuleList\((.*?)(?=\n {4,6}\)(?=\n))'
        m = re.search(pattern, text, re.DOTALL)
        if not m:
            return "cgc_unknown"
        block = m.group(1)
        single = len(re.findall(r'^      \(\d+\): Sequential', block, re.M))
        ranges = re.findall(r'^      \((\d+-\d+)\): (\d+) x Sequential', block, re.M)
        total = single + sum(int(r[1]) for r in ranges)
        if total == 1:
            return "cgc21"
        if total == 2:
            return "cgc22"
        return "cgc_unknown"
    if first.startswith("MTLnet("):
        return "base"
    return None


def _parse_loss(run_dir: Path) -> str | None:
    mp_path = run_dir / "model" / "model_params.json"
    if not mp_path.exists():
        return None
    try:
        d = json.loads(mp_path.read_text())
    except json.JSONDecodeError:
        return None
    loss_cls = d.get("hyperparameters", {}).get("criterion", {}).get("mtl")
    return LOSS_CLASS_TO_ID.get(loss_cls)


def _run_timestamp(run_dir: Path) -> str:
    # run_dir name format: mtlnet_lr1.0e-04_bs4096_ep10_YYYYMMDD_HHMMSS
    m = re.search(r'_(\d{8}_\d{6})$', run_dir.name)
    return m.group(1) if m else "00000000_000000"


def _has_summary(run_dir: Path) -> bool:
    return (run_dir / "summary" / "full_summary.json").exists()


def collect(state_filter: str | None = None) -> dict[str, Path]:
    """test_id → best matching run_dir (newest timestamp, summary present)."""
    out: dict[str, tuple[str, Path]] = {}  # test_id → (timestamp, run_dir)
    states = ["alabama", "arizona"] if state_filter is None else [state_filter]

    for state in states:
        root = REPO_ROOT / "results" / "fusion" / state
        if not root.exists():
            continue
        for run_dir in sorted(root.glob("mtlnet_*")):
            if not run_dir.is_dir() or not _has_summary(run_dir):
                continue
            arch = _parse_arch(run_dir)
            loss = _parse_loss(run_dir)
            if not arch or not loss:
                continue
            test_id = f"P1_{STATE_ABBREV[state]}_screen_{arch}_{loss}_seed42"
            ts = _run_timestamp(run_dir)
            if test_id in out:
                if ts > out[test_id][0]:
                    out[test_id] = (ts, run_dir)
            else:
                out[test_id] = (ts, run_dir)
    return {tid: rd for tid, (_, rd) in out.items()}


def load_planned_p1() -> dict[str, dict]:
    state_path = REPO_ROOT / "docs" / "studies" / "fusion" / "state.json"
    d = json.loads(state_path.read_text())
    return d["phases"]["P1"]["tests"]


def archive_and_analyze(test_id: str, run_dir: Path, claim_ids: list[str]) -> tuple[bool, str]:
    args = [PY, str(STUDY), "import", "--run-dir", str(run_dir.relative_to(REPO_ROOT)),
            "--phase", "P1", "--test-id", test_id, "--overwrite"]
    if claim_ids:
        args += ["--claims"] + claim_ids
    r = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return False, f"import failed: {r.stderr.strip()[:200]}"
    r2 = subprocess.run(
        [PY, str(STUDY), "analyze", "--phase", "P1", "--test-id", test_id],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if r2.returncode != 0:
        return False, f"analyze failed: {r2.stderr.strip()[:200]}"
    return True, r2.stdout.strip().splitlines()[-1] if r2.stdout else "ok"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--state", choices=["alabama", "arizona"], default=None)
    args = p.parse_args()

    planned = load_planned_p1()
    print(f"Planned P1 tests in state.json: {len(planned)}")

    mapping = collect(args.state)
    print(f"Found {len(mapping)} run_dirs with summary + identifiable config")

    matched = {tid: rd for tid, rd in mapping.items() if tid in planned}
    orphans = {tid: rd for tid, rd in mapping.items() if tid not in planned}
    missing = [tid for tid in planned if tid not in matched]

    print(f"\nMatched to planned: {len(matched)}")
    print(f"Orphans (run_dir not enrolled): {len(orphans)}")
    print(f"Planned still missing: {len(missing)}")

    if orphans:
        print("\nOrphan examples (first 5):")
        for tid in list(orphans)[:5]:
            print(f"  {tid}  ←  {orphans[tid].name}")

    if missing:
        print("\nMissing examples (first 5):")
        for tid in missing[:5]:
            print(f"  {tid}")

    if args.dry_run:
        print("\n[dry-run] no changes applied.")
        return 0

    print(f"\nArchiving + analyzing {len(matched)} tests...")
    ok = 0
    fail = 0
    for tid, run_dir in matched.items():
        claims = planned[tid].get("claim_ids", [])
        success, msg = archive_and_analyze(tid, run_dir, claims)
        if success:
            ok += 1
        else:
            fail += 1
            print(f"  [FAIL] {tid}: {msg}")
        if (ok + fail) % 20 == 0:
            print(f"  ...{ok + fail}/{len(matched)}")

    print(f"\nDone: {ok} archived+analyzed, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
