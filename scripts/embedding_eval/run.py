"""CLI runner for the embedding-eval ladder — L0 (geometry) + L1 (linear probe).

Example:
    python scripts/embedding_eval/run.py \
        --engines hgi check2hgi check2hgi_resln_design_b \
        --states florida --tasks cat reg \
        --ref-engine hgi

Writes:
    docs/results/embedding_eval/metrics_long.csv   (one row per metric/seed)
    docs/results/embedding_eval/summary.md         (engine x task tables)

L2 (capacity ladder) / L3 (MTL) are GPU-hour sequence runs launched via
scripts/train.py; pass --emit-l2l3 to print the ready-to-run commands.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# repo root + src/ on path (mirror scripts/train.py)
_root = Path(__file__).resolve().parent.parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np
import pandas as pd

from configs.paths import EmbeddingEngine

from sklearn.metrics import accuracy_score, f1_score

from scripts.embedding_eval.geometry import (
    centroid_separability, knn_predict, linear_cka, silhouette,
)
from scripts.embedding_eval.labels import ItemTable, load_item_table
from scripts.embedding_eval.linear_probe import fit_probe, make_folds

TASK_NAMES = {"cat": "next-cat", "reg": "next-reg", "poi": "next-poi"}


def _engine(name: str) -> EmbeddingEngine:
    return EmbeddingEngine(name)


def _records_for(
    tab: ItemTable,
    task: str,
    knn_k: int,
    sil_sample: int,
    seed: int,
    probe_epochs: int,
    probe_lr: float,
    n_folds: int = 5,
    max_items: int | None = None,
) -> list[dict]:
    """L0 + L1 rows for one (engine, state, granularity, task), via SHARED
    5-fold CV: the same StratifiedKFold split feeds both the train-free geometry
    (kNN train->test, silhouette/separability on the held-out fold) and the
    linear probe (train 4 folds, eval 1). Each metric => 5 per-fold values =>
    mean±SD downstream. Matches L2's 5-fold protocol."""
    mask = tab.valid_mask(task)
    emb = tab.emb[mask]
    labels = tab.labels(task)[mask]
    rows: list[dict] = []
    base = dict(engine=tab.engine, state=tab.state, task=task, granularity=tab.granularity)

    if len(np.unique(labels)) < 2:
        return rows  # degenerate (e.g. poi @ poi-granularity) — skip

    # subsample AFTER masking (m9) for comparable realized N across engines
    if max_items is not None and len(labels) > max_items:
        rng = np.random.default_rng(seed)
        sel = rng.choice(len(labels), size=max_items, replace=False)
        emb, labels = emb[sel], labels[sel]

    # densify labels to [0, C) so num_classes is exact and folds share a space
    uniq, dense = np.unique(labels, return_inverse=True)
    num_classes = len(uniq)
    dense = dense.astype(np.int64)
    placeids = tab.placeid[mask]
    if max_items is not None and len(placeids) > max_items:
        placeids = placeids[sel]  # keep placeids aligned with the subsample

    rows.append({**base, "level": "L0", "metric": "n_eval", "seed": -1, "value": float(len(dense))})
    rows.append({**base, "level": "L0", "metric": "label_coverage", "seed": -1, "value": float(mask.mean())})

    # ISOLATION: assign each item to a fold by its PLACEID in canonical (sorted)
    # order, so the fold of a POI is identical across engines regardless of each
    # engine's row ordering. Same seed + same placeid set => byte-identical
    # held-out sets per engine -> the comparison isolates the substrate, not the
    # split. (Earlier per-engine StratifiedKFold gave different folds per engine.)
    order = np.argsort(placeids, kind="stable")
    fold_of = np.empty(len(dense), dtype=np.int64)
    for _fi, (_, _te) in enumerate(make_folds(dense[order], n_folds, seed)):
        fold_of[order[_te]] = _fi

    for fi in range(n_folds):
        te = np.where(fold_of == fi)[0]
        tr = np.where(fold_of != fi)[0]
        # ---- L0 geometry on this fold (train-free) ----
        pred = knn_predict(emb[tr], dense[tr], emb[te], k=knn_k)
        rows.append({**base, "level": "L0", "metric": f"knn{knn_k}_acc", "seed": fi,
                     "value": float(accuracy_score(dense[te], pred))})
        rows.append({**base, "level": "L0", "metric": f"knn{knn_k}_macro_f1", "seed": fi,
                     "value": float(f1_score(dense[te], pred, average="macro", zero_division=0))})
        rows.append({**base, "level": "L0", "metric": "silhouette", "seed": fi,
                     "value": silhouette(emb[te], dense[te], sample=sil_sample, seed=seed)})
        for m, v in centroid_separability(emb[te], dense[te]).items():
            rows.append({**base, "level": "L0", "metric": m, "seed": fi, "value": v})
        # ---- L1 linear probe on this fold ----
        res = fit_probe(emb[tr], dense[tr], emb[te], dense[te], num_classes,
                        seed=seed, epochs=probe_epochs, lr=probe_lr)
        for m, v in res.items():
            rows.append({**base, "level": "L1", "metric": m, "seed": fi, "value": v})
    return rows


def _cka_rows(tables: dict, ref_engine: str) -> list[dict]:
    """Linear CKA of each engine vs ref, on placeid-aligned POI-pooled embeddings."""
    rows: list[dict] = []
    by_state: dict[str, dict[str, ItemTable]] = {}
    for (eng, state), tab in tables.items():
        if tab.granularity != "poi":
            continue
        by_state.setdefault(state, {})[eng] = tab
    for state, engs in by_state.items():
        if ref_engine not in engs:
            continue
        ref = engs[ref_engine]
        ref_idx = {int(p): i for i, p in enumerate(ref.placeid)}
        for eng, tab in engs.items():
            common = [int(p) for p in tab.placeid if int(p) in ref_idx]
            if len(common) < 10:
                continue
            tab_idx = {int(p): i for i, p in enumerate(tab.placeid)}
            xi = ref.emb[[ref_idx[p] for p in common]]
            yi = tab.emb[[tab_idx[p] for p in common]]
            rows.append({
                "engine": eng, "state": state, "task": "-", "granularity": "poi",
                "level": "L0", "metric": f"cka_vs_{ref_engine}", "seed": -1,
                "value": linear_cka(xi, yi),
            })
    return rows


def _md_table(piv: pd.DataFrame) -> str:
    """Render a pivot table (with index) as a markdown table — no tabulate dep."""
    piv = piv.reset_index()
    cols = [str(c) for c in piv.columns]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for _, r in piv.iterrows():
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append(f"{v:.4f}" if not np.isnan(v) else "nan")
            else:
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows])


def _agg_table(df: pd.DataFrame, level: str, task: str) -> pd.DataFrame:
    """engine × metric pivot of 'mean±SD' over the 5 CV folds (seed>=0 rows)."""
    sub = df[(df.level == level) & (df.task == task) & (df.seed >= 0)]
    agg = sub.groupby(["engine", "metric"])["value"].agg(["mean", "std"]).reset_index()
    agg["cell"] = agg.apply(lambda r: f"{r['mean']:.4f}±{r['std'] if not np.isnan(r['std']) else 0:.4f}", axis=1)
    return agg.pivot_table(index="engine", columns="metric", values="cell", aggfunc="first")


def _write_summary(df: pd.DataFrame, out: Path) -> None:
    lines = ["# Embedding-eval ladder — summary (5-fold CV, mean±SD over folds)\n"]
    for level, name in (("L0", "L0 geometry"), ("L1", "L1 linear probe")):
        for task in sorted(df[(df.level == level) & (df.seed >= 0)].task.unique()):
            if task == "-":
                continue
            lines.append(f"\n## {name} — {TASK_NAMES.get(task, task)} (mean±SD, 5 folds)\n")
            lines.append(_md_table(_agg_table(df, level, task)))
    # CKA (full-data diagnostic, single value)
    cka = df[df.metric.str.startswith("cka_vs_")]
    if len(cka):
        lines.append("\n## L0 — linear CKA vs reference (full-data)\n")
        lines.append(_md_table(cka.pivot_table(index="engine", columns="metric", values="value").round(4)))
    out.write_text("\n".join(lines) + "\n")


def _emit_l2l3(engines: list[str], states: list[str]) -> None:
    print("\n# ---- L2 capacity ladder (STL sequence task) ----")
    for eng in engines:
        for st in states:
            for head in ("next_gru", "next_stan_flow"):
                print(
                    f"python scripts/train.py --task next --state {st} --engine {eng} "
                    f"--cat-head {head} --epochs 50 --folds 5 --seed 0 --no-checkpoints"
                )
    print("\n# ---- L3 MTL (deployment) — H3-alt small-state recipe; see CLAUDE.md for B9/large-state ----")
    print("# NOTE: bare defaults DO NOT reproduce paper numbers. Full canonical flags below.")
    for st in states:
        print(
            f"python scripts/train.py --task mtl --task-set check2hgi_next_region \\\n"
            f"    --state {st} --engine check2hgi --seed 0 \\\n"
            f"    --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn \\\n"
            f"    --mtl-loss static_weight --category-weight 0.75 --scheduler constant \\\n"
            f"    --cat-head next_gru --reg-head next_getnext_hard \\\n"
            f"    --task-a-input-type checkin --task-b-input-type region \\\n"
            f"    --per-fold-transition-dir output/check2hgi/{st} --no-checkpoints"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Embedding-eval ladder L0+L1 runner")
    ap.add_argument("--engines", nargs="+", required=True)
    ap.add_argument("--states", nargs="+", default=["florida"])
    ap.add_argument("--tasks", nargs="+", default=["cat", "reg"], choices=["cat", "reg", "poi"])
    ap.add_argument("--granularity", default="poi", choices=["poi", "checkin"])
    ap.add_argument("--max-items", type=int, default=None,
                    help="subsample items (needed for checkin-granularity L0)")
    ap.add_argument("--knn-k", type=int, default=10)
    ap.add_argument("--silhouette-sample", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42, help="shuffle seed for the 5-fold split")
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument("--probe-epochs", type=int, default=300,
                    help="max epochs; early-stops on a train-val slice well before this")
    ap.add_argument("--probe-lr", type=float, default=1e-2)
    ap.add_argument("--ref-engine", default="hgi", help="reference engine for CKA")
    ap.add_argument("--out", default="docs/results/embedding_eval")
    ap.add_argument("--emit-l2l3", action="store_true")
    args = ap.parse_args()

    out_dir = _root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    tables: dict = {}
    all_rows: list[dict] = []
    for name in args.engines:
        eng = _engine(name)
        for state in args.states:
            print(f"[load] {name} / {state} ({args.granularity}) ...", flush=True)
            # load FULL table; subsample per-task AFTER masking (fairness, m9)
            tab = load_item_table(state, eng, granularity=args.granularity, seed=args.seed)
            tables[(name, state)] = tab
            for task in args.tasks:
                print(f"  [eval] task={task}", flush=True)
                all_rows += _records_for(
                    tab, task, args.knn_k, args.silhouette_sample,
                    args.seed, args.probe_epochs, args.probe_lr,
                    n_folds=args.n_folds, max_items=args.max_items,
                )

    if args.granularity == "poi":
        all_rows += _cka_rows(tables, args.ref_engine)

    df = pd.DataFrame(all_rows)
    csv_path = out_dir / "metrics_long.csv"
    df.to_csv(csv_path, index=False)
    _write_summary(df, out_dir / "summary.md")
    print(f"\n[done] {len(df)} rows -> {csv_path}")
    print(f"[done] summary -> {out_dir / 'summary.md'}")

    if args.emit_l2l3:
        _emit_l2l3(args.engines, args.states)


if __name__ == "__main__":
    main()
