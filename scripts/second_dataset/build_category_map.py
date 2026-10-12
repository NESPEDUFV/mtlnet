"""Build + version the Foursquare(v1) -> Gowalla-7-root category map (Phase E2).

City-generic (Massive-STEPS uses the SAME FSQ v1 taxonomy for every city, so the
10->7 crosswalk below is shared). See docs/studies/second_dataset/category_map.md
for the rationale, method, and known divergences.

METHOD: each FSQ leaf id -> its FSQ v1 top-level root (via fsq_v1_tree.json,
verified 100% leaf-id coverage for NYC+Istanbul) -> Gowalla root (FSQ_ROOT_TO_GOWALLA).
The fine FSQ leaf is preserved in the corpus for an Acc@k bridge metric.

Outputs (per city):  data/massive_steps_<city>/category_map.{csv,json}
Run:  python scripts/second_dataset/build_category_map.py --city istanbul
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cities import get as get_city, data_dir  # noqa: E402

VERSION = "v1-2026-06-15"
GOWALLA_ROOTS = ["Community", "Entertainment", "Food", "Nightlife",
                 "Outdoors", "Shopping", "Travel"]

# ---- THE DECISION: FSQ v1 top-level root -> Gowalla 7-root --------------------
FSQ_ROOT_TO_GOWALLA = {
    "Arts & Entertainment":        "Entertainment",
    "Event":                       "Entertainment",
    "Food":                        "Food",
    "Nightlife Spot":              "Nightlife",
    "Outdoors & Recreation":       "Outdoors",
    "Shop & Service":              "Shopping",
    "Travel & Transport":          "Travel",
    "College & University":        "Community",
    "Professional & Other Places": "Community",
    "Residence":                   "Community",
}
DIVERGENCES = [
    "Gym / Fitness / Yoga Studio: FSQ 'Outdoors & Recreation' -> Outdoors; Gowalla files fitness under Shopping/Services.",
    "Neighborhood / Plaza / Scenic Lookout: FSQ 'Outdoors & Recreation' -> Outdoors (matches Gowalla 'Plaza / Square').",
    "Office / Building / Coworking: FSQ 'Professional & Other Places' -> Community (no Gowalla 'work' root).",
]


def _fsq_tree(cdir: Path) -> dict:
    p = cdir / "fsq_v1_tree.json"
    if not p.exists():  # shared taxonomy — fall back to the nyc copy
        src = data_dir("nyc") / "fsq_v1_tree.json"
        if src.exists():
            shutil.copy(src, p)
    return json.loads(p.read_text())


def _inventory(cdir: Path) -> pd.DataFrame:
    inv_path = cdir / "fine_category_inventory.csv"
    if inv_path.exists():
        return pd.read_csv(inv_path, dtype={"venue_category_id": str})
    raw = cdir / "raw" / "tabular"
    df = pd.concat(
        [pd.read_parquet(raw / f"{s}-00000-of-00001.parquet",
                         columns=["venue_category_id", "venue_category"])
         for s in ("train", "validation", "test")], ignore_index=True)
    inv = (df.groupby(["venue_category_id", "venue_category"]).size()
             .reset_index(name="count").sort_values("count", ascending=False))
    inv.to_csv(inv_path, index=False)
    return inv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default="nyc")
    args = ap.parse_args()
    get_city(args.city)
    cdir = data_dir(args.city)

    tree = _fsq_tree(cdir)
    inv = _inventory(cdir)

    rows, unmapped = [], []
    for _, r in inv.iterrows():
        cid = str(r["venue_category_id"])
        node = tree.get(cid)
        if node is None:
            unmapped.append((cid, r["venue_category"]))
            fsq_root, gow = None, "None"
        else:
            fsq_root = node["root"]
            gow = FSQ_ROOT_TO_GOWALLA.get(fsq_root, "None")
        rows.append({"venue_category_id": cid, "fsq_category_name": r["venue_category"],
                     "fsq_root": fsq_root, "gowalla_root": gow, "count": int(r["count"])})

    out = pd.DataFrame(rows).sort_values("count", ascending=False)
    assert set(out["gowalla_root"].unique()) <= set(GOWALLA_ROOTS + ["None"])
    (cdir / "category_map.csv").write_text(out.to_csv(index=False))

    dist = out.groupby("gowalla_root")["count"].sum().sort_values(ascending=False)
    summary = {
        "city": args.city, "version": VERSION,
        "fsq_tree_source": "github:MettiHoof/3circles .../4sq_categories.json (FSQ v1)",
        "n_fsq_leaves": int(len(out)),
        "leaf_id_coverage": f"{int(out['fsq_root'].notna().sum())}/{len(out)}",
        "fsq_root_to_gowalla": FSQ_ROOT_TO_GOWALLA, "gowalla_roots": GOWALLA_ROOTS,
        "checkin_weighted_root_distribution": {k: int(v) for k, v in dist.items()},
        "leaf_count_per_root": {k: int(v) for k, v in out["gowalla_root"].value_counts().items()},
        "unmapped_leaf_ids": unmapped, "divergences": DIVERGENCES,
    }
    (cdir / "category_map.json").write_text(json.dumps(summary, indent=2))
    print(f"[{args.city}] leaves={len(out)} coverage={summary['leaf_id_coverage']} unmapped={len(unmapped)}")
    for k, v in dist.items():
        print(f"  {k:14s} {v:7d} ({100*v/dist.sum():4.1f}%)")


if __name__ == "__main__":
    main()
