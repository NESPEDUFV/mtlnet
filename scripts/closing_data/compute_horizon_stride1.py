"""Prediction horizon under the BOARD stride-1 windowing, for all six datasets.

For every gated stride-1 window (window=9, stride=1, MIN_SEQUENCE_LENGTH=10,
emit_tail=False — the exact `check2hgi_dk_ovl` board protocol), the prediction
horizon is the time gap between the LAST visit inside the 9-visit window and
its TARGET visit:

    gap = timestamp(target) - timestamp(window[-1])   [same user, consecutive
                                                       check-ins by protocol]

This is a pure data property (no fold split): reported over ALL windows per
dataset as median / mean / P25 / P75 / P90 in HOURS (plus extra percentiles
and within-threshold shares for context).

Data loading + windowing machinery is REUSED from
scripts/closing_data/compute_markov_floor_stride1.py (imported as a module):
same check-in streams (frozen check2hgi graph metadata for AL/AZ/FL/CA/IST;
Texas rebuilt from raw + tract shapefile with the preprocess-replica POI
filter) and the same closed-form gated stride-1 windowing (target positions =
check-ins with >= 9 same-user predecessors), which that script verified
per-user against the canonical ``data.inputs.core.generate_sequences`` and
gated against the paper's Table 1 Windows column.

SANITY GATES: (a) window count within 1% of Table 1
(articles/[mobiwac]/src/tables/tbl1_datasets.tex), (b) window count EXACTLY
equal to the sibling Markov-floor JSON
(docs/results/closing_data/markov_floor_stride1/<state>.json) when present.

Usage::

    .venv/bin/python scripts/closing_data/compute_horizon_stride1.py --state alabama
    # default: all six, smallest first, one state fully processed + freed at a time

Outputs: docs/results/closing_data/horizon_stride1/<state>.json
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_here = Path(__file__).resolve().parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

# Reuse the protocol-matched loaders/constants (this import also puts src/ on
# sys.path for configs.paths etc.).
import compute_markov_floor_stride1 as mkv  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_root = mkv._root
WINDOW = mkv.WINDOW          # 9
STRIDE = mkv.STRIDE          # 1
MIN_SEQ = mkv.MIN_SEQ        # 10
EMIT_TAIL = mkv.EMIT_TAIL    # False

OUT_DIR = _root / "docs/results/closing_data/horizon_stride1"
MARKOV_DIR = mkv.OUT_DIR     # docs/results/closing_data/markov_floor_stride1

NS_PER_HOUR = 3.6e12


def _target_positions(uid: np.ndarray) -> np.ndarray:
    """Closed-form gated stride-1 target positions (== mkv.build_windows).

    On the (userid, datetime)-sorted stream, targets are exactly the check-ins
    with >= WINDOW same-user predecessors: a user with n check-ins contributes
    n - WINDOW windows if n >= MIN_SEQ (= WINDOW + 1), else none.
    """
    n = len(uid)
    idx = np.arange(n)
    new_user = np.empty(n, dtype=bool)
    new_user[0] = True
    new_user[1:] = uid[1:] != uid[:-1]
    seg_start = np.maximum.accumulate(np.where(new_user, idx, 0))
    pos_in_user = idx - seg_start
    return idx[pos_in_user >= WINDOW]


def compute_state(state: str) -> dict:
    t0 = time.time()
    if state == "texas":
        md, _pid2idx, _p2r, mapping_src, n_dropped_ck = mkv._load_stream_texas()
        stream_src = (f"{mkv.IoPaths.get_city('texas')} (raw; sorted (userid,datetime) "
                      f"mergesort; {n_dropped_ck} check-ins dropped at unmapped POIs; "
                      f"POI filter: {mapping_src})")
    elif state in mkv.GRAPH_STATES:
        md, _pid2idx, _p2r, _msrc, n_dropped_ck = mkv._load_stream_from_graph(state)
        stream_src = (f"{mkv.IoPaths.CHECK2HGI.get_graph_data_file(state)} "
                      f"graph['metadata'] (substrate stream)")
    else:
        raise ValueError(f"unknown state {state}")
    del _pid2idx, _p2r

    # Keep only what the horizon needs; free the rest ASAP (RAM care at CA/TX).
    uid = md["userid"].to_numpy()
    ts_col = md["datetime"]
    if not np.issubdtype(ts_col.dtype, np.datetime64):
        ts_col = pd.to_datetime(ts_col)
    ts = ts_col.to_numpy(dtype="datetime64[ns]")
    n_ck = len(md)
    n_users = int(md["userid"].nunique())
    del md, ts_col
    gc.collect()

    t_idx = _target_positions(uid)
    n_windows = int(len(t_idx))
    del uid
    gc.collect()

    # gap = timestamp(target) - timestamp(last window visit), in hours (float64)
    gap_ns = (ts[t_idx] - ts[t_idx - 1]).astype(np.int64)
    del ts, t_idx
    gc.collect()
    assert (gap_ns >= 0).all(), f"{state}: negative gap — stream not time-sorted?"
    gap_h = gap_ns.astype(np.float64) / NS_PER_HOUR
    del gap_ns
    gc.collect()

    q = np.percentile(gap_h, [10, 25, 50, 75, 90, 95, 99])
    stats_hours = {
        "median": float(q[2]),
        "mean": float(gap_h.mean()),
        "p10": float(q[0]),
        "p25": float(q[1]),
        "p75": float(q[3]),
        "p90": float(q[4]),
        "p95": float(q[5]),
        "p99": float(q[6]),
        "min": float(gap_h.min()),
        "max": float(gap_h.max()),
    }
    share_within = {
        "1h": float((gap_h <= 1.0).mean()),
        "6h": float((gap_h <= 6.0).mean()),
        "24h": float((gap_h <= 24.0).mean()),
        "48h": float((gap_h <= 48.0).mean()),
        "72h": float((gap_h <= 72.0).mean()),
        "168h": float((gap_h <= 168.0).mean()),
    }
    del gap_h
    gc.collect()

    # --- gates ---
    expected = mkv.TABLE1_WINDOWS[state]
    ratio = n_windows / expected
    gate_pass = abs(ratio - 1.0) <= 0.01
    logger.info("[%s] windows=%d  Table1=%d  ratio=%.6f  gate(<=1%%)=%s",
                state, n_windows, expected, ratio, "PASS" if gate_pass else "FAIL")
    if not gate_pass:
        raise SystemExit(
            f"{state}: SANITY GATE FAILED — windows {n_windows} vs Table 1 {expected} "
            f"({(ratio - 1) * 100:+.2f}%).")

    markov_gate = None
    mk_path = MARKOV_DIR / f"{state}.json"
    if mk_path.exists():
        mk_n = json.loads(mk_path.read_text())["n_windows"]
        markov_gate = {"markov_floor_json": str(mk_path.relative_to(_root)),
                       "markov_n_windows": int(mk_n),
                       "exact_match": bool(mk_n == n_windows)}
        if mk_n != n_windows:
            raise SystemExit(f"{state}: window count {n_windows} != Markov-floor "
                             f"script count {mk_n} — machinery drift.")
        logger.info("[%s] exact window-count match vs Markov-floor JSON (%d)", state, mk_n)

    logger.info("[%s] horizon hours: median=%.2f mean=%.2f P25=%.2f P75=%.2f P90=%.2f",
                state, stats_hours["median"], stats_hours["mean"],
                stats_hours["p25"], stats_hours["p75"], stats_hours["p90"])

    return {
        "state": state,
        "quantity": "prediction_horizon_hours",
        "definition": "timestamp(target) - timestamp(last of the 9 window visits), "
                      "per gated stride-1 window, over ALL windows (no fold split; "
                      "data property)",
        "windowing": {"window_size": WINDOW, "stride": STRIDE,
                      "min_sequence_length": MIN_SEQ, "emit_tail": EMIT_TAIL,
                      "note": "board check2hgi_dk_ovl protocol (gated stride-1 overlap)"},
        "source": {"checkin_stream": stream_src,
                   "checkins_dropped_unmapped_poi": int(n_dropped_ck),
                   "timestamp_column": "datetime",
                   "machinery": "loaders reused from scripts/closing_data/"
                                "compute_markov_floor_stride1.py"},
        "n_checkins": int(n_ck),
        "n_users": n_users,
        "n_windows": n_windows,
        "window_count_gate": {"computed": n_windows, "table1_expected": expected,
                              "ratio": ratio, "within_1pct": gate_pass,
                              "table1_source": "articles/[mobiwac]/src/tables/"
                                               "tbl1_datasets.tex"},
        "markov_floor_crosscheck": markov_gate,
        "horizon_hours": stats_hours,
        "share_gap_within": share_within,
        "script": "scripts/closing_data/compute_horizon_stride1.py",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime_sec": round(time.time() - t0, 1),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", action="append", default=None,
                        choices=list(mkv.TABLE1_WINDOWS.keys()))
    args = parser.parse_args()
    states = args.state or ["alabama", "arizona", "istanbul", "florida",
                            "california", "texas"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for state in states:
        logger.info("=" * 64)
        logger.info("Prediction horizon (stride-1 board windowing): %s", state)
        logger.info("=" * 64)
        result = compute_state(state)
        out_path = OUT_DIR / f"{state}.json"
        out_path.write_text(json.dumps(result, indent=2))
        logger.info("[%s] saved %s | median=%.2fh IQR=[%.2f, %.2f]h | %.1fs",
                    state, out_path, result["horizon_hours"]["median"],
                    result["horizon_hours"]["p25"], result["horizon_hours"]["p75"],
                    result["runtime_sec"])
        gc.collect()


if __name__ == "__main__":
    main()
