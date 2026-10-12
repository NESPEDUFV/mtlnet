"""The guards on the layer-1 → layer-2 seam, tested by trying to get past them.

A substrate directory is consumed by dozens of cells that never see how it was made, so a wrong one
does not fail — it produces a number. Two failure modes are worth a hard stop:

* a **bidirectional** graph, where the one-shot readout convolves each history visit over its own
  future and writes the window's target into its features (28.63 macro-F1 points of leak, which
  reads as a spectacular substrate improvement);
* a **misaligned corpus**, where the embeddings come from one visit and the labels from another
  while every shape stays valid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch

from mtlcheck.config import SubstrateConfig
from mtlcheck.substrate import export, graph as graph_mod
from mtlcheck.substrate.training import SubstrateRun


def _frame(n: int = 40) -> pd.DataFrame:
    return pd.DataFrame({
        "userid": np.repeat(np.arange(max(n // 20, 1)), 20)[:n],
        "placeid": 100 + np.arange(n) % 15,
        "category": [f"c{i % 3}" for i in range(n)],
        "datetime": pd.date_range("2020-01-01", periods=n, freq="h"),
    })


def _corpus(n: int = 40):
    """`graph.build` consumes a Corpus, not a frame — it needs the category encoding too."""
    from mtlcheck.substrate.corpus import Corpus

    frame = _frame(n)
    vocab = tuple(sorted(frame["category"].unique()))
    codes = frame["category"].map({c: i for i, c in enumerate(vocab)}).to_numpy(dtype=np.int64)
    return Corpus(frame=frame, category_codes=codes, category_vocab=vocab)


def _run(n: int, dim: int = 64) -> SubstrateRun:
    return SubstrateRun(
        checkin=torch.zeros(n, dim), place=torch.zeros(15, dim), region=torch.zeros(4, dim),
        state_dict={}, best_epoch=1, best_loss=0.1, losses=[0.1], seconds=1.0, n_params=10,
        hard_negatives=True, peak_memory_bytes=None, deterministic=True,
        deterministic_achieved=True, seed=42, nondeterministic_ops=[],
        init_fingerprint="deadbeef",
    )


def _write(tmp_path, frame, graph):
    return export.write(
        tmp_path / "out", _run(len(frame)), frame, state="alabama",
        config=SubstrateConfig(engine="test"),
        place_to_index={int(p): i for i, p in enumerate(sorted(frame["placeid"].unique()))},
        poi_to_region=np.zeros(15, dtype=np.int64), graph=graph)


def test_a_bidirectional_graph_is_refused(tmp_path) -> None:
    """The guard must read the EDGES, not a caller's label.

    Its first version read a dict the caller assembled, so the entire leak class rested on that dict
    being honest. Here the graph is *labelled* forward-only and is not.
    """
    corpus = _corpus()
    honest = graph_mod.build(corpus, forward_only=False)
    lying = graph_mod.CheckinGraph(
        edge_index=honest.edge_index, edge_weight=honest.edge_weight, n_nodes=honest.n_nodes,
        forward_only=True,                      # the label says forward-only; the edges disagree
        edges_before_filter=honest.edges_before_filter)

    with pytest.raises(ValueError, match="forward in time"):
        _write(tmp_path, corpus.frame, lying)


def test_a_graph_whose_flag_contradicts_its_edges_is_refused(tmp_path) -> None:
    """The mirror case: forward-only edges carrying a False flag. One of the two is wrong."""
    corpus = _corpus()
    honest = graph_mod.build(corpus, forward_only=True)
    confused = graph_mod.CheckinGraph(
        edge_index=honest.edge_index, edge_weight=honest.edge_weight, n_nodes=honest.n_nodes,
        forward_only=False, edges_before_filter=honest.edges_before_filter)

    with pytest.raises(ValueError, match="flag and the data disagree"):
        _write(tmp_path, corpus.frame, confused)


def test_a_corpus_of_the_wrong_length_is_refused(tmp_path) -> None:
    corpus = _corpus()
    good = graph_mod.build(corpus, forward_only=True)
    with pytest.raises(ValueError, match="check-ins and the graph"):
        _write(tmp_path, corpus.frame.head(len(corpus.frame) - 1), good)


def test_a_forward_only_build_is_written(tmp_path) -> None:
    """The guards must not refuse the case they exist to allow."""
    corpus = _corpus()
    manifest = _write(tmp_path, corpus.frame, graph_mod.build(corpus, forward_only=True))

    assert manifest["graph"]["forward_only"] is True
    assert (tmp_path / "out" / "input" / "next.parquet").exists()
    assert (tmp_path / "out" / "manifest.json").exists()
    assert manifest["training"]["seed"] == 42
    assert manifest["training"]["init_fingerprint"] == "deadbeef"
