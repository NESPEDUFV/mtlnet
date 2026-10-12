"""T1.3 helper — regenerate check2hgi embedding for a single state with custom α.

Args:
    --state {alabama,arizona}
    --alpha-c2p FLOAT
    --alpha-p2r FLOAT
    --alpha-r2c FLOAT

Output dir is the canonical `output/check2hgi/{state}/` (overwriting prior).
After this, the caller must rebuild next_region.parquet + per-fold log_T.
"""

import argparse
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

STATE_TO_SHP = {
    "alabama": ("Alabama", Resources.TL_AL),
    "arizona": ("Arizona", Resources.TL_AZ),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, choices=list(STATE_TO_SHP))
    ap.add_argument("--alpha-c2p", type=float, required=True)
    ap.add_argument("--alpha-p2r", type=float, required=True)
    ap.add_argument("--alpha-r2c", type=float, required=True)
    ap.add_argument("--epoch", type=int, default=500)
    ap.add_argument(
        "--i-know-this-overwrites-the-frozen-v11-substrate",
        action="store_true",
        help=(
            "REQUIRED. This script writes to output/check2hgi/<state>/, which IS the frozen v11 "
            "BRACIS paper substrate; the repo-root CLAUDE.md says do not overwrite it. It also "
            "builds the CANONICAL GCN model, not the generation the dissertation delivers "
            "(that is output/check2hgi_v18/, built by scripts/integrity_v2/build_study_repr.py). "
            "Back the directory up and verify the copy before passing this."
        ),
    )
    args = ap.parse_args()

    # [2026-09-02] SAFETY GATE. Until today this script could not run at all: it computed the repo
    # root with four .parent hops, correct while it lived in docs/infra/a40/ and one level too high
    # since the 2026-05-16 move, so it died on ModuleNotFoundError before doing anything. Fixing
    # that path made a DESTRUCTIVE script runnable again, which is worse than leaving it broken:
    # it overwrites the frozen v11 substrate and it builds the wrong generation. Hence the flag.
    if not getattr(args, "i_know_this_overwrites_the_frozen_v11_substrate", False):
        sys.exit(
            "REFUSING to run.\n"
            "  This writes to output/check2hgi/%s/, the FROZEN v11 BRACIS substrate.\n"
            "  It also builds the canonical GCN model, NOT the generation the dissertation\n"
            "  delivers (output/check2hgi_v18/, via scripts/integrity_v2/build_study_repr.py).\n"
            "  If you meant to vary the alpha weights on the delivered generation, this is the\n"
            "  wrong tool. If you really mean this: back the directory up, verify the copy, and\n"
            "  pass --i-know-this-overwrites-the-frozen-v11-substrate." % args.state
        )

    name_camel, shapefile = STATE_TO_SHP[args.state]
    cfg = Namespace(
        dim=InputsConfig.EMBEDDING_DIM,
        num_layers=2,
        attention_head=4,
        alpha_c2p=args.alpha_c2p,
        alpha_p2r=args.alpha_p2r,
        alpha_r2c=args.alpha_r2c,
        lr=0.001,
        gamma=1.0,
        max_norm=0.9,
        epoch=args.epoch,
        mini_batch_threshold=5_000_000,
        batch_size=2**13,
        num_neighbors=10,
        device='cuda',
        shapefile=shapefile,
        force_preprocess=False,  # graphs already preprocessed; only retrain
        edge_type='user_sequence',
        temporal_decay=3600.0,
        use_compile=True,
        use_amp=False,
    )
    print(f"[regen-α] state={args.state} α=({args.alpha_c2p},{args.alpha_p2r},{args.alpha_r2c}) epoch={args.epoch}", flush=True)
    create_embedding(state=name_camel, args=cfg)
    print(f"[inputs] state={args.state} regenerating next-POI inputs", flush=True)
    generate_next_input_from_checkins(name_camel, EmbeddingEngine.CHECK2HGI)
    print(f"[done] state={args.state}", flush=True)


if __name__ == "__main__":
    main()
