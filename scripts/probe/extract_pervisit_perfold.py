"""Extract per-fold cat F1 macro from pervisit-counterfactual run dirs.

After scripts/run_pervisit_counterfactual_FL_CA_TX.sh produces fresh result
dirs at results/{check2hgi,check2hgi_pooled,hgi}/<state>/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/,
this script extracts per-fold macro-F1 + accuracy from each run's
folds/foldN_info.json and writes the simplified phase1_perfold/ JSON format
that the §6.1 figure renderer consumes.

Output naming mirrors the AZ counterfactual JSONs (commit 61b44c3):
    docs/results/phase1_perfold/
        FL_check2hgi_cat_gru_5f50ep_<DATE>.json
        FL_check2hgi_pooled_cat_gru_5f50ep_<DATE>.json
        FL_hgi_cat_gru_5f50ep_<DATE>.json
        CA_*  TX_*  (and AZ_* / AL_* if --states includes them)

The JSON shape is:
    {
      "fold_0": {"f1": <macro-f1>, "accuracy": <acc>},
      "fold_1": {...}, ..., "fold_4": {...}
    }

Usage
-----
    python3 scripts/probe/extract_pervisit_perfold.py \\
        --states florida california texas \\
        [--engines check2hgi check2hgi_pooled hgi] \\
        [--out docs/results/phase1_perfold]

By default the script picks the *latest* run dir per (state, engine) tuple;
pass --run-id <TIMESTAMP> to pin to a specific timestamp.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

# Map full-state-name -> two-letter prefix used in phase1_perfold filenames.
STATE_PREFIX = {
    "alabama": "AL",
    "arizona": "AZ",
    "florida": "FL",
    "california": "CA",
    "texas": "TX",
}

DEFAULT_ENGINES = ("check2hgi", "check2hgi_pooled", "hgi")
DEFAULT_STATES = ("florida", "california", "texas")

RUNDIR_RE = re.compile(r"^next_lr1\.0e-04_bs1024_ep50_(\d{8}_\d{6})(?:_\d+)?$")


def find_latest_rundir(results_root: Path, engine: str, state: str,
                       run_id: str | None) -> Path:
    """Return the result directory for a given (engine, state).

    If run_id is provided, the matching dir must end with `_<run_id>`. Otherwise
    the most recent (lexicographically max timestamp) run is selected.
    """
    state_dir = results_root / engine / state
    if not state_dir.exists():
        raise FileNotFoundError(
            f"No results for engine={engine} state={state} at {state_dir}"
        )

    candidates = []
    for child in state_dir.iterdir():
        if not child.is_dir():
            continue
        m = RUNDIR_RE.match(child.name)
        if not m:
            continue
        if run_id and not child.name.endswith(f"_{run_id}"):
            continue
        candidates.append((m.group(1), child))

    if not candidates:
        suffix = f" matching run_id={run_id}" if run_id else ""
        raise FileNotFoundError(
            f"No matching run dirs for engine={engine} state={state}"
            f"{suffix} under {state_dir}"
        )

    candidates.sort(key=lambda t: t[0])
    return candidates[-1][1]


def extract_fold_metrics(rundir: Path) -> dict[str, dict[str, float]]:
    """Read folds/foldN_info.json and return {fold_N: {f1, accuracy}}."""
    folds_dir = rundir / "folds"
    if not folds_dir.exists():
        raise FileNotFoundError(f"folds/ directory missing in {rundir}")

    out: dict[str, dict[str, float]] = {}
    for info_path in sorted(folds_dir.glob("fold*_info.json")):
        m = re.match(r"fold(\d+)_info\.json$", info_path.name)
        if not m:
            continue
        fold_idx = int(m.group(1))
        with info_path.open() as fh:
            payload = json.load(fh)

        # Path matches AZ counterfactual extraction:
        #   diagnostic_best_epochs.next.metrics.f1 (macro-F1)
        #   diagnostic_best_epochs.next.metrics.accuracy
        try:
            metrics = (
                payload["diagnostic_best_epochs"]["next"]["metrics"]
            )
        except KeyError as e:
            raise KeyError(
                f"Could not find diagnostic_best_epochs.next.metrics in "
                f"{info_path}: missing key {e}"
            ) from e

        out[f"fold_{fold_idx}"] = {
            "f1": float(metrics["f1"]),
            "accuracy": float(metrics["accuracy"]),
        }

    if not out:
        raise RuntimeError(f"No fold*_info.json files found in {folds_dir}")
    return out


def write_perfold_json(out_dir: Path, state: str, engine: str,
                       payload: dict[str, dict[str, float]],
                       date_tag: str) -> Path:
    """Write the phase1_perfold/<STATE>_<engine>_cat_gru_5f50ep_<DATE>.json."""
    prefix = STATE_PREFIX[state]
    fname = f"{prefix}_{engine}_cat_gru_5f50ep_{date_tag}.json"
    out_path = out_dir / fname
    out_dir.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        json.dump(payload, fh, indent=2)
    return out_path


def main(states: Iterable[str], engines: Iterable[str], out_dir: Path,
         results_root: Path, run_id: str | None) -> None:
    date_tag = datetime.utcnow().strftime("%Y%m%d")
    for state in states:
        if state not in STATE_PREFIX:
            print(f"WARN: skipping unknown state '{state}' "
                  f"(known: {sorted(STATE_PREFIX)})")
            continue
        for engine in engines:
            try:
                rundir = find_latest_rundir(results_root, engine, state, run_id)
                payload = extract_fold_metrics(rundir)
                out_path = write_perfold_json(out_dir, state, engine,
                                              payload, date_tag)
                f1s = [v["f1"] for v in payload.values()]
                mean_f1 = sum(f1s) / len(f1s) * 100
                print(f"[ok] {state}/{engine}: mean macro-F1 = {mean_f1:.2f} "
                      f"({len(f1s)} folds) -> {out_path}")
            except (FileNotFoundError, KeyError, RuntimeError) as e:
                print(f"[skip] {state}/{engine}: {e}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--states", nargs="+", default=list(DEFAULT_STATES),
        help="States to extract (default: florida california texas).",
    )
    p.add_argument(
        "--engines", nargs="+", default=list(DEFAULT_ENGINES),
        help="Substrate engines to extract (default: all three counterfactual cells).",
    )
    p.add_argument(
        "--out", type=Path,
        default=Path("docs/results/phase1_perfold"),
        help="Destination directory for the simplified per-fold JSONs.",
    )
    p.add_argument(
        "--results-root", type=Path, default=Path("results"),
        help="Root directory containing results/<engine>/<state>/<rundir>/.",
    )
    p.add_argument(
        "--run-id", type=str, default=None,
        help="Pin to a specific YYYYMMDD_HHMMSS timestamp suffix; "
             "defaults to latest matching dir per (state, engine).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.states, args.engines, args.out, args.results_root, args.run_id)
