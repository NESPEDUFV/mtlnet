"""Regenerate HGI embeddings for one US state using the canonical pipeline CONFIG.

Loads `process_state` + `CONFIG` from pipelines/embedding/hgi.pipe.py (which pins
the paper-grade settings: lr=0.006 + warmup_period=40, 2000 epochs, dim=64,
cross_region_weight=0.7) WITHOUT editing that shared file's STATES dict. Runs the
full 5-stage pipeline -> output/hgi/<state>/{embeddings,region_embeddings}.parquet.

Run CPU-only (set CUDA_VISIBLE_DEVICES="") so it never contends with a GPU sweep.

    CUDA_VISIBLE_DEVICES="" python scripts/embedding_eval/regen_hgi.py --state Alabama
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# shapefile resource per state name (matches hgi.pipe.py STATES intent)
from configs.paths import Resources  # noqa: E402

SHAPEFILES = {
    "Alabama": Resources.TL_AL,
    "Arizona": Resources.TL_AZ,
    "California": Resources.TL_CA,
    "Texas": Resources.TL_TX,
    "Florida": Resources.TL_FL,
}


def _load_pipe():
    path = _root / "pipelines" / "embedding" / "hgi.pipe.py"
    spec = importlib.util.spec_from_file_location("hgi_pipe_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True, choices=list(SHAPEFILES))
    args = ap.parse_args()

    mod = _load_pipe()
    print(f"[regen_hgi] {args.state}: CONFIG lr={mod.CONFIG.lr} warmup={mod.CONFIG.warmup_period} "
          f"epoch={mod.CONFIG.epoch} dim={mod.CONFIG.dim}", flush=True)
    ok = mod.process_state(args.state, {"shapefile": SHAPEFILES[args.state], "cross_region_weight": 0.7})
    print(f"[regen_hgi] {args.state}: {'OK' if ok else 'FAILED'}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
