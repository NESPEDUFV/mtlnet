"""Phase 5: full HGI train for FL (pickle already built by probe). Writes embeddings.parquet
+ region_embeddings.parquet, then validates non-degeneracy. Detached megascript."""
import sys, time
from pathlib import Path
from argparse import Namespace

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import numpy as np
import pandas as pd
import torch
from configs.paths import IoPaths, EmbeddingEngine, Resources
from configs.model import InputsConfig
from embeddings.hgi.hgi import train_hgi

CITY = "Florida"
CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM, alpha=0.5, attention_head=4, lr=0.006,
    gamma=1.0, max_norm=0.9, epoch=2000, warmup_period=40, poi2vec_epochs=100,
    force_preprocess=True, cross_region_weight=0.7, device='cpu', shapefile=str(Resources.TL_FL),
)

def main():
    t0 = time.time()
    train_hgi(CITY, CONFIG)
    dt = time.time() - t0
    print(f"[train_hgi] wall-clock = {dt:.1f}s ({dt/3600:.3f} h)")

    emb_p = IoPaths.get_embedd(CITY, EmbeddingEngine.HGI)
    reg_p = IoPaths.HGI.get_state_dir(CITY) / "region_embeddings.parquet"
    for name, p in [("embeddings", emb_p), ("region_embeddings", reg_p)]:
        df = pd.read_parquet(p)
        emb_cols = [c for c in df.columns if c not in ("placeid", "category", "region_id")]
        arr = df[emb_cols].to_numpy(dtype=np.float64)
        print(f"[verify] {name}: shape={df.shape} cols={df.columns[:3].tolist()}... "
              f"nan={np.isnan(arr).any()} min={arr.min():.4f} max={arr.max():.4f} "
              f"mean={arr.mean():.4f} std={arr.std():.4f} "
              f"n_unique_rows={len(np.unique(arr, axis=0))}")
    print("DONE_HGI_FL_TRAIN")

if __name__ == "__main__":
    main()
