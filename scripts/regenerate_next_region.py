"""Regenerate ``next_region.parquet`` with the ``last_region_idx`` column.

The column is needed by the ``next_getnext_hard`` head (B5 — faithful
GETNext). Running this script is additive: the extra column is ignored
by every reader that selects by column name (which is how all existing
FoldCreator code paths read the parquet). Older-schema parquets still
work with the pre-B5 code path.

Usage::

    python scripts/regenerate_next_region.py --state alabama
    python scripts/regenerate_next_region.py --state arizona
    python scripts/regenerate_next_region.py --state florida
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import EmbeddingEngine, IoPaths
from data.inputs.next_region import build_next_region_frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    args = parser.parse_args()

    df, n_regions = build_next_region_frame(args.state)
    if "last_region_idx" not in df.columns:
        raise RuntimeError(
            "build_next_region_frame did not include last_region_idx. "
            "Pull the latest code or regenerate from the check2HGI pipeline."
        )
    n_pad = int((df["last_region_idx"] < 0).sum())
    print(
        f"[{args.state}] rows={len(df)}  n_regions={n_regions}  "
        f"pad_rows (last_region=-1): {n_pad} ({n_pad / len(df) * 100:.1f}%)"
    )
    out = IoPaths.get_next_region(args.state, EmbeddingEngine.CHECK2HGI)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"[{args.state}] wrote → {out}")


if __name__ == "__main__":
    main()
