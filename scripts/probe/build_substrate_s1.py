"""Phase 11 S1 — Substrate audit: c2p hard-negative sampling.

Builds canonical c2hgi embeddings with ``c2p_hard_neg_prob`` enabled at the
check-in↔POI boundary. Same preprocessing, same architecture, same loss
weights — only the c2p negative-sampling distribution changes.

Hypothesis: c2hgi's c2p boundary uses pure-random negatives over the global
POI pool. A check-in vs random POI is a trivial discrimination (different
category, different region). Sampling from same-region different-POI
should sharpen the c2p signal — which propagates upward to the POI
representation that POI2Region consumes.

The pretraining graph (``temp/checkin_graph.pt``) is reused from the
canonical c2hgi output dir via symlink. Only the embeddings parquet files
are written into the dedicated ``output/check2hgi_substrate_s1/<state>/``.

Usage::

    python scripts/probe/build_substrate_s1.py --state alabama --epochs 500 --c2p_hard_neg_prob 0.25
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

import torch
from configs.paths import _Check2HGIIoPath, OUTPUT_DIR, Resources, IoPaths, EmbeddingEngine
from pathlib import Path as _Path

# Redirect the c2hgi output dir BEFORE importing/calling train_check2hgi.
SUBSTRATE_DIR = OUTPUT_DIR / "check2hgi_substrate_s1"
_Check2HGIIoPath._check2hgi_dir = SUBSTRATE_DIR  # type: ignore[attr-defined]

# IoPaths.get_embedd() builds its path independently of _Check2HGIIoPath
# (see paths.py: ``OUTPUT_DIR / engine.value / state / EMBEDDINGS_FILE``).
# Override it so the main check-in embeddings parquet ALSO lands in the
# substrate dir instead of overwriting canonical c2hgi output.
_orig_get_embedd = IoPaths.get_embedd

def _substrate_get_embedd(cls, state: str, embedd_engine: EmbeddingEngine) -> _Path:  # type: ignore[override]
    if embedd_engine == EmbeddingEngine.CHECK2HGI:
        return SUBSTRATE_DIR / state.lower() / IoPaths.EMBEDDINGS_FILE
    return _orig_get_embedd(state, embedd_engine)

IoPaths.get_embedd = classmethod(_substrate_get_embedd)  # type: ignore[assignment]

from embeddings.check2hgi.check2hgi import train_check2hgi  # noqa: E402


def _link_or_copy_graph(state: str, canonical_root: Path) -> None:
    """Make the substrate temp dir reuse canonical preprocessing artefacts."""
    target_temp = SUBSTRATE_DIR / state.lower() / "temp"
    target_temp.mkdir(parents=True, exist_ok=True)
    src_temp = canonical_root / state.lower() / "temp"
    for fname in ("checkin_graph.pt", "boroughs_area.csv", "sequences_next.parquet"):
        src = src_temp / fname
        dst = target_temp / fname
        if dst.exists():
            continue
        if not src.exists():
            print(f"[warn] missing canonical artefact {src}; skipping link")
            continue
        try:
            os.symlink(src, dst)
        except OSError:
            import shutil
            shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", "--city", dest="city", required=True)
    parser.add_argument("--c2p_hard_neg_prob", type=float, default=0.25)
    parser.add_argument("--epoch", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--max_norm", type=float, default=0.9)
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--num_layers", type=int, default=2)
    parser.add_argument("--attention_head", type=int, default=4)
    parser.add_argument("--alpha_c2p", type=float, default=0.4)
    parser.add_argument("--alpha_p2r", type=float, default=0.3)
    parser.add_argument("--alpha_r2c", type=float, default=0.3)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--use_amp", action="store_true", default=False)
    parser.add_argument("--use_compile", action="store_true", default=False)
    parser.add_argument("--mini_batch_threshold", type=int, default=5_000_000)
    parser.add_argument("--batch_size", type=int, default=2**13)
    parser.add_argument("--num_neighbors", type=int, default=10)
    parser.add_argument("--shapefile", type=str, default=None,
                        help="Optional. If unset, picked from state name.")
    parser.add_argument("--force_preprocess", action="store_true")
    parser.add_argument("--edge_type", type=str, default="user_sequence")
    parser.add_argument("--temporal_decay", type=float, default=3600.0)
    args = parser.parse_args()

    # Auto-pick MPS on Apple Silicon if available.
    if args.device == "cpu" and torch.backends.mps.is_available():
        args.device = "mps"

    if args.shapefile is None:
        sf_map = {
            "alabama": Resources.TL_AL,
            "arizona": Resources.TL_AZ,
            "florida": Resources.TL_FL,
        }
        key = args.city.lower()
        if key not in sf_map:
            parser.error(f"--shapefile required for city={args.city}; known: {list(sf_map)}")
        args.shapefile = str(sf_map[key])

    canonical_root = OUTPUT_DIR / "check2hgi"
    _link_or_copy_graph(args.city, canonical_root)

    print(
        f"[substrate-s1] state={args.city}  c2p_hard_neg_prob={args.c2p_hard_neg_prob}  "
        f"epoch={args.epoch}  device={args.device}\n"
        f"[substrate-s1] writing to {SUBSTRATE_DIR / args.city.lower()}"
    )
    train_check2hgi(args.city, args)


if __name__ == "__main__":
    main()
