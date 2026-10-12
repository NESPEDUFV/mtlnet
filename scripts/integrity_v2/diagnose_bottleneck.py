"""Why does a raw one-hot beat a 64-d embedding that was built from the same information?

The puzzle. A model given only the nine observed category one-hots reaches 28.9964 macro-F1 on the
dedicated protocol. Every honest embedding arm -- which is built from those same categories PLUS the
hour, the weekday, and a two-hop neighbourhood -- lands between 27.51 and 28.47, i.e. slightly BELOW
it. A representation with strictly more input information performs worse than the raw feature. Two
explanations are possible and they have different consequences, so they must be separated rather than
argued about.

  H1 UNDER-TRAINING. The dedicated model on the embedding arms is stopping too early or is
     mis-tuned, so the embedding's extra information is present but unused. If this is the cause the
     fix is a longer schedule or a different learning rate, and the leak conclusion is unaffected but
     the "honest representation is worthless" conclusion is premature.

  H2 LOSSY COMPRESSION. The 64-d vector does not preserve the category of its own visit. The encoder
     was trained to reconstruct a place's mean category composition, not to preserve a single visit's
     label, and a two-layer graph convolution over a path graph averages each node with its
     neighbours. If this is the cause, then the embedding literally destroys the feature that carries
     most of the signal, and no amount of downstream training can recover it.

The test that separates them is direct: probe each arm's vectors for the OWN category of the visit
they represent. That is not a prediction task and involves no target -- it asks whether the
representation retains a feature it was handed as input. A raw one-hot scores 1.0 by construction. An
embedding that scores near the majority-class floor has thrown the feature away.

Reported alongside it: the same probe for the visit's own hour bucket and its own place, so the loss
can be attributed rather than merely observed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

REPO = Path(__file__).resolve().parents[2]


def probe(Z: np.ndarray, y: np.ndarray, seeds: int = 5) -> dict:
    """Macro-F1 of a linear probe recovering y from Z, averaged over seeds."""
    out = []
    for s in range(seeds):
        tr, te = train_test_split(np.arange(len(Z)), test_size=0.3, random_state=s, stratify=y)
        m = LogisticRegression(max_iter=600)
        m.fit(Z[tr], y[tr])
        out.append(f1_score(y[te], m.predict(Z[te]), average="macro"))
    return {"macro_f1_mean": float(np.mean(out)), "macro_f1_std": float(np.std(out)),
            "n_seeds": seeds, "n": int(len(Z))}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--arms", nargs="+", required=True,
                    help="label=path pairs; path is a per-visit embeddings parquet")
    ap.add_argument("--max-rows", type=int, default=40000,
                    help="subsample for probe cost; applied identically to every arm")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    res = {"state": args.state.lower(), "max_rows": args.max_rows, "arms": {},
           "question": ("does the representation retain the OWN category of the visit it represents? "
                        "A raw one-hot scores 1.0 by construction; an embedding near the "
                        "majority-class floor has discarded the feature it was given as input."),
           "hypotheses": {
               "H1_under_training": "the embedding keeps the feature and the head fails to use it",
               "H2_lossy_compression": "the embedding does not keep the feature at all",
           }}

    for spec in args.arms:
        label, path = spec.split("=", 1)
        df = pd.read_parquet(path)
        dims = sorted([c for c in df.columns if str(c).isdigit()], key=int)
        rng = np.random.default_rng(0)
        idx = np.arange(len(df))
        if len(idx) > args.max_rows:
            idx = rng.choice(idx, args.max_rows, replace=False)
            idx.sort()
        Z = df[dims].to_numpy(np.float32)[idx]
        sub = df.iloc[idx]

        y_cat = sub["category"].astype(str).to_numpy()
        maj = pd.Series(y_cat).value_counts(normalize=True).iloc[0]
        arm = {"dim": len(dims), "own_category": probe(Z, y_cat),
               "majority_class_share": float(maj)}

        # own hour bucket, to show whether the temporal columns survive the bottleneck
        hb = (pd.to_datetime(sub["datetime"]).dt.hour // 6).astype(str).to_numpy()
        arm["own_hour_bucket"] = probe(Z, hb)

        # a coarse place probe: the 20 most visited places, so the label set stays learnable
        top = sub["placeid"].value_counts().head(20).index
        m = sub["placeid"].isin(top).to_numpy()
        if m.sum() > 400:
            arm["own_place_top20"] = probe(Z[m], sub.loc[m, "placeid"].astype(str).to_numpy())

        res["arms"][label] = arm
        print(f"  {label:22s} dim={len(dims):3d}  own-category {arm['own_category']['macro_f1_mean']:.4f} "
              f"(majority {maj:.4f})  own-hour {arm['own_hour_bucket']['macro_f1_mean']:.4f}",
              flush=True)

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2))
    print(f"[diagnose] wrote {outp}")


if __name__ == "__main__":
    main()
