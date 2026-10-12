"""T2.1 helper — regenerate check2hgi embeddings with custom p2r hard-neg knobs.

Forwards into the args namespace:
    --p2r-hard-neg-prob FLOAT     (None → legacy 25%; explicit float overrides)
    --p2r-hard-neg-min-batch INT  (default 50000; controls FL inclusion)
    --p2r-sim-lo FLOAT, --p2r-sim-hi FLOAT  (default 0.6, 0.8; similarity band)

α weights remain canonical (0.4 / 0.3 / 0.3); scheduler/WD remain canonical.
"""

import argparse
import sys
from argparse import Namespace
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

STATE_TO_SHP = {
    "alabama": ("Alabama", Resources.TL_AL),
    "arizona": ("Arizona", Resources.TL_AZ),
    "florida": ("Florida", Resources.TL_FL),
    "georgia": ("Georgia", Resources.TL_GA),
    "california": ("California", Resources.TL_CA),
    "texas": ("Texas", Resources.TL_TX),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, choices=list(STATE_TO_SHP))
    ap.add_argument("--p2r-hard-neg-prob", type=float, default=None,
                    help="Hard-neg rate at p2r. None=legacy canonical 25% gated.")
    ap.add_argument("--p2r-hard-neg-min-batch", type=int, default=50000,
                    help="Batch-size gate. Set very high to force-enable for FL.")
    ap.add_argument("--p2r-sim-lo", type=float, default=0.6)
    ap.add_argument("--p2r-sim-hi", type=float, default=0.8)
    ap.add_argument("--epoch", type=int, default=500)
    # Optimizer-hygiene knobs (default = canonical Adam + StepLR γ=1 + no WD;
    # for Tier 2+ exploration the provisional canonical is AdamW wd=5e-2).
    ap.add_argument("--scheduler", default="step", choices=("step", "cosine", "warmup_constant"))
    ap.add_argument("--warmup-pct", type=float, default=0.0)
    ap.add_argument("--weight-decay", type=float, default=0.0)
    ap.add_argument("--eta-min-ratio", type=float, default=0.01)
    args = ap.parse_args()

    name_camel, shapefile = STATE_TO_SHP[args.state]
    cfg = Namespace(
        dim=InputsConfig.EMBEDDING_DIM,
        num_layers=2,
        attention_head=4,
        alpha_c2p=0.4,
        alpha_p2r=0.3,
        alpha_r2c=0.3,
        lr=0.001,
        gamma=1.0,
        max_norm=0.9,
        epoch=args.epoch,
        mini_batch_threshold=5_000_000,
        batch_size=2**13,
        num_neighbors=10,
        device='cuda',
        shapefile=shapefile,
        force_preprocess=False,
        edge_type='user_sequence',
        temporal_decay=3600.0,
        use_compile=True,
        use_amp=False,
        p2r_hard_neg_prob=args.p2r_hard_neg_prob,
        p2r_hard_neg_min_batch=args.p2r_hard_neg_min_batch,
        p2r_hard_neg_sim_range=(args.p2r_sim_lo, args.p2r_sim_hi),
        scheduler=args.scheduler,
        warmup_pct=args.warmup_pct,
        weight_decay=args.weight_decay,
        eta_min_ratio=args.eta_min_ratio,
    )
    print(f"[T2.1-regen] state={args.state} p2r_hard_neg_prob={args.p2r_hard_neg_prob} "
          f"min_batch={args.p2r_hard_neg_min_batch} sim=({args.p2r_sim_lo},{args.p2r_sim_hi}) "
          f"sched={args.scheduler} wd={args.weight_decay}",
          flush=True)
    create_embedding(state=name_camel, args=cfg)
    print(f"[inputs] state={args.state} regenerating next-POI inputs", flush=True)
    generate_next_input_from_checkins(name_camel, EmbeddingEngine.CHECK2HGI)
    print(f"[done] state={args.state}", flush=True)


if __name__ == "__main__":
    main()
