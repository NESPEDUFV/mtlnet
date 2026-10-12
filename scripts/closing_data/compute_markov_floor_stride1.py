"""Protocol-matched Markov-1 REGION floor under the BOARD windowing (stride-1).

The paper's current region floor (docs/results/P0/simple_baselines/<state>/
next_region.json, baseline ``markov_1step_region``) was computed on the frozen
NON-overlapping substrate windows (stride-9, MIN_SEQ=5, emit_tail=True); the
paper discloses that windowing mismatch (06_results.tex "indicative rather than
protocol-matched"). This script recomputes the SAME first-order region-level
Markov floor under the paper's BOARD protocol windowing:

    window=9, stride=1, MIN_SEQUENCE_LENGTH=10, emit_tail=False (gated)

which is the exact `check2hgi_dk_ovl` board windowing (RESULTS_BOARD §1,
RUN_MATRIX §0, tbl1_overlap_stats.py). Under this gating every emitted window
has 9 REAL visits (no padding) and a genuine next visit as target, so the
windows of a user with n >= 10 check-ins are exactly the (n-9) positions with
>= 9 same-user predecessors. That closed form is used for the vectorised build
and is verified per user against the repo's canonical
``data.inputs.core.generate_sequences`` (same function the board builders call).

Fold protocol mirrors scripts/compute_simple_baselines.py EXACTLY (that script
is NOT modified): user-grouped StratifiedGroupKFold, SEED=42, N_SPLITS=5,
stratification key = next_category mapped through the inverse CATEGORIES_MAP,
groups = str(userid), train-fold-only transition counts, val-fold Acc@K/MRR,
mean +- std across the 5 folds. The baseline implementation replicates
``baseline_markov_kstep_region(k=1)`` semantics (Counter.most_common top-10
with train-insertion-order tie-break, global train top-10 fallback for unseen
last-regions) with a per-key top-k cache for speed (identical outputs).

Check-in stream + poi->region mapping sources (windowing-independent, so the
frozen v11 artifacts are protocol-neutral for the MAPPING):

  * alabama/arizona/florida/california/istanbul: the check2hgi graph pickle
    ``output/check2hgi/<state>/temp/checkin_graph.pt`` provides both the
    substrate check-in stream (graph['metadata']: userid, placeid, datetime,
    category — already (userid, datetime)-sorted and POI-vocabulary-filtered)
    and the maps (placeid_to_idx, poi_to_region). For the Gowalla states the
    substrate stream is row-identical to data/checkins/<State>.parquet (zero
    POIs fall outside the census tracts; validated AL 113,846 == raw). For
    Istanbul the metadata IS the mahalle substrate post null-coord drop
    (462,615 ck / 23,694 users / 29,816 POIs / 520 mahalles == Table 1).
  * texas: no local graph artifact (disk-reclaimed) — the mapping is REBUILT
    from raw lat/lon + the census-tract shapefile
    data/miscellaneous/tl_2022_48_tract_TX by replicating
    research/embeddings/check2hgi/preprocess.py:_assign_regions verbatim
    (unique-POI frame, sjoin predicate='intersects' with no reprojection,
    dropna(GEOID), region idx = GEOID order of first appearance, last-wins on
    boundary-duplicate placeids, check-ins filtered to mapped POIs).

SANITY GATE (mandatory): the per-state stride-1 window count must match the
paper's Table 1 Windows column (articles/[mobiwac]/src/tables/tbl1_datasets.tex,
computed by scripts/closing_data/tbl1_overlap_stats.py and validated against the
on-disk dk_ovl parquet at AL) within 1%. The JSON records computed vs expected.

Usage::

    PYTHONPATH=src .venv/bin/python scripts/closing_data/compute_markov_floor_stride1.py --state alabama
    # default: all six, smallest first, one state fully processed+freed at a time

Outputs: docs/results/closing_data/markov_floor_stride1/<state>.json
(does NOT touch docs/results/P0/).
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import pickle
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[2]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from sklearn.model_selection import StratifiedGroupKFold

from configs.globals import CATEGORIES_MAP
from configs.paths import IoPaths
from data.inputs.core import generate_sequences

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SEED = 42
N_SPLITS = 5
WINDOW = 9
STRIDE = 1
MIN_SEQ = 10
EMIT_TAIL = False
TOP_K = 10

# Paper Table 1 Windows column (articles/[mobiwac]/src/tables/tbl1_datasets.tex,
# produced by scripts/closing_data/tbl1_overlap_stats.py; AL validated exact
# against the on-disk check2hgi_dk_ovl parquet; Istanbul = rebuilt dk_ovl count).
TABLE1_WINDOWS = {
    "istanbul": 271_666,
    "alabama": 96_326,
    "arizona": 200_895,
    "florida": 1_274_418,
    "texas": 3_830_414,
    "california": 2_925_466,
}

OLD_FLOOR_DIR = _root / "docs/results/P0/simple_baselines"
OUT_DIR = _root / "docs/results/closing_data/markov_floor_stride1"

TX_TRACT_SHP = _root / "data/miscellaneous/tl_2022_48_tract_TX/tl_2022_48_tract.shp"

GRAPH_STATES = {"alabama", "arizona", "florida", "california", "istanbul"}


# ---------------------------------------------------------------------------
# Check-in stream + poi->region mapping
# ---------------------------------------------------------------------------

def _load_stream_from_graph(state: str):
    """Substrate check-in stream + maps from the frozen check2hgi graph pickle.

    graph['metadata'] is the exact substrate check-in table (userid, placeid,
    datetime, category), already sorted by (userid, datetime) and filtered to
    the POI vocabulary — the same rows/order the board's
    generate_next_input_from_checkins windows (its mergesort re-sort is a
    no-op on already-sorted data).
    """
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    logger.info("[%s] loading graph pickle %s", state, graph_path)
    with open(graph_path, "rb") as f:
        graph = pickle.load(f)
    md = graph["metadata"][["userid", "placeid", "datetime", "category"]].copy()
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    poi_to_region = np.asarray(poi_to_region, dtype=np.int64)
    del graph
    gc.collect()
    # Defensive: assert the metadata really is (userid, datetime)-sorted so the
    # closed-form windowing below is valid (stable re-sort must be a no-op).
    uid = md["userid"].to_numpy()
    ts = md["datetime"].to_numpy()
    same_user = uid[1:] == uid[:-1]
    assert not (same_user & (ts[1:] < ts[:-1])).any(), (
        f"{state}: graph metadata not sorted by (userid, datetime)")
    mapping_src = str(graph_path)
    return md, placeid_to_idx, poi_to_region, mapping_src, 0


def _rebuild_texas_mapping():
    """Replicate check2hgi preprocess._assign_regions for Texas from raw data.

    Mirrors research/embeddings/check2hgi/preprocess.py lines 129-170:
    unique-POI frame ('first' lat/lon per placeid), sjoin(how='left',
    predicate='intersects') against the tract polygons used AS-IS (the original
    build round-trips shapefile geometry through WKT CSV and *declares*
    EPSG:4326 without reprojecting; NAD83 coords are used numerically
    unchanged), dropna(GEOID), region idx = order of first GEOID appearance,
    placeid_to_idx = enumerate over the joined frame (last-wins for POIs
    intersecting several tracts at a boundary — dict semantics of the
    original), poi_to_region = positional region_idx array.
    """
    import geopandas as gpd

    raw_path = IoPaths.get_city("texas")
    logger.info("[texas] rebuilding poi->region from %s + %s", raw_path, TX_TRACT_SHP)
    pois = pd.read_parquet(raw_path, columns=["placeid", "latitude", "longitude"])
    pois = pois.groupby("placeid", sort=True).agg(
        latitude=("latitude", "first"), longitude=("longitude", "first")
    ).reset_index()
    tracts = gpd.read_file(TX_TRACT_SHP)[["GEOID", "geometry"]]
    tracts = gpd.GeoDataFrame(tracts, geometry="geometry", crs="EPSG:4326",
                              ).set_crs("EPSG:4326", allow_override=True)
    pois_gdf = gpd.GeoDataFrame(
        pois,
        geometry=gpd.points_from_xy(pois["longitude"], pois["latitude"]),
        crs="EPSG:4326",
    )
    joined = pois_gdf.sjoin(tracts, how="left", predicate="intersects")
    n_unmapped_pois = int(joined["GEOID"].isna().sum())
    joined = joined.dropna(subset=["GEOID"])
    region_to_idx = {r: i for i, r in enumerate(joined["GEOID"].unique())}
    joined["region_idx"] = joined["GEOID"].map(region_to_idx)
    placeid_to_idx = {pid: i for i, pid in enumerate(joined["placeid"].tolist())}
    poi_to_region = joined["region_idx"].to_numpy(dtype=np.int64)
    logger.info("[texas] mapped POIs=%d (unmapped dropped=%d), regions=%d",
                joined["placeid"].nunique(), n_unmapped_pois, len(region_to_idx))
    return placeid_to_idx, poi_to_region, n_unmapped_pois


def _load_stream_texas():
    placeid_to_idx, poi_to_region, n_unmapped_pois = _rebuild_texas_mapping()
    raw_path = IoPaths.get_city("texas")
    md = pd.read_parquet(raw_path, columns=["userid", "placeid", "datetime", "category"])
    md["category"] = md["category"].astype("category")
    # Board builders' sort (stable mergesort on (userid, datetime)).
    md = md.sort_values(["userid", "datetime"], kind="mergesort").reset_index(drop=True)
    n_before = len(md)
    valid = md["placeid"].isin(placeid_to_idx.keys())
    md = md[valid].reset_index(drop=True)
    n_dropped_ck = n_before - len(md)
    if n_dropped_ck:
        logger.warning("[texas] dropped %d check-ins at POIs outside all tracts "
                       "(mirrors preprocess check-in filter)", n_dropped_ck)
    mapping_src = (f"REBUILT: {IoPaths.get_city('texas')} lat/lon + {TX_TRACT_SHP} "
                   f"(preprocess._assign_regions replica; "
                   f"{n_unmapped_pois} POIs unmapped/dropped)")
    return md, placeid_to_idx, poi_to_region, mapping_src, n_dropped_ck


# ---------------------------------------------------------------------------
# Windowing (board gated stride-1) — vectorised + generate_sequences verify
# ---------------------------------------------------------------------------

def build_windows(md: pd.DataFrame, region_of_ck: np.ndarray):
    """Vectorised gated stride-1 windows.

    Under (stride=1, MIN_SEQ=10, emit_tail=False) every window has 9 real
    visits and its target is the next real visit: for a user with n check-ins,
    targets are exactly the positions with >= 9 same-user predecessors
    (n-9 windows for n >= 10, none otherwise). Returns per-window arrays:
    last_region (position 8 of the window), y_region (target), next_category,
    userid.
    """
    uid = md["userid"].to_numpy()
    n = len(md)
    idx = np.arange(n)
    new_user = np.empty(n, dtype=bool)
    new_user[0] = True
    new_user[1:] = uid[1:] != uid[:-1]
    seg_start = np.maximum.accumulate(np.where(new_user, idx, 0))
    pos_in_user = idx - seg_start
    tmask = pos_in_user >= WINDOW  # target positions
    t_idx = idx[tmask]
    last_region = region_of_ck[t_idx - 1]
    y_region = region_of_ck[t_idx]
    next_cat = md["category"].to_numpy()[t_idx]
    w_uid = uid[t_idx]
    return last_region, y_region, next_cat, w_uid


def verify_against_generate_sequences(md: pd.DataFrame, w_uid, last_region_poiid_check):
    """Per-user equivalence check against the repo's canonical generate_sequences.

    For every user, run generate_sequences(places, window=9, stride=1,
    min_sequence_length=10, emit_tail=False) and compare (a) window count and
    (b) the (window[-1], target) placeid pairs against the vectorised build.
    Streaming (per user) so RAM stays O(user).
    """
    uid_all = md["userid"].to_numpy()
    pid_all = md["placeid"].to_numpy()
    n = len(md)
    # user segment boundaries on the sorted frame
    starts = np.flatnonzero(np.r_[True, uid_all[1:] != uid_all[:-1]])
    ends = np.r_[starts[1:], n]
    total_gs = 0
    mism = 0
    vec_ptr = 0
    vec_uid = w_uid
    for a, b in zip(starts, ends):
        places = pid_all[a:b].tolist()
        seqs = generate_sequences(
            places, window_size=WINDOW, stride=STRIDE,
            min_sequence_length=MIN_SEQ, emit_tail=EMIT_TAIL,
        )
        k = len(seqs)
        total_gs += k
        # matching vectorised rows for this user are contiguous
        exp_k = max(0, (b - a) - WINDOW) if (b - a) >= MIN_SEQ else 0
        if k != exp_k:
            mism += 1
            continue
        if k:
            gs_last = [s[WINDOW - 1] for s in seqs]
            gs_tgt = [s[WINDOW] for s in seqs]
            vec_last = pid_all[a + WINDOW - 1: b - 1]
            vec_tgt = pid_all[a + WINDOW: b]
            if (list(vec_last) != gs_last) or (list(vec_tgt) != gs_tgt):
                mism += 1
            if not (vec_uid[vec_ptr:vec_ptr + k] == uid_all[a]).all():
                mism += 1
            vec_ptr += k
    return total_gs, mism


# ---------------------------------------------------------------------------
# Markov-1 region baseline (replicates baseline_markov_kstep_region k=1)
# ---------------------------------------------------------------------------

def markov1_region_fold(last_tr, y_tr, last_va, y_va):
    """First-order region Markov: P(next_region | last_region), train counts
    only, top-10 by Counter.most_common (count desc, train-insertion-order
    tie-break — identical to compute_simple_baselines), global train top-10
    fallback for unseen last-regions. Returns metrics + fallback count."""
    transition: dict[int, Counter] = defaultdict(Counter)
    for lp, lb in zip(last_tr.tolist(), y_tr.tolist()):
        transition[lp][lb] += 1
    global_counts = Counter(y_tr.tolist())
    global_topk = [label for label, _ in global_counts.most_common(TOP_K)]
    topk_cache = {k: [l for l, _ in c.most_common(TOP_K)] for k, c in transition.items()}

    n_val = len(y_va)
    preds = np.full((n_val, TOP_K), -1, dtype=np.int64)
    n_fallback = 0
    for i, lp in enumerate(last_va.tolist()):
        tk = topk_cache.get(lp)
        if tk is None:
            tk = global_topk
            n_fallback += 1
        preds[i, : len(tk)] = tk

    hit = preds == y_va[:, None]
    any10 = hit.any(axis=1)
    first = hit.argmax(axis=1)  # rank of the hit where any10; garbage elsewhere
    rr = np.zeros(n_val, dtype=np.float64)
    rr[any10] = 1.0 / (first[any10] + 1.0)
    return {
        "acc1": float(hit[:, :1].any(axis=1).mean()),
        "acc5": float(hit[:, :5].any(axis=1).mean()),
        "acc10": float(any10.mean()),
        "mrr": float(rr.mean()),
        "n_val_fallback_global": int(n_fallback),
    }


# ---------------------------------------------------------------------------
# Per-state driver
# ---------------------------------------------------------------------------

def compute_state(state: str, skip_gs_verify: bool = False) -> dict:
    t0 = time.time()
    if state == "texas":
        md, placeid_to_idx, poi_to_region, mapping_src, n_dropped_ck = _load_stream_texas()
        stream_src = f"{IoPaths.get_city('texas')} (raw; sorted (userid,datetime) mergesort; " \
                     f"{n_dropped_ck} check-ins dropped at unmapped POIs)"
    elif state in GRAPH_STATES:
        md, placeid_to_idx, poi_to_region, mapping_src, n_dropped_ck = _load_stream_from_graph(state)
        stream_src = f"{IoPaths.CHECK2HGI.get_graph_data_file(state)} graph['metadata'] (substrate stream)"
    else:
        raise ValueError(f"unknown state {state}")

    n_ck, n_users = len(md), md["userid"].nunique()
    n_regions = int(poi_to_region.max()) + 1
    logger.info("[%s] stream: %d check-ins, %d users, %d POIs, %d regions (partition)",
                state, n_ck, n_users, md["placeid"].nunique(), n_regions)

    # placeid -> region per check-in (vocabulary must be complete)
    poi_idx = md["placeid"].map(placeid_to_idx)
    n_oov = int(poi_idx.isna().sum())
    assert n_oov == 0, f"{state}: {n_oov} check-ins with placeid outside the mapping vocabulary"
    region_of_ck = poi_to_region[poi_idx.to_numpy(dtype=np.int64)]
    del poi_idx
    gc.collect()

    # --- windowing (board gated stride-1) ---
    last_region, y_region, next_cat, w_uid = build_windows(md, region_of_ck)
    n_windows = len(y_region)

    # generate_sequences equivalence (canonical code path)
    gs_verify = None
    if not skip_gs_verify:
        total_gs, mism = verify_against_generate_sequences(md, w_uid, None)
        assert mism == 0 and total_gs == n_windows, (
            f"{state}: vectorised windows != generate_sequences "
            f"(gs={total_gs}, vec={n_windows}, mismatched_users={mism})")
        gs_verify = {"generate_sequences_total": int(total_gs),
                     "mismatched_users": int(mism), "pass": True}
        logger.info("[%s] generate_sequences equivalence PASS (%d windows)", state, total_gs)

    # --- Table 1 window-count sanity gate ---
    expected = TABLE1_WINDOWS[state]
    ratio = n_windows / expected
    gate_pass = abs(ratio - 1.0) <= 0.01
    logger.info("[%s] windows=%d  Table1=%d  ratio=%.6f  gate(<=1%%)=%s",
                state, n_windows, expected, ratio, "PASS" if gate_pass else "FAIL")
    if not gate_pass:
        raise SystemExit(
            f"{state}: SANITY GATE FAILED — windows {n_windows} vs Table 1 {expected} "
            f"({(ratio - 1) * 100:+.2f}%). Investigate before reporting.")

    del md, region_of_ck
    gc.collect()

    # --- fold protocol (mirror compute_simple_baselines) ---
    inv_categories = {v: k for k, v in CATEGORIES_MAP.items()}
    y_strat_s = pd.Series(next_cat).astype(object).map(inv_categories)
    n_bad = int(y_strat_s.isna().sum())
    assert n_bad == 0, f"{state}: {n_bad} next_category values outside CATEGORIES_MAP"
    y_strat = y_strat_s.to_numpy(dtype=np.int64)
    del y_strat_s, next_cat
    userids = pd.Series(w_uid).astype(str).to_numpy()
    del w_uid
    gc.collect()

    n_classes_observed = int(y_region.max()) + 1
    sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    fold_results = []
    for fold_idx, (train_idx, val_idx) in enumerate(
            sgkf.split(np.zeros(len(y_region)), y_strat, groups=userids)):
        m = markov1_region_fold(
            last_region[train_idx], y_region[train_idx],
            last_region[val_idx], y_region[val_idx],
        )
        fold = {"fold": fold_idx, "n_train": int(len(train_idx)),
                "n_val": int(len(val_idx)), "markov_1step_region": m}
        fold_results.append(fold)
        logger.info("[%s] fold %d: n_train=%d n_val=%d acc10=%.4f (fallback=%d)",
                    state, fold_idx, fold["n_train"], fold["n_val"],
                    m["acc10"], m["n_val_fallback_global"])

    agg = {}
    for metric in ("acc1", "acc5", "acc10", "mrr"):
        vals = [f["markov_1step_region"][metric] for f in fold_results]
        agg[f"{metric}_mean"] = float(np.mean(vals))
        agg[f"{metric}_std"] = float(np.std(vals))

    # --- old (non-overlap) floor for the apples-to-apples delta ---
    old = None
    old_path = OLD_FLOOR_DIR / state / "next_region.json"
    if old_path.exists():
        od = json.loads(old_path.read_text())
        old = {
            "path": str(old_path.relative_to(_root)),
            "windowing": "non-overlap (stride-9, MIN_SEQ=5, emit_tail=True) frozen substrate",
            "best_simple_baseline": od["best_simple_baseline"],
            "best_simple_acc10_mean": od["best_simple_acc10_mean"],
            "markov_1step_region_acc10_mean": od["aggregate"]["markov_1step_region"]["acc10_mean"],
        }

    runtime = time.time() - t0
    result = {
        "state": state,
        "task": "next_region",
        "baseline": "markov_1step_region",
        "windowing": {"window_size": WINDOW, "stride": STRIDE,
                      "min_sequence_length": MIN_SEQ, "emit_tail": EMIT_TAIL,
                      "note": "board check2hgi_dk_ovl protocol (gated stride-1 overlap); "
                              "every window has 9 real visits, target = genuine next visit"},
        "fold_protocol": {"splitter": "StratifiedGroupKFold", "n_splits": N_SPLITS,
                          "shuffle": True, "seed": SEED,
                          "groups": "str(userid)",
                          "stratify": "next_category -> int via inverse CATEGORIES_MAP",
                          "mirrors": "scripts/compute_simple_baselines.py"},
        "source": {"checkin_stream": stream_src,
                   "poi_region_mapping": mapping_src,
                   "checkins_dropped_unmapped_poi": int(n_dropped_ck)},
        "n_checkins": int(n_ck),
        "n_users": int(n_users),
        "n_regions_partition": n_regions,
        "n_classes_observed": n_classes_observed,
        "n_windows": int(n_windows),
        "window_count_gate": {"computed": int(n_windows), "table1_expected": expected,
                              "ratio": ratio, "within_1pct": gate_pass,
                              "table1_source": "articles/[mobiwac]/src/tables/tbl1_datasets.tex"},
        "generate_sequences_verify": gs_verify,
        "per_fold": fold_results,
        "aggregate": {"markov_1step_region": agg},
        "markov_1step_region_acc10_mean": agg["acc10_mean"],
        "markov_1step_region_acc10_std": agg["acc10_std"],
        "old_floor_nonoverlap": old,
        "delta_acc10_new_minus_old": (
            float(agg["acc10_mean"] - old["markov_1step_region_acc10_mean"]) if old else None),
        "script": "scripts/closing_data/compute_markov_floor_stride1.py",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime_sec": round(runtime, 1),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", action="append", default=None,
                        choices=list(TABLE1_WINDOWS.keys()))
    parser.add_argument("--skip-gs-verify", action="store_true",
                        help="skip the per-user generate_sequences equivalence check")
    args = parser.parse_args()
    # smallest first so failures surface fast; one state at a time, freed between
    states = args.state or ["alabama", "arizona", "istanbul", "florida", "california", "texas"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for state in states:
        logger.info("=" * 64)
        logger.info("Markov-1 region floor (stride-1 board windowing): %s", state)
        logger.info("=" * 64)
        result = compute_state(state, skip_gs_verify=args.skip_gs_verify)
        out_path = OUT_DIR / f"{state}.json"
        out_path.write_text(json.dumps(result, indent=2))
        logger.info("[%s] saved %s | acc10=%.4f +- %.4f (old %.4f, delta %+.4f) | %.1fs",
                    state, out_path, result["markov_1step_region_acc10_mean"],
                    result["markov_1step_region_acc10_std"],
                    result["old_floor_nonoverlap"]["markov_1step_region_acc10_mean"]
                    if result["old_floor_nonoverlap"] else float("nan"),
                    result["delta_acc10_new_minus_old"] or float("nan"),
                    result["runtime_sec"])
        gc.collect()


if __name__ == "__main__":
    main()
