"""Analyze a completed/archived test against its expected ranges.

Reads $STUDY_DIR/state.json, fetches the test's `observed` + `expected`
blocks, assigns a verdict, and (for out-of-range results) opens an issue.

Verdicts:
  matches_hypothesis  — observed.joint_f1 inside expected.joint_range
  partial_match       — within 1 tolerance-window outside the range
  surprising          — outside and not within tolerance
  refutes             — expected a positive effect but observed negative
  unreliable          — missing data / NaN
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _state import RESULTS_DIR, mutate_state, open_issue, set_test, utcnow

DEFAULT_TOLERANCE = 0.03  # ±3 p.p. for "partial_match" band


def _check_range(value: float | None, rng: list[float] | None, tolerance: float) -> str:
    if value is None:
        return "unreliable"
    if rng is None:
        return "unscored"
    lo, hi = float(rng[0]), float(rng[1])
    if lo <= value <= hi:
        return "matches_hypothesis"
    if (lo - tolerance) <= value <= (hi + tolerance):
        return "partial_match"
    return "surprising"


def verdict_for(observed: dict[str, Any], expected: dict[str, Any], tolerance: float) -> dict[str, Any]:
    joint_verdict = _check_range(observed.get("joint_f1"), expected.get("joint_range"), tolerance)
    cat_verdict = _check_range(observed.get("cat_f1"), expected.get("cat_f1_range"), tolerance)
    next_verdict = _check_range(observed.get("next_f1"), expected.get("next_f1_range"), tolerance)

    severity = {"matches_hypothesis": 0, "partial_match": 1, "surprising": 2, "unreliable": 3, "unscored": -1}
    verdicts = [joint_verdict, cat_verdict, next_verdict]
    worst = max(verdicts, key=lambda v: severity.get(v, -1))

    return {
        "verdict": worst,
        "detail": {
            "joint": joint_verdict,
            "category": cat_verdict,
            "next": next_verdict,
        },
        "tolerance": tolerance,
    }


def analyze(phase: str, test_id: str, tolerance: float) -> int:
    with mutate_state() as state:
        entry = state.get("phases", {}).get(phase, {}).get("tests", {}).get(test_id)
        if entry is None:
            print(f"[analyze] no test {test_id} in phase {phase}", file=sys.stderr)
            return 2

        observed = entry.get("observed") or {}
        if not observed:
            archive_meta = RESULTS_DIR / phase / test_id / "metadata.json"
            if archive_meta.exists():
                with archive_meta.open() as fh:
                    observed = json.load(fh).get("observed", {})
                entry["observed"] = observed
        expected = entry.get("expected") or {}

        result = verdict_for(observed, expected, tolerance)
        entry["verdict"] = result["verdict"]
        entry["verdict_detail"] = result["detail"]
        entry["analyzed_at"] = utcnow()

        if result["verdict"] == "surprising":
            entry["status"] = "surprising"
            issue_id = open_issue(
                state,
                test_id=test_id,
                issue_type="surprising",
                description=(
                    f"{test_id}: verdict={result['detail']}; "
                    f"observed={observed}; expected={expected}"
                ),
            )
            entry.setdefault("notes", "")
            entry["notes"] = (entry["notes"] + f"\nopened {issue_id}").strip()
        elif result["verdict"] == "unreliable":
            entry["status"] = "corrupt"
            open_issue(
                state,
                test_id=test_id,
                issue_type="corrupt",
                description=f"{test_id}: observed metrics missing or NaN",
            )
        else:
            # preserve `archived` status if already there, otherwise mark analyzed
            if entry.get("status") not in {"archived"}:
                entry["status"] = "analyzed"

        set_test(state, phase, test_id, entry)

    print(f"[analyze] {test_id}: verdict={result['verdict']} detail={result['detail']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a test vs expected.")
    parser.add_argument("--phase", required=True)
    parser.add_argument("--test-id", required=True)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                        help="Slack allowed outside expected range for partial_match (default: 0.03)")
    args = parser.parse_args()
    return analyze(args.phase, args.test_id, args.tolerance)


if __name__ == "__main__":
    sys.exit(main())
