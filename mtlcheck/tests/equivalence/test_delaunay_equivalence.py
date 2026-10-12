"""E12 — the Delaunay place graph against the banked HGI artifact.

The verification that matters for this component. Measured at Alabama, the only state whose HGI
artifacts are on this machine: identical place set, identical edge set, and weights agreeing to
2.2e-16. The reimplementation is vectorised where the reference used a Python loop with a `seen`
set, and the ordering that loop produced is not observable — the consumer re-emits both directions.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ._old_repo import OLD_REPO

REFERENCE = OLD_REPO
HGI = REFERENCE / "output" / "hgi" / "alabama" / "temp"
GRAPH = REFERENCE / "output" / "check2hgi" / "alabama" / "temp" / "checkin_graph.pt"

pytestmark = [pytest.mark.equivalence, pytest.mark.artifacts]


def _undirected(edges: pd.DataFrame, places: pd.DataFrame) -> dict:
    """Edges keyed by PLACEID pair, so the two row-index conventions cannot confound the check."""
    pid = places["placeid"].to_numpy()
    keys = np.sort(np.stack([pid[edges["source"]], pid[edges["target"]]], axis=1), axis=1)
    return dict(zip(map(tuple, keys), edges["weight"].to_numpy()))


@pytest.mark.skipif(not (HGI / "pois.csv").exists() or not GRAPH.exists(),
                    reason="the banked HGI artifacts are not on this machine")
def test_e12_the_place_graph_reproduces_the_banked_artifact() -> None:
    from mtlcheck.substrate import corpus as corpus_mod, delaunay

    banked_places = pd.read_csv(HGI / "pois.csv")
    banked_edges = pd.read_csv(HGI / "edges.csv")

    with open(GRAPH, "rb") as fh:
        graph = pickle.load(fh)
    poi_to_region = np.asarray(graph["poi_to_region"], dtype=np.int64)
    place_regions = pd.Series({int(pid): int(poi_to_region[int(i)])
                               for pid, i in graph["placeid_to_idx"].items()})

    corpus = corpus_mod.load("alabama")
    assert corpus.has_fclass, "the corpus must carry `spot`; without it the builder now refuses"
    ours = delaunay.build(corpus.frame.rename(columns={"spot": "fclass"}), place_regions)

    # All THREE columns, not just placeid. The category and fclass codes were never compared, and
    # they were wrong: the builder substituted category for fclass, so it wrote 7 symbols where the
    # reference has 284 — the entire vocabulary of the code book this table feeds.
    mine = ours.places.sort_values("placeid").reset_index(drop=True)
    theirs = banked_places.sort_values("placeid").reset_index(drop=True)
    assert len(mine) == len(theirs) == 11848
    for column in ("placeid", "category", "fclass"):
        assert np.array_equal(mine[column].to_numpy(), theirs[column].to_numpy()), (
            f"pois.csv column {column!r} differs")
    assert mine["fclass"].nunique() == 284

    mine_edges = _undirected(ours.edges, ours.places)
    their_edges = _undirected(banked_edges, banked_places)
    assert len(mine_edges) == len(their_edges) == 35519
    assert set(mine_edges) == set(their_edges), "the edge SET must match, whatever the row order"

    difference = max(abs(mine_edges[k] - their_edges[k]) for k in their_edges)
    assert difference < 1e-12, f"weights differ by {difference:.3e}; expected machine epsilon"

    # ORIENTATION, which the undirected comparison above cannot see and `poi2vec` walks directed.
    # Canonicalising to low->high would make this a DAG; the banked file is 49.7% high->low.
    high_to_low = float((ours.edges["source"] > ours.edges["target"]).mean())
    banked_high_to_low = float((banked_edges["source"] > banked_edges["target"]).mean())
    assert abs(high_to_low - banked_high_to_low) < 0.02, (
        f"orientation {high_to_low:.3f} against the reference's {banked_high_to_low:.3f}")
