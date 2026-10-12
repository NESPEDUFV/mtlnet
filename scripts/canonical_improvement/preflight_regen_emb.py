"""Stage B helper for canonical_improvement pre-flight on A40.

Regenerates check2hgi embeddings + per-fold seeded log_T for AL + AZ.
Run from the worktree (or main repo) after Stage A baseline runs land.

Workflow (orchestrated by run_stage_b.sh, not this file):
    1. Backup output/check2hgi/{alabama,arizona} -> *.bak_existingemb
    2. python docs/infra/a40/preflight_regen_emb.py
    3. python scripts/compute_region_transition.py --state alabama --per-fold --n-splits 5 --seed 42
    4. python scripts/compute_region_transition.py --state arizona --per-fold --n-splits 5 --seed 42
    5. Re-launch scripts/train.py MTL H3-alt on each (parallel)
"""

import sys
from argparse import Namespace
from copy import copy
from pathlib import Path

# [2026-09-02] FIXED: four .parent hops resolved to the repo root while these scripts lived
# in docs/infra/a40/; the 2026-05-16 move to scripts/canonical_improvement/ left them one
# level too high, so every one of them died on `ModuleNotFoundError: No module named
# 'configs'` before running a single line. Caught 2026-09-02 trying to run the Q13 ablation.
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from configs.paths import Resources, EmbeddingEngine
from configs.model import InputsConfig
from embeddings.check2hgi.check2hgi import create_embedding
from data.inputs.builders import generate_next_input_from_checkins

BASE_CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    num_layers=2,
    attention_head=4,
    alpha_c2p=0.4,
    alpha_p2r=0.3,
    alpha_r2c=0.3,
    lr=0.001,
    gamma=1.0,
    max_norm=0.9,
    epoch=500,
    mini_batch_threshold=5_000_000,
    batch_size=2**13,
    num_neighbors=10,
    device='cuda',  # A40 GPU
    shapefile=None,
    force_preprocess=True,
    edge_type='user_sequence',
    temporal_decay=3600.0,
    use_compile=True,
    use_amp=False,
)

STATES = [
    ('Alabama', Resources.TL_AL),
    ('Arizona', Resources.TL_AZ),
]


def run_one(state_name: str, shapefile) -> None:
    cfg = copy(BASE_CONFIG)
    cfg.shapefile = shapefile
    print(f"[regen] {state_name} on device={cfg.device}", flush=True)
    create_embedding(state=state_name, args=cfg)
    print(f"[inputs] {state_name} next-POI inputs", flush=True)
    generate_next_input_from_checkins(state_name, EmbeddingEngine.CHECK2HGI)
    print(f"[done] {state_name}", flush=True)


if __name__ == "__main__":
    for name, shp in STATES:
        run_one(name, shp)
