#!/bin/bash
# closing_data — CA/TX canonical HGI training (mirror of scripts/mtl_improvement/build_ge_hgi_train.sh,
# the recipe that produced the canonical GE HGI). Produces output/hgi/<state>/{embeddings,region_embeddings}.parquet.
#
# Why on the A40 (not locally): HGI is NOT bit-reproducible across machines (AL/AZ/FL differ local-vs-A40).
# AL/AZ/FL/GE canonical HGI all live on the A40, so CA/TX must be built on the SAME machine to keep the
# whole 6-state HGI set one canonical build (freeze comparability anchor — see closing_data FREEZE_READINESS §2).
#
# Prereqs already present on the A40 (verified 2026-06-22): poi2vec teacher (poi2vec_poi_embeddings_<State>.csv)
# + temp/ graph (edges.csv, boroughs_area.csv, pois.csv, encodings.json, poi-encoder.tensor). gowalla.pt absent
# => Phase 4 (create_hgi_graph_pickle) builds it; force_preprocess=False reuses temp/. HGI trains on CPU
# (epoch=2000) so the A40 GPU stays free.
#
# Launch (per state, detached, parallel — 16 threads each on the 32-core A40):
#   setsid bash scripts/closing_data/build_catx_hgi.sh California > /tmp/catx_hgi/california.log 2>&1 < /dev/null &
#   setsid bash scripts/closing_data/build_catx_hgi.sh Texas      > /tmp/catx_hgi/texas.log      2>&1 < /dev/null &
set -uo pipefail
CITY="${1:?usage: build_catx_hgi.sh <California|Texas>}"
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
LOGDIR=/tmp/catx_hgi; mkdir -p "$LOGDIR"
export OMP_NUM_THREADS=16
echo "[$(date '+%H:%M:%S')] ${CITY}-HGI Phase4(pickle)+Phase5(train) start (pid=$$)"
PYTHONPATH=src:research CITY="$CITY" $PY - <<'PYEOF'
import os, time
from pathlib import Path
from argparse import Namespace
import numpy as np, pandas as pd
from configs.paths import IoPaths, Resources
from configs.model import InputsConfig
from embeddings.hgi.preprocess import create_hgi_graph_pickle
from embeddings.hgi.hgi import train_hgi

CITY = os.environ["CITY"]
SHP = {"California": Resources.TL_CA, "Texas": Resources.TL_TX}
assert CITY in SHP, f"unsupported {CITY}"
CRW = 0.7  # cross_region_weight w_r — canonical US-state value

# ---- Phase 4: build gowalla.pt (mirror build_ge_hgi_train.sh) ----
gowalla = IoPaths.HGI.get_graph_data_file(CITY)
if gowalla.exists():
    print(f"[phase4] skip — {gowalla} exists")
else:
    poi_emb_path = IoPaths.HGI.get_poi_emb_file(CITY)
    print(f"[phase4] poi_emb_path={poi_emb_path} exists={Path(poi_emb_path).exists()}")
    create_hgi_graph_pickle(city=CITY, poi_emb_path=str(poi_emb_path), cross_region_weight=CRW)
    assert gowalla.exists(), "phase4 did not write gowalla.pt"
    print(f"[phase4] wrote {gowalla}")

# ---- Phase 5: train HGI (canonical: dim=64, epoch=2000, lr=0.006, warmup=40, w_r=0.7, CPU) ----
cfg = Namespace(dim=InputsConfig.EMBEDDING_DIM, alpha=0.5, attention_head=4, lr=0.006,
                gamma=1.0, max_norm=0.9, epoch=2000, warmup_period=40, poi2vec_epochs=100,
                force_preprocess=False, cross_region_weight=CRW, device='cpu',
                shapefile=str(SHP[CITY]))
t0 = time.time(); train_hgi(CITY, cfg); print(f"[train_hgi] wall={time.time()-t0:.1f}s")

reg_p = IoPaths.HGI.get_state_dir(CITY) / "region_embeddings.parquet"
emb_p = IoPaths.HGI.get_state_dir(CITY) / "embeddings.parquet"
df = pd.read_parquet(reg_p)
cols = [c for c in df.columns if c not in ('placeid', 'category', 'region_id')]
arr = df[cols].to_numpy(float)
print(f"[verify] region_embeddings shape={df.shape} nan={np.isnan(arr).any()} std={arr.std():.4f}")
print(f"[verify] embeddings.parquet exists={emb_p.exists()}")
print(f"DONE_{CITY}_HGI_TRAIN")
PYEOF
echo "[$(date '+%H:%M:%S')] ${CITY}-HGI exit=$?"
