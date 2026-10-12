"""Write a study arm as a normal engine directory, so the REPORTED pipeline can consume it unchanged.

Why this exists. Every metric in this study so far came from a small category head written inside the
study, at one fold, 30 epochs, one hyperparameter setting. That is fine for comparing arms to each
other but it cannot be placed beside the dissertation's Table 3, whose dedicated column is the tuned
`next_gru` (hidden 256, two layers, dropout 0.3) at n=20 with a per-dataset recipe and macro-F1 taken
at the f1-best epoch. The two differ in architecture, protocol, epoch selection, and (at Florida) in
how many users are present, and the observed gaps run in OPPOSITE directions at the two datasets
(Alabama higher, Florida lower), so no single correction reconciles them.

The fix is to stop reimplementing the predictor. This script converts an arm into the on-disk layout
`scripts/train.py` already reads -- `<engine>/<state>/input/next.parquet`, a flat table of
SLIDE_WINDOW x dim float columns named "0".."575" plus `userid` and `next_category` -- so the reported
training command runs on the strict representation with no code change and no reimplementation. The
number it produces is then comparable to the reported one by construction, because it is the same
model, the same head, the same recipe, and the same scorer.

Region labels are copied through unchanged from the source engine, because a strict CHECK-IN readout
does not alter which region a historical place belongs to, and the loader hard-fails unless
next_region.parquet is row-aligned with next.parquet by userid.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
WINDOW = 9


def load_arm(path: Path, next_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return ([n_windows, 9, dim] tensor, row ids into next_df) for a per-window npz arm."""
    z = np.load(path)
    S = z["seq"].astype(np.float32)
    uu = z["userid"].astype(np.int64)
    starts = z["window_start"].astype(np.int64)
    nu = next_df["userid"].astype(np.int64).to_numpy()
    rows = np.empty(len(uu), dtype=np.int64)
    for u in np.unique(uu):
        m = uu == u
        rw = np.where(nu == u)[0]
        st = starts[m]
        assert st.max() < len(rw), f"user {u}: window {st.max()} beyond {len(rw)} rows"
        rows[m] = rw[st]
    return S, rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--arm-npz", required=True,
                    help="a per-window npz produced by infer_checkins.py (readout prefix / "
                         "prefix_forward_only)")
    ap.add_argument("--source-engine", default="check2hgi_dk_ovl",
                    help="engine whose next.parquet defines the row space and supplies region labels")
    ap.add_argument("--dest-engine", required=True,
                    help="engine directory to create under output/, e.g. check2hgi_strict_al")
    args = ap.parse_args()

    st = args.state.lower()
    src_dir = REPO / "output" / args.source_engine / st / "input"
    nxt = pd.read_parquet(src_dir / "next.parquet")
    S, rows = load_arm(Path(args.arm_npz), nxt)

    dim = S.shape[2]
    n_feat = WINDOW * dim
    flat = S.reshape(len(S), n_feat)

    # Column names must match what load_next_data expects: digit-named, sorted by int, so that
    # embedding_dim = n_features // SLIDE_WINDOW recovers the right dim.
    out = pd.DataFrame(flat, columns=[str(i) for i in range(n_feat)])
    out["userid"] = nxt["userid"].to_numpy()[rows]
    out["next_category"] = nxt["next_category"].to_numpy()[rows]

    dest = REPO / "output" / args.dest_engine / st / "input"
    dest.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dest / "next.parquet", index=False)

    # Region labels ride along, subset to the same rows and in the same order. The loader verifies
    # userid equality between the two files and hard-fails on a mismatch, which is the guard that
    # makes this safe.
    src_reg = src_dir / "next_region.parquet"
    if src_reg.exists():
        reg = pd.read_parquet(src_reg).iloc[rows].reset_index(drop=True)
        reg.to_parquet(dest / "next_region.parquet", index=False)

    # Anything else the engine dir carries is copied verbatim so the preset pre-flight passes.
    for extra in src_dir.glob("*.parquet"):
        if extra.name not in ("next.parquet", "next_region.parquet"):
            shutil.copy(extra, dest / extra.name)

    meta = {
        "study": "check2hgi_integrity_v2",
        "state": st,
        "arm_npz": str(args.arm_npz),
        "source_engine": args.source_engine,
        "dest_engine": args.dest_engine,
        "n_windows": int(len(out)),
        "n_windows_source": int(len(nxt)),
        "window": WINDOW,
        "embedding_dim": dim,
        "purpose": ("lets scripts/train.py run the REPORTED dedicated model on this arm, so the "
                    "resulting macro-F1 is comparable to the dissertation's dedicated column "
                    "instead of to a head written inside the study"),
        "region_labels": "copied from the source engine, subset to the same rows and order",
    }
    (dest.parent / "materialize.json").write_text(json.dumps(meta, indent=2))
    print(f"[materialize] {st}: wrote {dest}/next.parquet "
          f"({len(out)} of {len(nxt)} source windows, dim={dim})")


if __name__ == "__main__":
    main()
