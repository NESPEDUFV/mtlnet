"""Shared helpers for a study's state.json.

The active study directory is resolved from the ``STUDY_DIR`` environment
variable (absolute or repo-relative path).  If the variable is not set, it
defaults to ``docs/archive/fusion-study`` so existing workflows keep working on the
fusion branch without any change.

Atomic read/modify/write + small query helpers. No training logic here —
each script composes these primitives.
"""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]

_study_dir_env = os.environ.get("STUDY_DIR", "")
if _study_dir_env:
    STUDIES_DIR = Path(_study_dir_env)
    if not STUDIES_DIR.is_absolute():
        STUDIES_DIR = REPO_ROOT / STUDIES_DIR
else:
    STUDIES_DIR = REPO_ROOT / "docs" / "studies" / "fusion"

STATE_PATH = STUDIES_DIR / "state.json"
RESULTS_DIR = STUDIES_DIR / "results"

STUDY_VERSION = "1.0"
PHASES = ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict[str, Any]:
    now = utcnow()
    return {
        "study_version": STUDY_VERSION,
        "study_started": now,
        "last_update": now,
        "current_phase": "P0",
        "open_issues": [],
        "phases": {
            phase: {
                "status": "running" if phase == "P0" else "planned",
                "started": now if phase == "P0" else None,
                "finished": None,
                "tests": {},
            }
            for phase in PHASES
        },
    }


def read_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"{STATE_PATH} does not exist. Run `python scripts/study/launch_test.py --init` "
            "or `/study init` first."
        )
    with STATE_PATH.open("r") as fh:
        return json.load(fh)


def write_state(state: dict[str, Any]) -> None:
    state["last_update"] = utcnow()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix=".state.", suffix=".json", dir=str(STATE_PATH.parent)
    )
    try:
        with os.fdopen(tmp_fd, "w") as fh:
            json.dump(state, fh, indent=2, sort_keys=False)
            fh.write("\n")
        os.replace(tmp_path, STATE_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


@contextmanager
def mutate_state() -> Iterator[dict[str, Any]]:
    """Read, yield for mutation, then write atomically."""
    state = read_state()
    yield state
    write_state(state)


def ensure_initialized(force: bool = False) -> Path:
    if STATE_PATH.exists() and not force:
        return STATE_PATH
    write_state(empty_state())
    return STATE_PATH


def get_test(state: dict[str, Any], phase: str, test_id: str) -> dict[str, Any] | None:
    return state.get("phases", {}).get(phase, {}).get("tests", {}).get(test_id)


def set_test(state: dict[str, Any], phase: str, test_id: str, entry: dict[str, Any]) -> None:
    state["phases"].setdefault(phase, {"status": "planned", "tests": {}})
    state["phases"][phase].setdefault("tests", {})
    state["phases"][phase]["tests"][test_id] = entry


def iter_tests(state: dict[str, Any], phase: str | None = None) -> Iterator[tuple[str, str, dict[str, Any]]]:
    phases = [phase] if phase else PHASES
    for ph in phases:
        tests = state.get("phases", {}).get(ph, {}).get("tests", {})
        for tid, entry in tests.items():
            yield ph, tid, entry


# Tier-to-minutes constants (also used by enroll_p1.py / launch_test.py).
# Per-test config.compute_weight_min overrides these.
TIER_MINUTES: dict[str, int] = {
    "screen": 3,
    "promote": 6,
    "confirm": 30,
    "heavy": 120,
}


# Map US state abbreviations to full lowercase names as stored in config
_STATE_ABBREV: dict[str, str] = {
    "AL": "alabama",
    "AZ": "arizona",
    "FL": "florida",
    "CA": "california",
    "NY": "new_york",
}


def _normalize_state(s: str) -> str:
    """Normalize a state identifier to lowercase full name.

    Accepts abbreviations (AL → alabama) or full names (alabama → alabama).
    """
    upper = s.upper()
    if upper in _STATE_ABBREV:
        return _STATE_ABBREV[upper]
    return s.lower()


def _matches_filters(
    entry: dict[str, Any],
    *,
    filter_states: list[str] | None = None,
    filter_tiers: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
    max_runtime_min: int | None = None,
) -> bool:
    """Return True if the planned-test entry passes all active filters."""
    config = entry.get("config") or {}
    if filter_states:
        state_val = _normalize_state(config.get("state") or "")
        normalized_filter = [_normalize_state(s) for s in filter_states]
        if state_val not in normalized_filter:
            return False
    if filter_tiers:
        tier_val = config.get("tier") or "screen"
        if tier_val not in filter_tiers:
            return False
    if filter_archs:
        arch_val = config.get("arch") or config.get("model_name") or ""
        if arch_val not in filter_archs:
            return False
    if filter_optims:
        optim_val = config.get("optim") or config.get("mtl_loss") or ""
        if optim_val not in filter_optims:
            return False
    if max_runtime_min is not None:
        tier_val = config.get("tier") or "screen"
        weight_min = config.get("compute_weight_min") or TIER_MINUTES.get(tier_val, TIER_MINUTES["screen"])
        if weight_min > max_runtime_min:
            return False
    return True


def find_next_planned(
    state: dict[str, Any],
    phase: str | None = None,
    *,
    filter_states: list[str] | None = None,
    filter_tiers: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
    max_runtime_min: int | None = None,
) -> tuple[str, str, dict[str, Any]] | None:
    """Return the first planned test in the target phase matching all filters."""
    target = phase or state.get("current_phase")
    for ph, tid, entry in iter_tests(state, target):
        if entry.get("status") != "planned":
            continue
        if _matches_filters(
            entry,
            filter_states=filter_states,
            filter_tiers=filter_tiers,
            filter_archs=filter_archs,
            filter_optims=filter_optims,
            max_runtime_min=max_runtime_min,
        ):
            return ph, tid, entry
    return None


def find_all_planned(
    state: dict[str, Any],
    phase: str | None = None,
    *,
    filter_states: list[str] | None = None,
    filter_tiers: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
    max_runtime_min: int | None = None,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Return all planned tests matching filters (for dry-run display)."""
    target = phase or state.get("current_phase")
    results = []
    for ph, tid, entry in iter_tests(state, target):
        if entry.get("status") != "planned":
            continue
        if _matches_filters(
            entry,
            filter_states=filter_states,
            filter_tiers=filter_tiers,
            filter_archs=filter_archs,
            filter_optims=filter_optims,
            max_runtime_min=max_runtime_min,
        ):
            results.append((ph, tid, entry))
    return results


def open_issue(
    state: dict[str, Any],
    *,
    test_id: str,
    issue_type: str,
    description: str,
) -> str:
    issues = state.setdefault("open_issues", [])
    issue_id = f"ISS-{len(issues) + 1:03d}"
    issues.append(
        {
            "issue_id": issue_id,
            "test_id": test_id,
            "type": issue_type,
            "raised_at": utcnow(),
            "description": description,
            "status": "open",
            "resolution": None,
        }
    )
    return issue_id


def summarize_phase(state: dict[str, Any], phase: str) -> dict[str, Any]:
    tests = state.get("phases", {}).get(phase, {}).get("tests", {})
    counts: dict[str, int] = {}
    for entry in tests.values():
        status = entry.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return {
        "phase": phase,
        "status": state.get("phases", {}).get(phase, {}).get("status"),
        "total_tests": len(tests),
        "by_status": counts,
    }
