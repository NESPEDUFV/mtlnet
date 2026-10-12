#!/usr/bin/env python3
"""Region persistence on the Markov-floor windows: what share of windows have target == last region.

WHY THIS EXISTS
---------------
5_mobiwac.tex's Markov-floor paragraph explains why a first-order region transition table reads a
strong signal on our windows. That explanation needs the share of windows whose target region equals
the last visited region -- a property of the label sequence.

Two nearby quantities have both been mistaken for it, and both errors shipped:
  * 22.4 percent, a PLACE-level "target reappears in its own 9-history" rate on NON-OVERLAPPING
    windows (PIPELINE_AUDIT_2026-06-03.md:24). Wrong level and wrong windowing.
  * 0.32064, markov_1step_region acc1_mean from markov_floor_stride1/<state>.json. That is the top-1
    ACCURACY of a fitted transition table against held-out targets, not a share of windows. It lands
    close to the persistence share, which is exactly what makes the substitution easy to miss.

A persistence measurement on output/check2hgi/<state>/input/next_region.parquet gives a third number
(31.26 percent at Alabama) because that file holds ~12.7k rows against this protocol's 96,326
windows: a different window base.

So the quantity is computed here, from the same check-in stream and the same windowing as the floor,
and the WINDOW COUNT IS GATED against the floor artifact's n_windows. If that gate fails the
reconstruction is wrong and the script says so rather than emitting a number.

Usage:  python scripts/embedding_eval/region_persistence.py [state ...]
Output: docs/results/closing_data/markov_floor_stride1/region_persistence_<state>.json
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
FLOOR_DIR = REPO / "docs/results/closing_data/markov_floor_stride1"

WINDOW_SIZE = 9
STRIDE = 1
MIN_SEQUENCE_LENGTH = 10
EMIT_TAIL = False


def load_stream(state: str) -> pd.DataFrame:
    """Check-ins with a region column, from the same graph file the floor was computed on."""
    path = REPO / "output/check2hgi" / state / "temp/checkin_graph.pt"
    with open(path, "rb") as handle:          # torch.load rejects this file; it is a pickle
        graph = pickle.load(handle)
    frame = graph["metadata"].copy()
    poi_of_checkin = np.asarray(graph["checkin_to_poi"])
    region_of_poi = np.asarray(graph["poi_to_region"])
    if len(poi_of_checkin) != len(frame):
        raise SystemExit(f"{state}: checkin_to_poi has {len(poi_of_checkin)} rows, "
                         f"metadata has {len(frame)}")
    frame["region"] = region_of_poi[poi_of_checkin]
    return frame.sort_values(["userid", "datetime"], kind="mergesort").reset_index(drop=True)


def persistence(frame: pd.DataFrame) -> tuple[int, int]:
    """(windows, windows whose target region equals the window's last region)."""
    windows = hits = 0
    for _, group in frame.groupby("userid", sort=False):
        regions = group["region"].to_numpy()
        if len(regions) < MIN_SEQUENCE_LENGTH:
            continue
        last_start = len(regions) - WINDOW_SIZE - (0 if not EMIT_TAIL else -1)
        for start in range(0, last_start, STRIDE):
            windows += 1
            if regions[start + WINDOW_SIZE - 1] == regions[start + WINDOW_SIZE]:
                hits += 1
    return windows, hits


def main(states: list[str]) -> int:
    rc = 0
    for state in states:
        floor_path = FLOOR_DIR / f"{state}.json"
        if not floor_path.exists():
            print(f"{state}: no floor artifact at {floor_path}, skipping")
            rc = 1
            continue
        floor = json.loads(floor_path.read_text())
        expected = floor["n_windows"]

        frame = load_stream(state)
        windows, hits = persistence(frame)
        gate = windows == expected
        share = hits / windows if windows else float("nan")

        print(f"{state}: windows {windows:,} (floor artifact {expected:,}) "
              f"gate {'PASS' if gate else 'FAIL'} | target==last {hits:,} | {100*share:.2f}%")
        if not gate:
            print(f"  {state}: WINDOW COUNT GATE FAILED — the windowing does not match the floor, "
                  f"so this share is not comparable to it. No file written.")
            rc = 1
            continue

        out = {
            "what": "share of windows whose target region equals the region of the window's last visit",
            "state": state,
            "n_windows": windows,
            "n_windows_expected_from_floor_artifact": expected,
            "window_count_gate_pass": gate,
            "target_equals_last_region": hits,
            "region_persistence_share": round(share, 6),
            "region_persistence_pct": round(100 * share, 2),
            "protocol": {
                "source_stream": f"output/check2hgi/{state}/temp/checkin_graph.pt -> metadata",
                "region_map": "checkin_to_poi -> poi_to_region from the same file",
                "ordering": "sorted by (userid, datetime), stable",
                "window_size": WINDOW_SIZE, "stride": STRIDE,
                "min_sequence_length": MIN_SEQUENCE_LENGTH, "emit_tail": EMIT_TAIL,
            },
            "not_to_be_confused_with": {
                "markov_1step_region_acc1_mean": floor["aggregate"]["markov_1step_region"]["acc1_mean"],
                "explanation": "top-1 accuracy of a fitted first-order transition table, not a share "
                               "of windows; numerically close, which is why the two were once swapped",
            },
        }
        (FLOOR_DIR / f"region_persistence_{state}.json").write_text(json.dumps(out, indent=1))
    return rc


if __name__ == "__main__":
    args = sys.argv[1:] or ["alabama"]
    sys.exit(main(args))
