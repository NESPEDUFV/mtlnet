#!/bin/bash
# GE HGI training (deferred T0.1b tail) — produces output/hgi/georgia/region_embeddings.parquet
# (+ embeddings.parquet) needed for the STL-HGI reg ceiling + the composite (d) at GE.
# Two phases, mirroring build_hgi_fl_phase4_probe.py (Phase 4 pickle) + build_hgi_fl_train.py (Phase 5):
#   Phase 4: create_hgi_graph_pickle(poi_emb_path=poi2vec, cross_region_weight=0.7) -> temp/gowalla.pt
#   Phase 5: train_hgi (epoch=2000, lr=0.006, warmup=40) on CPU -> region_embeddings.parquet
# HGI trains on CPU, so the A40 stays free for STL ceiling runs in parallel.
#   Launch: setsid bash scripts/mtl_improvement/build_ge_hgi_train.sh > /tmp/ge_hgi/run.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
LOGDIR=/tmp/ge_hgi; mkdir -p "$LOGDIR"
export OMP_NUM_THREADS=16
echo "[$(date '+%H:%M:%S')] GE-HGI Phase4 (pickle) + Phase5 (train) start"
PYTHONPATH=src:research $PY - <<'PYEOF'
import sys, time
from pathlib import Path
from argparse import Namespace
import numpy as np, pandas as pd
from configs.paths import IoPaths, EmbeddingEngine, Resources
from configs.model import InputsConfig
from embeddings.hgi.preprocess import create_hgi_graph_pickle
from embeddings.hgi.hgi import train_hgi

CITY = "Georgia"
CRW = 0.7

# ---- Phase 4: build gowalla.pt (mirror build_hgi_fl_phase4_probe.py) ----
gowalla = IoPaths.HGI.get_graph_data_file(CITY)
if gowalla.exists():
    print(f"[phase4] skip — {gowalla} exists")
else:
    poi_emb_path = IoPaths.HGI.get_poi_emb_file(CITY)
    print(f"[phase4] poi_emb_path={poi_emb_path} exists={Path(poi_emb_path).exists()}")
    create_hgi_graph_pickle(city=CITY, poi_emb_path=str(poi_emb_path), cross_region_weight=CRW)
    assert gowalla.exists(), "phase4 did not write gowalla.pt"
    print(f"[phase4] wrote {gowalla}")

# ---- Phase 5: train HGI ----
cfg = Namespace(dim=InputsConfig.EMBEDDING_DIM, alpha=0.5, attention_head=4, lr=0.006,
                gamma=1.0, max_norm=0.9, epoch=2000, warmup_period=40, poi2vec_epochs=100,
                force_preprocess=False, cross_region_weight=CRW, device='cpu',
                shapefile=str(Resources.TL_GA))
t0=time.time(); train_hgi(CITY, cfg); print(f"[train_hgi] wall={time.time()-t0:.1f}s")
reg_p = IoPaths.HGI.get_state_dir(CITY) / "region_embeddings.parquet"
df = pd.read_parquet(reg_p); cols=[c for c in df.columns if c not in ('placeid','category','region_id')]
arr=df[cols].to_numpy(float)
print(f"[verify] region_embeddings shape={df.shape} nan={np.isnan(arr).any()} "
      f"std={arr.std():.4f} n_unique={len(np.unique(arr,axis=0))}")
print("DONE_GE_HGI_TRAIN")
PYEOF
echo "[$(date '+%H:%M:%S')] GE-HGI exit=$?"
