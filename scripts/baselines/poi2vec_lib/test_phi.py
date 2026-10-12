#!/usr/bin/env python
"""Unit test for the FIXED midpoint tree + OVERLAP-AREA phi (POI2Vec mechanisms #1, #2).

Hand-built 2x2 grid: bbox = [0,0,2,2], theta = 1.0 -> the midpoint tree splits lon@0
(depth 0) into [0,1)x and [1,2)x, then lat@1 into two halves each -> exactly 4 unit
leaf cells (a 2x2 grid). We then assert:

  (A) sum(phi) == 1 per POI (atol 1e-6),
  (B) a POI CENTERED inside one cell (e.g. (0.5,0.5)) gets phi == [1.0] on that one leaf,
  (C) a POI on the CENTER CROSS (2.0,2.0 corner of all 4 cells -> (1.0,1.0)) routes to
      2-4 cells with AREA-PROPORTIONAL weights (equal quarters -> 0.25 each).

Run: PYTHONPATH=src .venv/bin/python scripts/baselines/poi2vec_lib/test_phi.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from poi2vec_lib import build_midpoint_tree, build_poi_routes  # noqa: E402


def main():
    bbox = (0.0, 0.0, 2.0, 2.0)
    theta = 1.0
    tree = build_midpoint_tree(bbox, theta=theta, even_axis=0)
    print(f"tree: n_internal={tree.n_internal} n_leaf={tree.n_leaf} "
          f"theta={tree.theta}")
    print("leaf rects (lon0,lat0,lon1,lat1):")
    for j, r in enumerate(tree.leaf_rects):
        print(f"  leaf {j}: {tuple(round(float(v),3) for v in r)}  "
              f"path_nodes={tree.leaf_path_nodes[j].tolist()} "
              f"dirs={tree.leaf_path_dirs[j].astype(int).tolist()}")
    assert tree.n_leaf == 4, f"expected 4 leaves, got {tree.n_leaf}"
    assert tree.n_internal == 3, f"expected 3 internal (1 lon + 2 lat), got {tree.n_internal}"

    # POIs:
    #  P0 centered in bottom-left cell  (0.5,0.5) -> single leaf, phi=[1.0]
    #  P1 centered in top-right cell     (1.5,1.5) -> single leaf, phi=[1.0]
    #  P2 on the center cross            (1.0,1.0) -> 4 cells, equal phi (theta box
    #     [0.5,0.5,1.5,1.5] overlaps each unit cell in a 0.5x0.5 quarter)
    #  P3 on a lon split line, mid-lat   (1.0,0.5) -> 2 cells (left+right of bottom),
    #     equal phi (box [0.5,0,1.5,1] -> 0.5x1 each)
    poi_xy = np.array([
        [0.5, 0.5],
        [1.5, 1.5],
        [1.0, 1.0],
        [1.0, 0.5],
    ], dtype=np.float64)
    routes = build_poi_routes(poi_xy, tree, theta=theta, route_count=4)

    ok = True
    for i, (leaf_ids, phi) in enumerate(routes):
        s = float(phi.sum())
        print(f"P{i} xy={poi_xy[i].tolist()} -> leaves={leaf_ids.tolist()} "
              f"phi={[round(float(p),4) for p in phi]} sum={s:.6f}")
        # (A) sum(phi)==1
        assert abs(s - 1.0) <= 1e-6, f"P{i} sum(phi)={s} != 1"

    # (B) centered POIs -> single leaf, phi=1
    assert len(routes[0][0]) == 1 and abs(float(routes[0][1][0]) - 1.0) <= 1e-6, \
        "P0 (centered) must route to exactly 1 leaf with phi=1"
    assert len(routes[1][0]) == 1 and abs(float(routes[1][1][0]) - 1.0) <= 1e-6, \
        "P1 (centered) must route to exactly 1 leaf with phi=1"

    # (C) center cross -> 4 cells, equal area-proportional weights (0.25 each)
    assert len(routes[2][0]) == 4, f"P2 (cross) must route to 4 leaves, got {len(routes[2][0])}"
    assert np.allclose(routes[2][1], 0.25, atol=1e-6), \
        f"P2 (cross) phi must be 0.25 each, got {routes[2][1].tolist()}"

    # P3 on a lon split, mid-lat -> 2 cells, equal weights (0.5 each)
    assert len(routes[3][0]) == 2, f"P3 must route to 2 leaves, got {len(routes[3][0])}"
    assert np.allclose(routes[3][1], 0.5, atol=1e-6), \
        f"P3 phi must be 0.5 each, got {routes[3][1].tolist()}"

    print("\nPHI UNIT TEST: ALL ASSERTIONS PASS")


if __name__ == "__main__":
    main()
