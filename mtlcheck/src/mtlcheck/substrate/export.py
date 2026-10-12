"""Write a substrate to disk in the layout the training layer reads.

A substrate directory is the contract between layer 1 and layer 2. It holds the three embedding
levels, the two input tables, the alignment witness, and a manifest saying how it was made:

    <engine>/<state>/
    ├── embeddings.parquet          check-in level: userid, placeid, category, datetime + 64 dims
    ├── poi_embeddings.parquet      place level
    ├── region_embeddings.parquet   region level — what the region tower reads
    ├── input/next.parquet          576 columns + userid + next_category
    ├── input/next_region.parquet   the region labels
    ├── temp/sequences_next.parquet the windows in place ids
    └── manifest.json               recipe, seed, loss, timings, and the S17/R16 switches

The manifest is not decoration. Every question this rewrite had to answer by re-running something —
was this built forward-only, were hard negatives on, which epoch was selected, was it deterministic —
is a field here. The reference's provenance file was the one artifact that made the capacity-audit
defect findable, so this keeps that idea and extends it.

The check-in export is a **one-shot full-graph readout**. That is only equivalent to encoding each
window's own prefix because the graph is forward-only: a visit's neighbourhood contains nothing after
it, so encoding the whole corpus at once gives each visit the same vector it would get from its
prefix alone. The reference verified exactly this on Alabama at max 2.4e-06 over all 96 326 windows.
Under a bidirectional graph the two would differ and this export would be wrong.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..config import DataConfig, SubstrateConfig
from .graph import CheckinGraph
from ..data import materialize, sequences
from .training import SubstrateRun

logger = logging.getLogger(__name__)


def write(directory: Path, run: SubstrateRun, corpus: pd.DataFrame, *,
          state: str, config: SubstrateConfig, place_to_index: dict,
          poi_to_region: np.ndarray, graph: CheckinGraph,
          data_config: DataConfig | None = None) -> dict[str, Any]:
    """Materialise a finished build. Returns the manifest it wrote."""
    directory = Path(directory)
    _refuse_leaky_export(graph)
    _refuse_misaligned_corpus(corpus, graph)
    (directory / "input").mkdir(parents=True, exist_ok=True)
    (directory / "temp").mkdir(parents=True, exist_ok=True)

    checkin = run.checkin.numpy()
    if len(checkin) != len(corpus):
        raise ValueError(f"{len(checkin)} check-in vectors for {len(corpus)} check-ins")

    _write_levels(directory, run, corpus, checkin)

    data_config = data_config or DataConfig()
    windows = sequences.build_from(corpus, data_config)
    categories = corpus["category"].to_numpy()

    next_frame = materialize.next_table(windows, checkin, categories)
    next_frame.to_parquet(directory / "input" / "next.parquet", index=False)

    region_frame, n_regions = materialize.next_region_table(
        windows, categories, place_to_index, poi_to_region)
    region_frame.to_parquet(directory / "input" / "next_region.parquet", index=False)

    materialize.sequences_table(windows).to_parquet(
        directory / "temp" / "sequences_next.parquet", index=False)

    # The place -> region maps, so a consumer never has to reach back into the engine this was
    # derived from. Without them the region tower silently falls back to another engine's directory,
    # on the axis that carries the headline conclusion.
    pd.DataFrame({"placeid": list(place_to_index.keys()),
                  "poi_idx": list(place_to_index.values())}).to_parquet(
        directory / "place_index.parquet", index=False)
    pd.DataFrame({"poi_idx": np.arange(len(poi_to_region), dtype=np.int64),
                  "region_idx": np.asarray(poi_to_region, dtype=np.int64)}).to_parquet(
        directory / "poi_to_region.parquet", index=False)

    manifest = _manifest(state, config, run, _summarise(graph), len(corpus), len(windows.target),
                         n_regions, data_config)
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2))
    logger.info("substrate written to %s · %d windows · %d regions",
                directory, len(windows.target), n_regions)
    return manifest


def _refuse_leaky_export(graph: CheckinGraph) -> None:
    """Verify forward-onlyness from the EDGE INDEX, not from a caller's summary.

    The first version of this guard read `graph_summary["forward_only"]` — a dict the caller
    assembles — which makes the whole 28.63 pp leak class ride on a dict literal being honest. A
    caller that mislabels its graph passes. So the property is checked where it lives: every edge
    must run from an earlier visit to a later one, which holds only because `corpus.load` sorted the
    check-ins into `(userid, datetime)` order, making a node id its position in its user's history.

    Under a bidirectional graph a visit's neighbourhood contains its own future, so the one-shot
    readout writes the window's target into the history's features and the category cell scores
    ~56.9 instead of ~28.2 — a spectacular-looking substrate improvement that is a leak.
    """
    edges = graph.edge_index
    if edges.shape[1] and not bool((edges[0] < edges[1]).all()):
        backward = int((edges[0] >= edges[1]).sum())
        raise ValueError(
            f"refusing to export: {backward} of {edges.shape[1]} edges do not run forward in time, "
            f"so a one-shot readout would write the window's target into its own history. Build the "
            f"graph with forward_only=True, or export per window."
        )
    if not graph.forward_only:
        raise ValueError(
            "refusing to export: the graph reports forward_only=False. Its edges happen to be "
            "forward-only, but the flag and the data disagree and one of them is wrong."
        )


def _refuse_misaligned_corpus(corpus: pd.DataFrame, graph: CheckinGraph) -> None:
    """The corpus must be the one the graph was built from, not merely the same length.

    A re-sorted corpus of equal length passes every shape check and produces a fully scrambled
    substrate: each window would take its embeddings from one visit and its label from another.
    """
    if len(corpus) != graph.n_nodes:
        raise ValueError(
            f"corpus has {len(corpus)} check-ins and the graph {graph.n_nodes} nodes")


def _summarise(graph: CheckinGraph) -> dict[str, Any]:
    return {"forward_only": graph.forward_only, "nodes": graph.n_nodes, "edges": graph.n_edges,
            "dropped_backward": graph.dropped_backward}


def _write_levels(directory: Path, run: SubstrateRun, corpus: pd.DataFrame,
                  checkin: np.ndarray) -> None:
    columns = [str(i) for i in range(checkin.shape[1])]

    frame = pd.DataFrame(checkin, columns=columns)
    for column in ("datetime", "category", "placeid", "userid"):
        frame.insert(0, column, corpus[column].to_numpy())
    frame.to_parquet(directory / "embeddings.parquet", index=False)

    for name, tensor in (("poi_embeddings", run.place), ("region_embeddings", run.region)):
        level = pd.DataFrame(tensor.numpy(), columns=columns)
        # The index column the region tower joins on. Named for its level, not "id", because a
        # place index and a region index are both integers and confusing them is silent.
        level.insert(0, "region_idx" if name.startswith("region") else "poi_idx",
                     np.arange(len(level), dtype=np.int64))
        level.to_parquet(directory / f"{name}.parquet", index=False)


def _manifest(state: str, config: SubstrateConfig, run: SubstrateRun,
              graph_summary: dict[str, Any], n_checkins: int, n_windows: int,
              n_regions: int, data_config: DataConfig) -> dict[str, Any]:
    return {
        "state": state,
        "engine": config.engine,
        "recipe": asdict(config),
        "graph": graph_summary,
        "counts": {"checkins": n_checkins, "windows": n_windows, "regions": n_regions},
        "data_recipe": asdict(data_config),
        "training": {
            "best_epoch": run.best_epoch,
            "best_loss": run.best_loss,
            "epochs_to_within_one_percent": run.epochs_to_within_one_percent,
            "seconds": run.seconds,
            "seconds_per_epoch": run.seconds / max(len(run.losses), 1),
            "n_params": run.n_params,
            "seed": run.seed,
            "init_fingerprint": run.init_fingerprint,
            "peak_memory_gb": (run.peak_memory_bytes / 2**30
                               if run.peak_memory_bytes is not None else None),
            "loss_curve": run.losses,
        },
        # The two switches that changed between the reference and here. Both are recorded because
        # both change what the artifact IS, and neither is visible from the numbers.
        "switches": {
            "region_hard_negatives": run.hard_negatives,
            "hard_negative_size_gate": config.p2r_hard_neg_size_gate,
            # Requested AND achieved. They differ when CUBLAS_WORKSPACE_CONFIG was not set before
            # torch initialised, and a manifest reporting only the request would promise a
            # reproducibility the run does not have.
            "deterministic_requested": run.deterministic,
            "deterministic_achieved": run.deterministic_achieved,
            # Empty means the guarantee is complete. Non-empty names exactly what it does not cover.
            "nondeterministic_fallbacks": run.nondeterministic_ops,
        },
    }


__all__ = ["write"]
