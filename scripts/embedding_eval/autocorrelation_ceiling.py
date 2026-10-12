#!/usr/bin/env python3
"""Autocorrelation ceiling for the next-category task.

WHY THIS EXISTS
---------------
The leak-sniff gate (``scripts/embedding_eval/leak_sniff.py``) flags an embedding whose per-step
probe beats a reference. Two different quantities have both been called that reference:

  (a) the CONTROL ENGINE's achieved per-step probe score. This is what the gate uses IN CODE
      (``flag if perstep_F1 > control_perstep_F1 + margin``); at Florida it is 0.4090.
  (b) the AUTOCORRELATION CEILING, described in RESCREEN.md:57 as "predicting next-cat from the
      genuine last-visited category". That is a label-only quantity and needs no embedding.

The internal record treats (a) and (b) as interchangeable ("~0.45 F1", "the clean control ceiling
(~0.41)"). This script computes (b) directly so the two can be compared instead of conflated.

WHAT IT COMPUTES
----------------
Macro-F1 of predicting ``next_category`` using ONLY the genuine category history of the input
window. No embeddings are read. Four label-only predictors are reported, and the ceiling is the
best of them, because a ceiling is the best achievable under the information restriction:

  persistence          predict next = last-visited category (no fitting)
  last_cat             balanced logistic on one-hot(last-visited category)
  window_counts        balanced logistic on category counts over the 9-window
  window_positional    balanced logistic on positional one-hots of all 9 slots

``class_weight="balanced"`` is used because the target metric is macro-F1; an unweighted logistic
optimizes log-loss and systematically under-predicts rare categories, which understates a ceiling.

DERIVATION RULES (identical to the training inputs, not re-invented here)
  last-visited POI : last non-pad entry of poi_0..poi_8   (src/data/inputs/next_region.py:132-146)
  POI -> category  : checkin_graph.pt["metadata"]; modal category per placeid
  label            : next.parquet["next_category"], row-alignment asserted against
                     sequences_next.parquet on userid
  protocol         : GroupKFold(5) by userid, macro-F1, mean over folds (matches leak_sniff.py)

Some corpora (Istanbul) carry venues re-categorized over time, so placeid -> category is not
strictly a function. The modal category is used, the ambiguity rate is recorded, and a strict
variant that drops every ambiguous place is reported as a sensitivity check.
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupKFold

ROOT = Path("/Users/vitor/Desktop/mestrado/ingred")
STATES = ["alabama", "arizona", "florida", "texas", "california", "istanbul"]
N_FOLDS = 5
WINDOW = 9


def _load(state: str):
    base = ROOT / "output/check2hgi" / state
    gpath = base / "temp/checkin_graph.pt"
    spath = base / "temp/sequences_next.parquet"
    npath = base / "input/next.parquet"
    for p in (gpath, spath, npath):
        if not p.exists():
            raise FileNotFoundError(f"{state}: missing {p.relative_to(ROOT)}")

    with open(gpath, "rb") as f:
        graph = pickle.load(f)
    meta = graph["metadata"]
    per_place = meta.groupby("placeid")["category"].nunique()
    ambiguous = set(per_place[per_place > 1].index)
    place2cat = meta.groupby("placeid")["category"].agg(lambda s: s.value_counts().idxmax())

    seq = pd.read_parquet(spath)
    nxt = pd.read_parquet(npath, columns=["userid", "next_category"])
    if len(seq) != len(nxt):
        raise ValueError(f"{state}: row counts disagree ({len(seq)} vs {len(nxt)})")
    if not (seq["userid"].astype(str).values == nxt["userid"].astype(str).values).all():
        raise ValueError(f"{state}: userid columns are not row-aligned")

    cats = sorted(meta["category"].unique())
    c2i = {c: i for i, c in enumerate(cats)}
    poi = seq[[f"poi_{i}" for i in range(WINDOW)]].astype(np.int64).to_numpy()
    catmat = (pd.Series(poi.ravel()).map(place2cat).map(c2i)
                .to_numpy(dtype=float).reshape(poi.shape))
    y = nxt["next_category"].map(c2i).to_numpy()
    users = seq["userid"].astype(str).to_numpy()
    return poi, catmat, y, users, cats, ambiguous, len(per_place), len(ambiguous)


def _features(poi, catmat, cats, ambiguous, strict):
    valid = poi >= 0
    keep = valid.any(axis=1)
    if strict and ambiguous:
        # drop rows whose LAST slot is an ambiguous place (that slot defines the ceiling feature)
        lastpos = np.where(keep, valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1), 0)
        lastpoi = poi[np.arange(len(poi)), lastpos]
        keep = keep & ~np.isin(lastpoi, list(ambiguous))
    K = len(cats)
    n = len(poi)
    lastpos = np.where(keep, valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1), 0)
    li = catmat[np.arange(n), lastpos]
    keep = keep & ~np.isnan(li)

    x_last = np.zeros((n, K), dtype=np.float32)
    idx = np.arange(n)[keep]
    x_last[idx, li[keep].astype(int)] = 1.0

    x_pos = np.zeros((n, WINDOW * K), dtype=np.float32)
    x_cnt = np.zeros((n, K), dtype=np.float32)
    for j in range(WINDOW):
        cj = catmat[:, j]
        m = ~np.isnan(cj)
        x_pos[np.arange(n)[m], j * K + cj[m].astype(int)] = 1.0
        np.add.at(x_cnt, (np.arange(n)[m], cj[m].astype(int)), 1.0)
    return keep, {"last_cat": x_last, "window_counts": x_cnt, "window_positional": x_pos}


def ceiling(state: str, strict: bool = False) -> dict:
    poi, catmat, y, users, cats, ambiguous, n_places, n_ambig = _load(state)
    keep, feats = _features(poi, catmat, cats, ambiguous, strict)
    y_k, u_k = y[keep], users[keep]
    splits = list(GroupKFold(N_FOLDS).split(feats["last_cat"][keep], y_k, u_k))

    scores = {}
    # persistence needs no fitting
    pf = [f1_score(y_k[te], feats["last_cat"][keep][te].argmax(1),
                   average="macro", zero_division=0) for _, te in splits]
    scores["persistence"] = pf
    for name, X in feats.items():
        Xk = X[keep]
        f = []
        for tr, te in splits:
            clf = LogisticRegression(max_iter=3000, class_weight="balanced")
            clf.fit(Xk[tr], y_k[tr])
            f.append(f1_score(y_k[te], clf.predict(Xk[te]), average="macro", zero_division=0))
        scores[name] = f

    means = {k: float(np.mean(v)) for k, v in scores.items()}
    best = max(means, key=means.get)
    maj = []
    for tr, te in splits:
        m = np.bincount(y_k[tr], minlength=len(cats)).argmax()
        maj.append(f1_score(y_k[te], np.full(len(te), m), average="macro", zero_division=0))
    return {
        "state": state, "strict": strict,
        "rows_used": int(keep.sum()), "rows_total": int(len(y)),
        "places": n_places, "places_multi_category": n_ambig,
        "n_classes": len(cats),
        "ceiling_macro_f1": round(means[best], 4),
        "ceiling_predictor": best,
        "ceiling_sd": round(float(np.std(scores[best], ddof=1)), 4),
        "per_predictor": {k: round(v, 4) for k, v in means.items()},
        "majority_floor_macro_f1": round(float(np.mean(maj)), 4),
        "per_fold_ceiling": [round(float(v), 4) for v in scores[best]],
    }


def main() -> None:
    rows, strict_rows, errors = [], [], []
    for st in STATES:
        try:
            r = ceiling(st)
            rows.append(r)
            line = (f"{st:11s} ceiling={r['ceiling_macro_f1']:.4f} "
                    f"({r['ceiling_predictor']}, sd {r['ceiling_sd']:.4f})  "
                    f"floor={r['majority_floor_macro_f1']:.4f}  n={r['rows_used']:,}  "
                    f"| {r['per_predictor']}")
            if r["places_multi_category"]:
                sr = ceiling(st, strict=True)
                strict_rows.append(sr)
                line += f"  [strict={sr['ceiling_macro_f1']:.4f}]"
            print(line)
        except Exception as exc:
            errors.append({"state": st, "error": f"{type(exc).__name__}: {exc}"})
            print(f"{st:11s} SKIPPED — {type(exc).__name__}: {exc}")

    outdir = ROOT / "docs/results/embedding_eval/rescreen_cat"
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {
        "what": "label-only autocorrelation ceiling for next-category (no embeddings read)",
        "definition_source": "docs/results/embedding_eval/rescreen_cat/RESCREEN.md:57",
        "protocol": (f"GroupKFold({N_FOLDS}) by userid; macro-F1; mean over folds; "
                     "ceiling = best of {persistence, last_cat, window_counts, "
                     "window_positional}; balanced logistic because the metric is macro-F1"),
        "results": rows,
        "sensitivity_strict_drop_ambiguous_last_place": strict_rows,
        "skipped": errors,
    }
    (outdir / "autocorrelation_ceiling.json").write_text(json.dumps(payload, indent=2))
    pd.DataFrame(rows).drop(columns=["per_predictor", "per_fold_ceiling"]).to_csv(
        outdir / "autocorrelation_ceiling.csv", index=False)
    pd.DataFrame([{"state": r["state"], **r["per_predictor"]} for r in rows]).to_csv(
        outdir / "autocorrelation_ceiling_predictors.csv", index=False)


if __name__ == "__main__":
    main()
