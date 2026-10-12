#!/usr/bin/env python
"""Category geometry (silhouette + kNN purity) of the DELIVERED v18 representation.

Why this exists. Ch.5 (`articles/dissertacao/src/chapters/5_mobiwac/06_results.tex`) and its figure
(`src/figures/mobiwac/fig3_embquality_diss.py`) quoted silhouette ~0.57 / kNN purity ~0.98 vs HGI
~0.00 / ~0.78, measured on the v14 engine `check2hgi_design_k_resln_mae_l0_1`, an earlier build
(source: `docs/studies/closing_data/archive/run_logs/PART1_QUALITY/metrics_long.csv`). The author asked
for the same numbers on the delivered build `check2hgi_v18`. This file is the exact wrapper that
produced them.

Run (2026-09-30 05:10-05:11 UTC, 60 s, on nespedgpu, repo commit 157c6e10), fed to python over stdin
from ~/PoiMtlNet with PYTHONPATH=src:research PYTHONDONTWRITEBYTECODE=1; outputs went to
/tmp/geom_v18_20260930/ (on /, never /home, never output/) and were copied here unchanged
(metrics_long.csv md5 a0d02843982409ab1160038ecbcac6d6, verified equal on both sides). RUNINFO.txt
is the run's own start/end record.

Equivalent command (the wrapper only adds the v18 path redirect below):
    scripts/embedding_eval/run.py \
        --engines hgi check2hgi_design_k_resln_mae_l0_1 check2hgi_v18 \
        --states alabama arizona florida california texas \
        --tasks cat --granularity poi --max-items 40000 --seed 42 \
        --knn-k 10 --silhouette-sample 10000 --ref-engine hgi \
        --out /tmp/geom_v18_20260930

The sampling flags were read off the old CSV, not recalled: n_eval = 11848 / 20666 / 40000 x 3 means
--max-items 40000; its `seed` column 0..4 is the FOLD index of run.py's shared StratifiedKFold (seed
42, keyed on sorted placeid); k=10 and the 10000 silhouette sample are run.py defaults.

Why a wrapper. run.py reads `IoPaths.load_embedd(state, engine)`, i.e. output/<engine>/<state>/
embeddings.parquet, and mean-pools per placeid (granularity=poi). The v18 engine directory was
materialized with input/, temp/ and the region symlink only -- no embeddings.parquet -- so the wrapper
redirects that one call, for engine check2hgi_v18 only, to the per-visit export the engine was built
from. hgi and v14 go through the unmodified loader. Nothing is written anywhere except --out.

v18 inputs, per state, and why each is the delivered representation:
  alabama     results/check2hgi_integrity_v2/alabama/E2/embeddings_insample.parquet
              engine materialized from E2/win_matched.npz; materialize.json equivalence record:
              insample export == per-window prefix_forward_only readout over 96,326 windows,
              max abs 2.38e-06
  arizona     results/check2hgi_v18/arizona/V18/embeddings_insample.parquet
              equivalence record: 200,895 windows, max abs 2.86e-06
  florida     results/check2hgi_v18/florida/V18/embeddings_insample.parquet
              engine materialized from this parquet; equivalence record: 1,274,418 windows,
              max abs 3.10e-06
  california  results/check2hgi_v18/california/V18/embeddings_insample.parquet
  texas       results/check2hgi_v18/texas/V18/embeddings_insample.parquet
              CAVEAT: materialize.json has equivalence_vs_per_window_npz = null. Both engines were
              materialized FROM this parquet ("one-shot full-graph forward-only export, windowed by
              indexing"), so it is by construction the input those cells trained on; what is
              unmeasured is export-vs-per-window readout, not whether this is the delivered input.

Checks that make the v18 numbers citable:
  * n_eval identical across hgi / v14 / v18 at every state (11848, 20666, 40000, 40000, 40000).
  * REPRODUCTION FIRST: hgi and v14, recomputed in the same session, match PART1_QUALITY per
    state-fold -- silhouette max |diff| 5.96e-08 (v14) / 1.86e-09 (hgi), knn10_acc max |diff| 0.
    The harness is unchanged; the only thing that moved is the v18 input.

Result (mean over state x fold, n=25; SD with ddof=1, the convention of the figure's constants):
                     silhouette        knn10_acc
  v14 (old)          0.5668 +- 0.0302  0.9827 +- 0.0039   (= the constants currently printed)
  v18 (delivered)    0.5140 +- 0.0533  0.9804 +- 0.0065
  hgi                0.0003 +- 0.0046  0.7750 +- 0.0311   (unchanged)
  AL/AZ/FL only: v18 0.4889 / 0.9770 (the three states with an equivalence record).
"""
import runpy
import sys

import pandas as pd

import configs.paths as P

_orig = P.IoPaths.load_embedd
V18 = {"alabama": "results/check2hgi_integrity_v2/alabama/E2/embeddings_insample.parquet"}
for st in ["arizona", "florida", "california", "texas"]:
    V18[st] = f"results/check2hgi_v18/{st}/V18/embeddings_insample.parquet"


def _patched(state, engine):
    if engine == P.EmbeddingEngine.CHECK2HGI_V18:
        print(f"[wrapper] v18/{state} <- {V18[state.lower()]}", flush=True)
        return pd.read_parquet(V18[state.lower()])
    return _orig(state, engine)


P.IoPaths.load_embedd = staticmethod(_patched)
sys.argv = ["run.py", "--engines", "hgi", "check2hgi_design_k_resln_mae_l0_1", "check2hgi_v18",
            "--states", "alabama", "arizona", "florida", "california", "texas",
            "--tasks", "cat", "--granularity", "poi", "--max-items", "40000", "--seed", "42",
            "--knn-k", "10", "--silhouette-sample", "10000", "--ref-engine", "hgi",
            "--out", "/tmp/geom_v18_20260930"]
runpy.run_path("scripts/embedding_eval/run.py", run_name="__main__")
