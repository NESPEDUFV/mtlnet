"""Standalone POI2Vec runner for Tier B substrate prerequisite.

Trains POI2Vec at a single state and writes:
    output/hgi/{state}/poi2vec_poi_embeddings_{State}.csv
    output/hgi/{state}/embeddings.pt           (poi_emb_path, tensor format)
    output/hgi/{state}/poi2vec_fclass_embeddings_{State}.pt

Usage:
    .venv/bin/python scripts/substrate_protocol_cleanup/run_poi2vec.py --city Alabama --epochs 100 --device cuda
"""

import argparse
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import torch  # noqa: E402
from embeddings.hgi.poi2vec import train_poi2vec  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    device = torch.device(args.device)
    t0 = time.time()
    out = train_poi2vec(
        city=args.city,
        epochs=args.epochs,
        embedding_dim=args.dim,
        batch_size=args.batch_size,
        lr=args.lr,
        k=args.k,
        device=device,
        save_intermediate=True,
    )
    elapsed = time.time() - t0
    print(f"[POI2VEC DONE] city={args.city} elapsed_sec={elapsed:.1f} out={out}")


if __name__ == "__main__":
    main()
