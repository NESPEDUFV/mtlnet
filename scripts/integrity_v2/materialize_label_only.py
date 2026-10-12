"""Materialize the LABEL-ONLY benchmark as an engine, so it can be scored on the dedicated protocol.

Why this exists. The audit's probe ladder reports a label-only reference -- what a classifier reaches
given nothing but the nine observed category labels -- and that number is the one that decides whether
a representation is worth having. But the ladder's value is measured with the study's own instrument:
one fold, a scikit-learn probe, averaged over classifier seeds. The dedicated-model board is next_gru
over five folds at the f1-best epoch. Comparing an arm from one protocol against a benchmark from the
other is exactly the mixing this study's own report banner forbids, and a reviewer caught it being
done.

The fix is to measure the benchmark on the SAME protocol as the arms. This writes an engine whose
per-visit "embedding" is a one-hot of the visit's own category, zero-padded to the canonical width so
the reported command runs unchanged. A model given that input sees the nine observed labels and
nothing else, which is precisely the benchmark, now expressed in dedicated-model units.

The padding is not cosmetic. next_gru infers its input dimension from the column count divided by the
window, so a 7-wide block would train a differently shaped model and would not be comparable. Zero
padding to 64 keeps the architecture identical and adds no information.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
WINDOW = 9
DIM = 64
N_CAT = 7


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--source-engine", default="check2hgi_dk_ovl")
    ap.add_argument("--dest-engine", required=True)
    ap.add_argument("--categories-from", required=True,
                    help="a per-visit parquet carrying userid, datetime and category, used only to "
                         "read each observed visit's own category label")
    args = ap.parse_args()

    st = args.state.lower()
    src = REPO / "output" / args.source_engine / st / "input"
    nxt = pd.read_parquet(src / "next.parquet")
    emb = pd.read_parquet(args.categories_from)

    cats = sorted(emb["category"].astype(str).unique())
    assert len(cats) == N_CAT, f"expected {N_CAT} categories, found {len(cats)}: {cats}"
    cmap = {c: i for i, c in enumerate(cats)}

    # Per-visit one-hot, in the same per-user visit order the windowing assumes.
    emb = emb.sort_values(["userid", "datetime"]).reset_index(drop=True)
    eu = emb["userid"].astype(np.int64).to_numpy()
    ec = emb["category"].astype(str).map(cmap).to_numpy()
    nu = nxt["userid"].astype(np.int64).to_numpy()

    S = np.zeros((len(nxt), WINDOW, DIM), dtype=np.float32)
    rows, keep = [], np.zeros(len(nxt), dtype=bool)
    for u in np.unique(nu):
        rw = np.where(nu == u)[0]
        ei = np.where(eu == u)[0]
        for k, r in enumerate(rw):
            if k + WINDOW >= len(ei):
                break
            S[r, np.arange(WINDOW), ec[ei[k:k + WINDOW]]] = 1.0
            keep[r] = True
            rows.append(r)
    rows = np.asarray(rows)

    flat = S[rows].reshape(len(rows), WINDOW * DIM)
    out = pd.DataFrame(flat, columns=[str(i) for i in range(WINDOW * DIM)])
    out["userid"] = nu[rows]
    out["next_category"] = nxt["next_category"].to_numpy()[rows]

    dest = REPO / "output" / args.dest_engine / st / "input"
    dest.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dest / "next.parquet", index=False)

    reg = src / "next_region.parquet"
    if reg.exists():
        pd.read_parquet(reg).iloc[rows].reset_index(drop=True).to_parquet(
            dest / "next_region.parquet", index=False)

    meta = {
        "study": "check2hgi_integrity_v2 / label-only benchmark on the dedicated protocol",
        "state": st, "n_windows": int(len(out)), "n_windows_source": int(len(nxt)),
        "content": ("each of the nine window slots is a one-hot of that OBSERVED visit's own "
                    f"category in the first {N_CAT} of {DIM} columns; the remaining columns are zero"),
        "why_padded": ("next_gru infers input width from columns divided by window, so padding to "
                       f"{DIM} keeps the architecture identical to the embedding arms while adding "
                       "no information"),
        "purpose": ("gives the label-only reference in the SAME units as the dedicated-model board, "
                    "so an arm's value can be judged without mixing protocols"),
        "categories": cats,
    }
    (dest.parent / "materialize.json").write_text(json.dumps(meta, indent=2))
    print(f"[label-only] {st}: wrote {dest}/next.parquet ({len(out)} of {len(nxt)} windows)")


if __name__ == "__main__":
    main()
