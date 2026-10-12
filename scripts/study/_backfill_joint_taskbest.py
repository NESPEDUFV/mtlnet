"""One-off: backfill `cat_f1_taskbest`, `next_f1_taskbest`, `joint_f1_taskbest`
into every archived test in state.json by re-parsing each test's
full_summary.json. No new training needed.

See docs/archive/fusion-study/issues/P1_METHODOLOGY_FLAWS.md F1 for context.

Usage:
    .venv/bin/python scripts/study/_backfill_joint_taskbest.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "study"))
from _state import read_state, write_state  # noqa: E402
from archive_result import _joint_score_taskbest  # noqa: E402


def backfill(dry_run: bool = False) -> int:
    state = read_state()
    phases = state.get("phases", {})
    touched = 0
    missing = 0
    already = 0
    for phase_id, phase in phases.items():
        tests = phase.get("tests", {}) or {}
        if not isinstance(tests, dict):
            continue
        for test_id, entry in tests.items():
            archive = entry.get("results_archive")
            if not archive:
                continue
            summary_path = ROOT / archive / "full_summary.json"
            if not summary_path.exists():
                missing += 1
                continue
            obs = entry.setdefault("observed", {})
            if "joint_f1_taskbest" in obs and not dry_run:
                already += 1
                continue
            summary = json.loads(summary_path.read_text())
            jt, ct, nt = _joint_score_taskbest(summary)
            if jt is None:
                missing += 1
                continue
            obs["cat_f1_taskbest"] = ct
            obs["next_f1_taskbest"] = nt
            obs["joint_f1_taskbest"] = jt
            touched += 1
    print(f"touched: {touched}, already had field: {already}, missing data: {missing}")
    if not dry_run and touched:
        write_state(state)
        print("state.json updated.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(backfill(dry_run=args.dry_run))
