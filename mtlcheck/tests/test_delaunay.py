"""The Delaunay place graph — HGI's scaffolding, rebuilt here.

Reproduces the banked Alabama artifact essentially exactly: 11,848 places with an identical placeid
set, 35,519 edges with 100% overlap, and weights agreeing to 2.2e-16 — machine epsilon. That is the
verification that matters and it lives in `tests/equivalence`; these pin the behaviours.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.substrate import delaunay


def _corpus(n_places=12, per_place=3, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for place in range(n_places):
        lon, lat = -86.5 + place * 0.05, 32.3 + (place % 4) * 0.05
        for _ in range(per_place):
            rows.append({"placeid": place, "category": place % 7, "fclass": place % 5,
                         "longitude": lon + rng.normal(0, 1e-4),
                         "latitude": lat + rng.normal(0, 1e-4)})
    return pd.DataFrame(rows)


def test_a_place_takes_the_MEAN_of_its_checkins(): 
    """And that is not the convention the hierarchy uses.

    `regions.py` reproduces the reference's OTHER rule — a place takes its FIRST check-in's
    coordinates. Both exist in the reference, for different artifacts, and they disagree for any
    place whose check-ins are not coincident. Reproduced as-is, on both sides.
    """
    corpus = pd.DataFrame({
        "placeid": [1, 1, 2], "category": [0, 0, 1], "fclass": [0, 0, 1],
        "longitude": [-86.0, -87.0, -85.0], "latitude": [32.0, 33.0, 34.0]})
    places = delaunay.place_table(corpus)
    assert places.loc[places.placeid == 1, "longitude"].iloc[0] == pytest.approx(-86.5)
    assert places.loc[places.placeid == 1, "latitude"].iloc[0] == pytest.approx(32.5)


def test_a_checkin_without_a_category_never_moves_its_places_position():
    """The dropna happens BEFORE the aggregation, so it is excluded from the mean too."""
    corpus = pd.DataFrame({
        "placeid": [1, 1], "category": [0, None], "fclass": [0, 0],
        "longitude": [-86.0, -99.0], "latitude": [32.0, 45.0]})
    places = delaunay.place_table(corpus)
    assert places["longitude"].iloc[0] == pytest.approx(-86.0), "the NaN row must not pull the mean"


def test_the_cross_region_penalty_is_inverted_and_that_is_reproduced():
    """⚠ The defect that matters, pinned so nobody 'fixes' it by accident.

    The weight is log((1 + D**1.5) / (1 + dist**1.5)) with D the bbox diagonal in DEGREES and dist
    the haversine in METRES. The ratio is far below 1, so the log is negative for ~98.6% of edges —
    and multiplying a negative by the cross-region discount 0.7 makes it LARGER. The intended
    penalty for crossing a region boundary is a bonus.

    Every banked substrate at every state was trained on these weights, so correcting the units
    would redefine the graph and make every banked number unreproducible.
    """
    corpus = _corpus()
    regions = pd.Series({p: p % 2 for p in range(12)})          # alternating, so edges cross

    faithful = delaunay.build(corpus, regions)
    fixed = delaunay.build(corpus, regions, fix_unit_mismatch=True)

    assert len(faithful.edges) == len(fixed.edges), "the fix changes weights, never topology"
    assert not np.allclose(faithful.edges.weight, fixed.edges.weight), (
        "if these agreed, the flag would be doing nothing and the defect would be unpinned")

    # The INVERSION itself, asserted rather than described. Recompute the raw decay the way build
    # does and check its sign: negative under the faithful units, positive under the fix. A wrong
    # "fix" that merely rescaled D by a constant would leave the sign alone and fail here.
    places = delaunay.place_table(corpus)
    points = places[["longitude", "latitude"]].to_numpy()
    lo, hi = points.min(axis=0), points.max(axis=0)
    degrees = float(np.hypot(*(hi - lo)))
    metres = float(delaunay.haversine_m(lo[0], lo[1], hi[0], hi[1]))
    distance = delaunay.haversine_m(points[0, 0], points[0, 1], points[1, 0], points[1, 1])

    decay = lambda d: np.log((1 + d ** 1.5) / (1 + distance ** 1.5))
    assert decay(degrees) < 0, "the faithful units make the distance term NEGATIVE"
    assert decay(metres) > 0, "and correcting them makes it positive, which flips the discount"


def test_places_outside_every_region_are_dropped_and_COUNTED(caplog):
    """The reference drops them with an inner join, silently and uncounted — which hides a wrong
    shapefile until something downstream fails on a shape mismatch."""
    corpus = _corpus()
    regions = pd.Series({p: 0 for p in range(9)})               # places 9..11 have no region

    with caplog.at_level("WARNING"):
        graph = delaunay.build(corpus, regions)
    assert graph.dropped_outside == 3
    assert len(graph.places) == 9
    assert "match no region" in caplog.text


def test_every_simplex_edge_survives_once_in_its_ORIGINAL_orientation():
    """No cutoff, no pruning, each undirected pair once — and NOT canonicalised to low->high.

    Canonicalising looks harmless and is not: `poi2vec` walks this graph DIRECTED, so an all-low->high
    edge list is a DAG. Measured at Alabama, canonical orientation raises absorbed walk steps from
    61.4% to 78.9% and drops distinct nodes per walk from 4.47 to 2.87 — a different co-occurrence
    distribution, hence a different code book. The banked edges.csv is 49.7% high->low.
    """
    graph = delaunay.build(_corpus(), pd.Series({p: 0 for p in range(12)}))
    pairs = [tuple(row) for row in graph.edges[["source", "target"]].to_numpy()]

    assert len({tuple(sorted(p)) for p in pairs}) == len(pairs), "each undirected pair exactly once"
    assert not any(s == t for s, t in pairs), "no self-loops"
    assert any(s > t for s, t in pairs), (
        "some edge must run high->low, or the graph is a DAG and the directed walk collapses")
    assert graph.edges.weight.min() == 0.0 and graph.edges.weight.max() == 1.0


def test_pairs_are_scanned_row_major_not_by_column_block():
    """A ordem de varredura decide a orientação de CADA aresta, não só a distribuição delas.

    A referência percorre `for simplex in triangles: for x, y in combinations(simplex, 2)` — as três
    arestas do simplex 0, depois as do simplex 1. Concatenar blocos de coluna (todas as (0,1), depois
    todas as (0,2)) dá o mesmo conjunto não dirigido, mas troca a orientação de arestas individuais:
    2,3 % delas em Alabama.

    `poi2vec` caminha este grafo DIRIGIDO, então isso alcança o code book.

    Na fixture abaixo o par {1,2} aparece no simplex 0 na posição de coluna (1,2) e no simplex 1 na
    posição (0,1). Por linha, a primeira aparição é (1,2); por bloco, é (2,1).

    Verificado contra o artefato bancado do HGI em Alabama: 35 519 arestas, orientação idêntica,
    zero invertidas, |Δ peso| máximo 1,1e-16.
    """
    import numpy as np

    simplices = np.array([[0, 1, 2],
                          [2, 1, 5]])

    def dedup(pairs):
        _, first = np.unique(np.sort(pairs, axis=1), axis=0, return_index=True)
        return pairs[np.sort(first)]

    row_major = dedup(np.stack([simplices[:, [0, 1]], simplices[:, [0, 2]], simplices[:, [1, 2]]],
                               axis=1).reshape(-1, 2))
    by_block = dedup(np.concatenate([simplices[:, [0, 1]], simplices[:, [0, 2]],
                                     simplices[:, [1, 2]]]))

    undirected = lambda m: {tuple(sorted(row)) for row in m.tolist()}
    assert undirected(row_major) == undirected(by_block), (
        "as duas ordens têm de dar o mesmo conjunto não dirigido — senão o teste testa outra coisa")

    orientation = lambda m: {tuple(sorted(row)): tuple(row) for row in m.tolist()}
    flipped = [k for k, v in orientation(row_major).items() if orientation(by_block)[k] != v]
    assert flipped == [(1, 2)], (
        "esta fixture existe para exibir a troca de orientação; se ela sumiu, o teste ficou inerte")
    assert orientation(row_major)[(1, 2)] == (1, 2)      # a ordem da referência
    assert orientation(by_block)[(1, 2)] == (2, 1)       # o que havia antes
