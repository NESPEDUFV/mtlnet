"""Safely regenerate the missing checkin_graph.pt for CA/TX (cleaned temp dirs),
then VERIFY the region sequence row-aligns with next_region.parquet's
last_region_idx. preprocess_check2hgi writes ONLY graph .pt files (no parquet /
embeddings), and poi->region is a deterministic spatial join → safe restore.

  PYTHONPATH=src:research .venv/bin/python scripts/mtl_improvement/t21_regen_catx_graph.py
"""
import sys, shutil
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src")); sys.path.insert(0, str(REPO / "research"))
import numpy as np, pandas as pd

from configs.paths import IoPaths, EmbeddingEngine
from embeddings.check2hgi.preprocess import preprocess_check2hgi
from data.inputs.region_sequence import build_region_sequence_tensor

SHP = {
    "California": "data/miscellaneous/tl_2022_06_tract_CA/tl_2022_06_tract.shp",
    "Texas": "data/miscellaneous/tl_2022_48_tract_TX/tl_2022_48_tract.shp",
}


def regen(city: str) -> bool:
    slug = city.lower()
    gpath = IoPaths.CHECK2HGI.get_graph_data_file(city)
    tempdir = gpath.parent
    # back up the existing temp dir
    bak = tempdir.parent / "temp_backup_pre_regen"
    if not bak.exists():
        shutil.copytree(tempdir, bak)
        print(f"[{city}] backed up {tempdir} -> {bak}")
    before = {p.name: p.stat().st_mtime for p in tempdir.glob("*")}
    print(f"[{city}] running preprocess_check2hgi (graph-only)...")
    preprocess_check2hgi(city, SHP[city], edge_type="user_sequence")
    after = {p.name: p.stat().st_mtime for p in tempdir.glob("*")}
    changed = [n for n in after if n not in before or after[n] != before.get(n)]
    print(f"[{city}] files added/changed: {changed}")
    # SAFETY: only graph .pt files may have changed; parquet must be untouched
    bad = [n for n in changed if n.endswith(".parquet")]
    if bad:
        print(f"[{city}] !! parquet changed ({bad}) — RESTORING backup, ABORT")
        shutil.rmtree(tempdir); shutil.copytree(bak, tempdir)
        return False
    if not gpath.exists():
        print(f"[{city}] !! checkin_graph.pt still missing — ABORT"); return False
    # VERIFY alignment: built region seq's last non-pad step == last_region_idx
    seq = build_region_sequence_tensor(city).numpy()  # [N,9,64] region embeddings
    nr = pd.read_parquet(IoPaths.CHECK2HGI.get_state_dir(city) / "input" / "next_region.parquet")
    # region embedding table to map emb-vector -> region id (via nearest/exact)
    from data.inputs.region_sequence import _load_region_embeddings, _load_graph_maps
    reg_emb = _load_region_embeddings(city)  # [n_regions, D]
    # last non-pad step per row
    pad = (np.abs(seq).sum(-1) == 0)  # [N,9]
    last_idx = (~pad).cumsum(1).argmax(1)
    last_vec = seq[np.arange(len(seq)), last_idx]  # [N,64]
    # match last_vec to region id by exact row in reg_emb
    # build a lookup from emb-tuple to region id
    from scipy.spatial import cKDTree
    tree = cKDTree(reg_emb)
    _, built_region = tree.query(last_vec, k=1)
    lr = nr["last_region_idx"].to_numpy()
    valid = lr >= 0
    agree = (built_region[valid] == lr[valid]).mean()
    print(f"[{city}] region-seq vs next_region.last_region_idx agreement: {agree*100:.2f}% (n={valid.sum()})")
    ok = agree > 0.98
    print(f"[{city}] {'ALIGNED ✓' if ok else 'MISALIGNED ✗'}")
    return ok


if __name__ == "__main__":
    cities = sys.argv[1:] or ["California", "Texas"]
    results = {c: regen(c) for c in cities}
    print("\n=== SUMMARY ===")
    for c, ok in results.items():
        print(f"  {c}: {'OK (graph restored + aligned)' if ok else 'FAILED/MISALIGNED'}")
    sys.exit(0 if all(results.values()) else 1)
