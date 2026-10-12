"""E10 — the substrate graph, checked against the audited v18 build, without a GPU.

The reference study recorded the edge count of every state's graph before and after the forward-only
filter (`docs/studies/closing_data/v18/AUDIT.md`). Those numbers are a complete fingerprint of the
preprocessing chain up to the encoder: they depend on how check-ins are loaded, which rows survive
the region join, how they are sorted, and how consecutive-visit pairs are enumerated. If they match,
every deterministic step before training agrees with the build that produced the banked numbers.

This is the cheapest high-value equivalence test in the suite: no GPU, no substrate artifact, no
training. It needs only the raw corpus.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from mtlcheck import paths
from mtlcheck.substrate import corpus as corpus_mod
from mtlcheck.substrate import graph as graph_mod

from ._old_repo import OLD_REPO

# docs/studies/closing_data/v18/AUDIT.md — "backward edges dropped: <before> -> <after>"
AUDITED = {
    "alabama":    (219_976,   109_988),
    "arizona":    (457_162,   228_581),
    "istanbul":   (881_336,   440_668),
    "florida":    (2_771_964, 1_385_982),
    "california": (6_268_580, 3_134_290),
    "texas":      (8_102_496, 4_051_248),
}


def _corpus_or_skip(state: str):
    path = paths.state_checkins(state)
    if not path.exists():
        pytest.skip(f"raw corpus not present locally: {path}")
    return corpus_mod.load(state)


# The region spatial join is a FILTER, and whether it removes anything is a property of the corpus,
# not of the code. At the five US states it is a no-op — the corpora were segregated by the same
# census tracts they are later joined against, so every POI already falls inside one. At Istanbul it
# is not: `data/massive_steps_istanbul/graph_report.json` records 81 856 of 544 471 check-ins dropped
# for falling outside every mahalle (544 471 - 81 856 = 462 615 in graph, 520 regions with POIs out
# of 972 polygons). Until `substrate/regions.py` applies that join, the Istanbul edge count is over
# by an amount BOUNDED BY that population.
#
# Open residual, not explained by the drop: the two reference sources disagree with each other.
# graph_report records `num_edges: 877 842` (= 438 921 forward) while AUDIT.md records 881 336 ->
# 440 668 — a difference of 1 747 forward edges. They describe different builds (graph_report comes
# from an older admin-mode worktree), so the audited count is the one to reproduce, but the
# discrepancy is logged rather than absorbed.
NEEDS_REGION_JOIN = {"istanbul"}


@pytest.mark.equivalence
@pytest.mark.parametrize("state", sorted(AUDITED))
def test_forward_edge_count_matches_audit(state: str, request) -> None:
    """The forward-only graph has exactly the audited number of edges."""
    if state in NEEDS_REGION_JOIN:
        request.node.add_marker(pytest.mark.xfail(
            reason="region join not implemented yet; Istanbul drops 81 856 check-ins there",
            strict=True,
        ))
    corpus = _corpus_or_skip(state)
    g = graph_mod.build(corpus, forward_only=True)
    before, after = AUDITED[state]

    assert g.n_edges == after, (
        f"{state}: built {g.n_edges} forward edges, audit says {after} "
        f"(delta {g.n_edges - after:+d}). A positive delta usually means rows the reference dropped "
        f"in the region spatial join survived here; a negative one means the opposite."
    )
    assert g.edges_before_filter == before
    assert g.dropped_backward == before - after


@pytest.mark.equivalence
@pytest.mark.parametrize("state", sorted(AUDITED))
def test_forward_is_exactly_half(state: str) -> None:
    """The invariant that holds at every state: the filter removes exactly one direction.

    Stronger than the per-state constants because it needs no audit table — every consecutive-visit
    edge is emitted in both directions, so forward-only must halve the set, with no self-loops
    surviving (a self-loop would satisfy neither src<tgt nor src>tgt and would break the identity).
    """
    corpus = _corpus_or_skip(state)
    bidirectional = graph_mod.build(corpus, forward_only=False)
    forward = graph_mod.build(corpus, forward_only=True)

    assert bidirectional.n_edges == 2 * forward.n_edges
    assert (forward.edge_index[0] < forward.edge_index[1]).all(), "a forward edge points backwards"
    assert (bidirectional.edge_index[0] != bidirectional.edge_index[1]).all(), "self-loop present"


@pytest.mark.equivalence
def test_istanbul_gap_is_exactly_the_region_drop() -> None:
    """The one state that fails E10 fails by the recorded amount, not by an unexplained one.

    This is the difference between "the region join is missing" and "something is wrong with the
    graph builder". It pins the gap to the drop count the corpus's own build report recorded, so if
    the two ever stop agreeing, that is a new finding rather than a known gap.
    """
    corpus = _corpus_or_skip("istanbul")
    built = graph_mod.build(corpus, forward_only=True).n_edges
    _, audited = AUDITED["istanbul"]

    # graph_report.json: n_rows 544 471 raw, n_checkins_dropped 81 856, 462 615 in graph.
    assert corpus.n_checkins == 544_471, "the raw Istanbul corpus changed"
    assert corpus.n_users == 23_700

    excess = built - audited
    dropped = 81_856
    # 80,103 edges against 81,856 dropped check-ins — a shortfall of 1,753, which is what a bound
    # rather than an identity predicts: a dropped check-in at the start or end of a user's history,
    # or several consecutive drops, removes fewer than one edge each. The gap is CONSISTENT WITH the
    # drop count, not equal to it.
    assert 0 < excess <= dropped, (
        f"Istanbul excess {excess} is not bounded by the {dropped} region-dropped check-ins"
    )
    assert excess == 80_103, "the excess moved; re-derive before assuming the same explanation"


@pytest.mark.equivalence
@pytest.mark.parametrize("state", sorted(AUDITED))
def test_edge_count_is_derivable_without_building(state: str) -> None:
    """`n_checkins - n_users_with_two_or_more_visits`, straight from the corpus."""
    corpus = _corpus_or_skip(state)
    predicted = graph_mod.expected_forward_edges(corpus.frame)
    assert predicted == graph_mod.build(corpus, forward_only=True).n_edges


@pytest.mark.equivalence
@pytest.mark.artifacts
def test_edge_weights_match_the_frozen_graph() -> None:
    """Edge VALUES, not just counts — the assertion that was missing.

    The suite pinned edge counts and feature layouts and passed with a temporal-decay constant that
    was wrong by a factor of 24, because a decay constant cannot change how many edges exist. Counts
    are a fingerprint of the row space; they say nothing about the weights the encoder consumes.

    The frozen graph the v18 substrate was built from is on disk locally, so this is checkable
    without a GPU and without rebuilding anything.
    """
    import pickle

    frozen_path = (OLD_REPO / "output" / "check2hgi" /
                   "alabama" / "temp" / "checkin_graph.pt")
    if not frozen_path.exists():
        pytest.skip(f"frozen graph absent: {frozen_path}")

    corpus = _corpus_or_skip("alabama")
    built = graph_mod.build(corpus, forward_only=True)

    with open(frozen_path, "rb") as fh:
        frozen = pickle.load(fh)
    fi = np.asarray(frozen["edge_index"])
    fw = np.asarray(frozen["edge_weight"], dtype=np.float64)

    keep = fi[0] < fi[1]
    frozen_src, frozen_weight = fi[0][keep], fw[keep]

    assert len(frozen_weight) == built.n_edges, (
        f"frozen graph has {len(frozen_weight)} forward edges, built {built.n_edges}"
    )
    # Both edge lists are in ascending source order, so they align without a join.
    assert np.array_equal(np.sort(frozen_src), np.sort(built.edge_index[0]))

    order_frozen = np.argsort(frozen_src, kind="stable")
    order_built = np.argsort(built.edge_index[0], kind="stable")
    delta = np.abs(frozen_weight[order_frozen] - built.edge_weight[order_built].astype(np.float64))

    assert delta.max() < 1e-6, (
        f"edge weights diverge from the frozen graph by up to {delta.max():.3e} "
        f"(mean {delta.mean():.3e}). The decay constant or the normalisation differs."
    )


@pytest.mark.equivalence
@pytest.mark.artifacts
def test_low_weight_fraction_matches_the_reference_figure() -> None:
    """46.8% of Alabama's edges fall below weight 0.01 — a figure the reference cites about its own
    graph, and an independent check on the decay constant that needs no frozen artifact at all."""
    corpus = _corpus_or_skip("alabama")
    built = graph_mod.build(corpus, forward_only=False)
    fraction = float((built.edge_weight < 0.01).mean())
    assert 0.46 < fraction < 0.48, (
        f"{fraction:.4f} of edges are below weight 0.01; the reference reports 0.468 for this graph"
    )


@pytest.mark.equivalence
@pytest.mark.parametrize("state", ["alabama"])
def test_node_features_layout(state: str) -> None:
    """15 channels: 7 category one-hot + 4 cyclical + 4 elapsed-time."""
    from mtlcheck.substrate import features as feat_mod

    corpus = _corpus_or_skip(state)
    f = feat_mod.build(corpus, continuous_time=True)

    assert f.in_channels == 15, f"expected in_channels=15, got {f.in_channels}"
    assert f.layout == ("canonical_11", "continuous_time_4")
    assert len(f.columns) == 15

    onehot = f.matrix[:, : corpus.n_categories]
    assert (onehot.sum(axis=1) == 1.0).all(), "category one-hot is not one-hot"

    # Elapsed time is measured up to the visit itself: a user's first visit has no gap and no
    # elapsed time, and is flagged.
    gap_col, since_first_col, _, is_zero_col = (f.matrix[:, 11], f.matrix[:, 12],
                                                f.matrix[:, 13], f.matrix[:, 14])
    first_rows = corpus.frame.groupby("userid", sort=False).head(1).index.to_numpy()
    assert (gap_col[first_rows] == 0.0).all()
    assert (since_first_col[first_rows] == 0.0).all()
    assert (is_zero_col[first_rows] == 1.0).all()

    # Without the elapsed-time block it is the canonical eleven.
    bare = feat_mod.build(corpus, continuous_time=False)
    assert bare.in_channels == 11
