"""The Delaunay place graph — HGI's spatial scaffolding, rebuilt here.

Both substrates consume this and neither could produce it: `spatial.load_delaunay` reads
`pois.csv` + `edges.csv` and the CLI took them as arguments. So a from-scratch build depended on an
artifact of the old HGI engine, which is the last thing standing between this package and "built
from the corpus".

This is HGI's *preprocess* phase only. An HGI training run is not on the v18 path.

## What it is

One row per place, then a Delaunay triangulation over the place coordinates, then every simplex edge
kept — no distance cutoff, no k-NN pruning. Edge weights combine a distance decay with a
cross-region discount, min-max normalised to [0, 1].

## The reproduced quirks, and the one that matters

Each is FAITHFUL: changing it changes every banked substrate, so each is reproduced deliberately and
named here rather than discovered later.

1. **The triangulation runs on raw (longitude, latitude) degrees treated as a Euclidean plane.** No
   projection. At Alabama's latitude a degree of longitude is ~0.83 of a degree of latitude, so the
   triangulation is mildly anisotropic relative to true geography.

2. **`qhull_options="QJ QbB Pp"`.** `QbB` rescales each coordinate independently into the unit box —
   which cancels most of quirk 1, by accident rather than design. `QJ` joggles the input, because
   real corpora contain exactly-coincident places; it makes the triangulation input-order dependent
   in the degenerate cases.

3. ⚠ **A UNIT MISMATCH THAT INVERTS THE CROSS-REGION PENALTY.** The weight is
   `log((1 + D**1.5) / (1 + dist**1.5))` where `D` is the bounding-box diagonal in **degrees**
   (Alabama: 5.887) and `dist` is the haversine in **metres** (typically 10³–10⁵). The ratio is
   therefore far below 1 and the log is **negative for 98.56 % of edges**. Multiplying a negative
   number by the cross-region discount `w_r = 0.7` makes it *larger*, so the intended penalty for
   crossing a region boundary is a **bonus**.

   Reproduced, not fixed. Every banked substrate at every state was trained on these weights, so
   correcting the units would silently redefine the graph and make every banked number
   unreproducible. `fix_unit_mismatch=True` exists for a declared ablation and is off by default.

4. **`source`/`target` are 0-based positional row indices into `pois.csv`** — not place ids, and not
   substrate place indices. The consumer does the two-hop remap.

## The two defects that are NOT reproduced

- Places falling outside every tract polygon are dropped by an inner join, silently and uncounted.
  Here they are counted and logged: a state that loses 10 % of its places to a wrong shapefile
  should say so at build time, not be discovered by a downstream shape mismatch.
- A place intersecting two tract polygons yields TWO rows in the reference, so it appears twice in
  `pois.csv` and gets two independent Delaunay vertices. Here the place table is one row per
  `placeid` by construction (`groupby`), so the duplicate cannot arise — the same resolution
  `regions.py` reaches, one layer earlier.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

#: The cross-region discount. 0.7 at every state in the reference's own driver.
DEFAULT_CROSS_REGION_WEIGHT = 0.7

#: WGS84 semi-major axis, which is what the reference's haversine uses — not the mean radius.
EARTH_RADIUS_M = 6378137.0

#: `log((1 + D**p) / (1 + dist**p))`. See quirk 3 for what the units do to it.
DISTANCE_DECAY_POWER = 1.5

#: Joggle, rescale each axis to the unit box, and print precision. Reproduced verbatim: `QJ` is
#: load-bearing because real corpora contain coincident places and Qhull refuses them otherwise.
QHULL_OPTIONS = "QJ QbB Pp"


@dataclass(frozen=True)
class DelaunayGraph:
    """One state's place graph, as the two CSVs the consumer expects."""

    places: pd.DataFrame        # placeid, category, fclass — row order IS the vertex index
    edges: pd.DataFrame         # source, target, weight — positional indices into `places`
    dropped_outside: int        # places matching no polygon

    def write(self, directory: Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.places.to_csv(directory / "pois.csv", index=False)
        self.edges.to_csv(directory / "edges.csv", index=False)
        logger.info("delaunay: %d places, %d edges -> %s",
                    len(self.places), len(self.edges), directory)


def haversine_m(lon1: np.ndarray, lat1: np.ndarray,
                lon2: np.ndarray, lat2: np.ndarray) -> np.ndarray:
    """Great-circle distance in metres, vectorised. Same constant as the reference."""
    lon1, lat1, lon2, lat2 = (np.radians(np.asarray(v, dtype=np.float64))
                              for v in (lon1, lat1, lon2, lat2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return EARTH_RADIUS_M * 2 * np.arcsin(np.sqrt(a))


def place_table(corpus: pd.DataFrame) -> pd.DataFrame:
    """One row per place: modal category and fclass, MEAN coordinates.

    The mean matters and is not obviously right — `regions.py` reproduces the reference's *other*
    convention, where a place takes its FIRST check-in's coordinates. Both exist in the reference,
    for different artifacts, and they disagree for any place whose check-ins are not coincident. The
    hierarchy uses first; the Delaunay uses mean. Reproduced as-is.

    The category dropna happens BEFORE the aggregation, so a check-in without a category never
    contributes to its place's mean position.
    """
    if "fclass" not in corpus.columns:
        # NEVER substitute `category`. It has 7 symbols where fclass has 284, and 284 is the entire
        # vocabulary of the POI2Vec code book this table feeds — the substitution would produce a
        # plausible artifact that silently trains a 7-symbol code book. The column is `spot` in the
        # corpus; `corpus.load` carries it when present.
        raise ValueError(
            "the place table needs an `fclass` column (the OSM venue class, `spot` in the corpus). "
            "Substituting `category` would build a 7-symbol code book where the reference has 284.")

    frame = corpus.dropna(subset=["category"])
    modal = lambda s: (m.iloc[0] if not (m := s.mode()).empty else s.iloc[0])
    grouped = frame.groupby("placeid", sort=True).agg(
        category=("category", modal),
        fclass=("fclass", modal),
        longitude=("longitude", "mean"),
        latitude=("latitude", "mean"),
    ).reset_index()
    grouped = grouped.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)

    # Encoded AFTER the dedup, over the modal values — which is where the reference fits its
    # LabelEncoder. Fitting over all check-ins instead can enlarge the vocabulary (a class that is
    # never any place's mode still gets a code) and permutes every code, so a table built that way
    # would not line up with the reference's at all.
    for column in ("category", "fclass"):
        # `pd.api.types`, NÃO `np.issubdtype`. No pandas 3 uma coluna de texto infere `StringDtype`,
        # um dtype de EXTENSÃO, e `np.issubdtype` só aceita dtype numpy — ele levanta
        # `TypeError: Cannot interpret '<StringDtype...>' as a data type` em vez de devolver False.
        # Sob pandas 2 a mesma coluna vinha como `object` e a chamada funcionava, então o defeito
        # ficou latente até o lock subir para 3.0.5 e travou o build de substrato inteiro — o
        # caminho default, o que computa o grafo do corpus.
        if not pd.api.types.is_integer_dtype(grouped[column].dtype):
            grouped[column] = pd.factorize(grouped[column], sort=True)[0]
    return grouped


def build(corpus: pd.DataFrame, place_regions: pd.Series, *,
          cross_region_weight: float = DEFAULT_CROSS_REGION_WEIGHT,
          fix_unit_mismatch: bool = False) -> DelaunayGraph:
    """The place graph. `place_regions` maps place id -> region id, for the cross-region test.

    `fix_unit_mismatch=True` converts the bounding-box diagonal to metres so the decay behaves as
    intended and the cross-region discount is a penalty rather than a bonus. It is OFF by default
    and every banked substrate was built with it off — see quirk 3.
    """
    from scipy.spatial import Delaunay

    places = place_table(corpus)
    before = len(places)
    places = places[place_regions.reindex(places["placeid"]).notna().to_numpy()]
    places = places.reset_index(drop=True)
    dropped_outside = before - len(places)
    if dropped_outside:
        logger.warning("delaunay: %d of %d places match no region and are dropped — the reference "
                       "drops them silently, which hides a wrong shapefile until a shape mismatch "
                       "downstream", dropped_outside, before)
    if len(places) < 4:
        raise ValueError(f"a Delaunay triangulation needs at least 4 places; got {len(places)}")

    region_of = place_regions.reindex(places["placeid"]).to_numpy()
    points = places[["longitude", "latitude"]].to_numpy(dtype=np.float64)

    minx, miny = points.min(axis=0)
    maxx, maxy = points.max(axis=0)
    diagonal = float(np.hypot(maxx - minx, maxy - miny))       # DEGREES — see quirk 3
    if fix_unit_mismatch:
        diagonal = float(haversine_m(minx, miny, maxx, maxy))

    simplices = Delaunay(points, qhull_options=QHULL_OPTIONS).simplices
    # Every simplex edge, deduplicated as UNDIRECTED, keeping the FIRST occurrence's ORIENTATION.
    #
    # Two things here are load-bearing and both were got wrong once.
    #
    # 1. Do NOT canonicalise to low->high. `poi2vec` walks this graph DIRECTED, so an all-low->high
    #    edge list is a DAG. Measured at Alabama, canonical orientation raises absorbed walk steps
    #    from 61.4% to 78.9% and drops distinct nodes per walk from 4.47 to 2.87 — a different
    #    co-occurrence distribution, hence a different code book. The banked edges.csv is 49.7%
    #    high->low.
    # 2. The SCAN ORDER decides which occurrence is first, so it decides every edge's orientation.
    #    The reference scans row-major — `for simplex in triangles: for x, y in combinations(...)`,
    #    i.e. simplex 0's three pairs, then simplex 1's — so the pairs are interleaved here to match.
    #    An earlier version concatenated column BLOCKS (every (0,1) pair, then every (0,2)), which
    #    reproduced the orientation *distribution* but not the per-edge orientation: 2,3 % of
    #    Alabama's edges pointed the other way.
    pairs = np.stack([simplices[:, [0, 1]], simplices[:, [0, 2]], simplices[:, [1, 2]]],
                     axis=1).reshape(-1, 2)
    # The reference has no such filter — `combinations` over a degenerate simplex would emit a
    # self-pair and it would survive. `QJ` joggles coincident points precisely so that cannot
    # happen, so this is a guard, and it must stay BEFORE the dedup or it would change which
    # occurrence is first.
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    _, first = np.unique(np.sort(pairs, axis=1), axis=0, return_index=True)
    pairs = pairs[np.sort(first)]

    source, target = pairs[:, 0], pairs[:, 1]
    distance = haversine_m(points[source, 0], points[source, 1],
                           points[target, 0], points[target, 1])
    decay = np.log((1 + diagonal ** DISTANCE_DECAY_POWER)
                   / (1 + distance ** DISTANCE_DECAY_POWER))
    same_region = region_of[source] == region_of[target]
    weight = decay * np.where(same_region, 1.0, cross_region_weight)

    span = weight.max() - weight.min()
    weight = (weight - weight.min()) / span if span > 0 else np.zeros_like(weight)

    if not fix_unit_mismatch:
        negative = float((decay < 0).mean())
        logger.info("delaunay: %.2f%% of edges have a NEGATIVE distance term, so the cross-region "
                    "discount raises their weight instead of lowering it (reproduced defect)",
                    negative * 100)

    return DelaunayGraph(
        places=places[["placeid", "category", "fclass"]],
        edges=pd.DataFrame({"source": source.astype(np.int64),
                            "target": target.astype(np.int64),
                            "weight": weight.astype(np.float64)}),
        dropped_outside=dropped_outside,
    )


__all__ = ["DelaunayGraph", "build", "place_table", "haversine_m",
           "DEFAULT_CROSS_REGION_WEIGHT", "EARTH_RADIUS_M", "QHULL_OPTIONS"]
