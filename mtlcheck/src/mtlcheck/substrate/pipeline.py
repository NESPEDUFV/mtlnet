"""Raw corpus to a substrate directory, in one function.

Until this existed, every substrate that had ever been built came from a scratch script — which is
how `repr_seed` stayed decorative through three rounds of validation, and why the export guards
protected nobody. The fixes were conventions, not contracts, because there was no single path they
sat on. This is that path.

## Two ways in, and the default needs no old artifact

⚠ This docstring used to say the opposite, and stayed wrong for a day after the code changed. What
follows is the state as of 2026-08-19; `_scaffolding` below is the arbiter.

Everything the substrate needs beyond the corpus — the region spatial join (`placeid_to_idx`,
`poi_to_region`), the shapefile geometry (`region_adjacency`, `region_area`), the region-by-region
category similarity the hard-negative sampler reads, the Delaunay place edges and the POI2Vec code
book — is **computed here, in-process**, from the corpus plus a census-tract shapefile:

    mtlcheck check2hgi build --recipe <r> --state <s> --shapefile <tract.shp>

The alternative entry points exist to REPRODUCE against banked artifacts, never to build:
`--hierarchy` (a pickled preprocessed join), `--poi2vec`, `--delaunay-places`/`--delaunay-edges`.
Passing them reads someone else's bytes instead of computing new ones. Both routes record a sha256
content digest of all three scaffolding artifacts in the manifest, so which one ran is never a
matter of recollection.
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ..config import DataConfig, SubstrateConfig
from . import corpus as corpus_mod
from . import export, features, graph as graph_mod, spatial
from .training import SubstrateData, SubstrateRun, build as train_build

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Hierarchy:
    """The place/region scaffolding, read from a preprocessed artifact."""

    place_to_index: dict
    poi_to_region: np.ndarray

    def place_regions(self) -> "pd.Series":
        """place id -> region id, which is what the Delaunay's cross-region test needs."""
        return pd.Series({int(pid): int(self.poi_to_region[int(i)])
                          for pid, i in self.place_to_index.items()})
    region_adjacency: np.ndarray
    region_area: np.ndarray
    region_similarity: np.ndarray
    num_places: int
    num_regions: int
    source: Path

    @classmethod
    def from_regions(cls, built, source: Path) -> "Hierarchy":
        """Build the hierarchy from a spatial join instead of a preprocessed artifact.

        This is what makes `--hierarchy` optional: with a shapefile the project derives the region
        scaffolding itself, and the artifact becomes a convenience rather than a dependency.
        """
        return cls(
            place_to_index=built.place_to_index,
            poi_to_region=built.poi_to_region,
            region_adjacency=built.region_adjacency,
            region_area=built.region_area,
            region_similarity=built.region_similarity,
            num_places=built.num_places,
            num_regions=built.num_regions,
            source=source,
        )

    @classmethod
    def load(cls, path: str | Path) -> "Hierarchy":
        path = Path(path)
        with path.open("rb") as handle:
            raw = pickle.load(handle)

        missing = [k for k in ("placeid_to_idx", "poi_to_region", "region_adjacency",
                               "region_area", "coarse_region_similarity", "num_pois",
                               "num_regions") if k not in raw]
        if missing:
            raise ValueError(f"{path} is missing {missing}")

        return cls(
            place_to_index=raw["placeid_to_idx"],
            poi_to_region=np.asarray(raw["poi_to_region"], dtype=np.int64),
            region_adjacency=np.asarray(raw["region_adjacency"], dtype=np.int64),
            region_area=np.asarray(raw["region_area"], dtype=np.float32),
            region_similarity=np.asarray(raw["coarse_region_similarity"], dtype=np.float32),
            num_places=int(raw["num_pois"]),
            num_regions=int(raw["num_regions"]),
            source=path,
        )


def build(state: str, config: SubstrateConfig, *, hierarchy_path: Path | None = None,
          shapefile: Path | None = None, poi2vec_path: Path | None = None,
          delaunay_places_path: Path | None = None, delaunay_edges_path: Path | None = None,
          out_dir: Path, device: torch.device, corpus_path: Path | None = None,
          data_config: DataConfig | None = None,
          deterministic: bool = True) -> dict:
    """Build one state's substrate and write it. Returns the manifest.

    The spatial scaffolding — the Delaunay place graph and the POI2Vec code book — is COMPUTED HERE
    when its paths are not given, so one command goes corpus -> substrate with no intermediate file
    to go stale. Passing the paths reads the artifacts instead, which is how a build reproduces
    against the old HGI engine's files.

    Why in-process is the default rather than a convenience. The round trip is not a numerical
    problem: the POI2Vec table is float32 and float32 through CSV is exact (verified). The problem is
    STALENESS — an artifact that survives a regeneration and is read as if it were current. This
    project has been burned by exactly that twice (C22, C29: a two-week-old transition matrix
    inflated Acc@10 by 8-12 pp and voided four waves of results), and a CSV sitting between two
    stages is that surface. Computed in-process the question cannot arise; read from disk, the
    manifest carries a content hash so the answer is checkable rather than assumed.
    """
    data_config = data_config or DataConfig()

    corpus = corpus_mod.load(state, path=corpus_path)
    if shapefile is not None:
        from . import regions as regions_mod
        built = regions_mod.build(corpus.frame, shapefile, category_codes=corpus.category_codes)
        hierarchy = Hierarchy.from_regions(built, Path(shapefile))
    elif hierarchy_path is not None:
        hierarchy = Hierarchy.load(hierarchy_path)
    else:
        raise ValueError("pass either a shapefile (to derive the regions) or a hierarchy artifact")
    corpus = _restrict_to_hierarchy(corpus, hierarchy)
    logger.info("corpus: %d check-ins · %d users · %d places · %d categories",
                corpus.n_checkins, corpus.n_users, corpus.n_places, corpus.n_categories)

    node_features = features.build(corpus, continuous_time=config.continuous_time)
    checkin_graph = graph_mod.build(corpus, forward_only=config.forward_only)

    checkin_to_poi = _place_indices(corpus.frame, hierarchy)
    scaffolding = _scaffolding(
        corpus, hierarchy, out_dir,
        poi2vec_path=poi2vec_path, delaunay_places_path=delaunay_places_path,
        delaunay_edges_path=delaunay_edges_path, seed=config.repr_seed,
        fix_unit_mismatch=config.fix_unit_mismatch,
        symmetrise_poi2vec=config.symmetrise_poi2vec)
    poi2vec = scaffolding["poi2vec"]
    delaunay_index, delaunay_weight = scaffolding["delaunay"]
    # config.mae_poi_target_dim, NOT corpus.n_categories. See `category_aggregate`: the reference
    # slices 8 columns and the eighth is mean hour_sin, so passing the true category count (7) built
    # a different objective than the one both banked substrates were trained on.
    recon_target = spatial.category_aggregate(
        node_features.matrix, checkin_to_poi, hierarchy.num_places, config.mae_poi_target_dim)

    as_tensor = lambda a, dtype=torch.float32: torch.tensor(np.asarray(a), dtype=dtype)
    data = SubstrateData(
        x=as_tensor(node_features.matrix),
        edge_index=as_tensor(checkin_graph.edge_index, torch.int64),
        edge_weight=as_tensor(checkin_graph.edge_weight),
        checkin_to_poi=as_tensor(checkin_to_poi, torch.int64),
        poi_to_region=as_tensor(hierarchy.poi_to_region, torch.int64),
        region_adjacency=as_tensor(hierarchy.region_adjacency, torch.int64),
        region_area=as_tensor(hierarchy.region_area),
        coarse_region_similarity=as_tensor(hierarchy.region_similarity),
        poi_delaunay_edge_index=delaunay_index,
        poi_recon_target=recon_target,
    )

    _model, run = train_build(
        config, data, in_channels=node_features.in_channels, num_places=hierarchy.num_places,
        num_regions=hierarchy.num_regions, poi2vec_table=poi2vec,
        delaunay_edge_index=delaunay_index, delaunay_edge_weight=delaunay_weight,
        recon_target_dim=int(recon_target.shape[1]), device=device, deterministic=deterministic)

    # Two export paths, chosen by the graph, not by a flag. A bidirectional build (v14) must not
    # produce check-in artifacts: the one-shot full-graph readout is equivalent to per-window
    # encoding ONLY under a forward-only graph, so `embeddings.parquet` and `input/next.parquet`
    # would be silently wrong. The leak guard in `export.write` is therefore left exactly as strict
    # — a bidirectional build simply never asks it for the artifacts it protects.
    manifest = export.write(
        out_dir, run, corpus.frame, state=state, config=config,
        place_to_index=hierarchy.place_to_index, poi_to_region=hierarchy.poi_to_region,
        graph=checkin_graph, data_config=data_config)

    # The provenance that makes "built from the corpus" a checkable statement rather than a slogan.
    manifest["inputs"] = {
        "corpus": str(corpus_path or "<default>"),
        "hierarchy": str(hierarchy.source),
        "hierarchy_derived_here": shapefile is not None,
        **scaffolding["provenance"],
        "not_rebuilt_here": (
            [] if shapefile is not None else
            ["the region spatial join (place->region, adjacency, area, similarity)"]
        ),
    }
    manifest["features"] = {"width": node_features.in_channels, "layout": list(node_features.layout)}
    (Path(out_dir) / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _scaffolding(corpus, hierarchy, out_dir: Path, *, poi2vec_path: Path | None,
                 delaunay_places_path: Path | None, delaunay_edges_path: Path | None,
                 seed: int, fix_unit_mismatch: bool = False,
                 symmetrise_poi2vec: bool = False) -> dict:
    """The Delaunay graph and the POI2Vec table: computed here, or read from given paths.

    Both are written to `out_dir/temp/` either way and hashed into the manifest, so "which POI2Vec
    was this substrate anchored to?" is answerable from the artifact rather than from a path that
    may since have been overwritten.
    """
    from . import delaunay as delaunay_mod, poi2vec as poi2vec_mod

    temp = Path(out_dir) / "temp"
    provenance: dict = {}

    if delaunay_places_path is not None and delaunay_edges_path is not None:
        places_path, edges_path = Path(delaunay_places_path), Path(delaunay_edges_path)
        provenance["delaunay"] = {"source": "read", "places": str(places_path),
                                  "edges": str(edges_path)}
    else:
        logger.info("delaunay: computing the place graph from the corpus")
        frame = corpus.frame.rename(columns={"spot": "fclass"})
        graph = delaunay_mod.build(frame, hierarchy.place_regions(),
                                   fix_unit_mismatch=fix_unit_mismatch)
        graph.write(temp)
        places_path, edges_path = temp / "pois.csv", temp / "edges.csv"
        provenance["delaunay"] = {"source": "computed", "places": len(graph.places),
                                  "edges": len(graph.edges),
                                  "dropped_outside": graph.dropped_outside}

    if poi2vec_path is not None:
        table_path = Path(poi2vec_path)
        provenance["poi2vec"] = {"source": "read", "path": str(table_path)}
    else:
        logger.info("poi2vec: training the code book from the place graph")
        places = pd.read_csv(places_path)
        edges = pd.read_csv(edges_path)
        table = poi2vec_mod.build(places, edges, seed=seed, symmetrise=symmetrise_poi2vec)
        table_path = temp / "poi2vec.csv"
        table.write(table_path)
        provenance["poi2vec"] = {"source": "computed", "seed": seed,
                                 "vocab": table.vocab_size,
                                 "distinct_vectors": table.distinct_vectors,
                                 "best_epoch": table.best_epoch}

    # The hash is what makes reuse checkable. A path is not provenance — it can be overwritten
    # between the build that wrote it and the build that reads it, which is C22 exactly.
    for key, path in (("delaunay_places", places_path), ("delaunay_edges", edges_path),
                      ("poi2vec", table_path)):
        provenance.setdefault("digests", {})[key] = _digest(path)

    return {
        "poi2vec": spatial.load_poi2vec(table_path, hierarchy.num_places, hierarchy.place_to_index),
        "delaunay": spatial.load_delaunay(places_path, edges_path, hierarchy.num_places,
                                          hierarchy.place_to_index),
        "provenance": provenance,
    }


def _digest(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()[:16]


def _restrict_to_hierarchy(corpus, hierarchy):
    """Descarta as visitas cujo lugar não sobreviveu ao join espacial.

    **No-op nos cinco estados dos EUA**, e é por isso que o caminho nunca rodou: os census tracts do
    TIGER ladrilham o estado, então nenhum lugar cai fora e este filtro não remove linha nenhuma.

    Em Istambul 12 850 dos 42 795 lugares não recebem região e as 80 109 visitas neles ficariam
    órfãs. **A causa dominante não é geométrica**: 12 516 desses lugares (97,4 %) não têm
    latitude/longitude **na fonte** — o `tabular` bruto do Massive-STEPS traz 62 621 linhas com NaN,
    e a ETL não perde nada. A lacuna geométrica real é de 328 lugares, 0,77 % do corpus — o corpus e a hierarquia
    discordariam, que é exatamente o que `_place_indices` recusa (e recusa com razão: um lugar
    ausente vira NaN, que o numpy converte em índice negativo e agrupa as visitas no último lugar).

    A referência fazia esta mesma restrição em silêncio, via o CSV de bairros pré-posicionado. Que
    ela é a operação certa está medido: sobram 29 945 lugares em 520 regiões, contra 29 816 lugares
    e **520** regiões nos artefatos dela — a contagem de regiões bate exatamente.

    ⚠ Os **129 lugares** de diferença (29 945 contra 29 816) **não estão explicados**. "Reproduz
    dentro do ruído" não é "reproduz": se alguém precisar da igualdade, isto é uma ponta aberta, não
    um resultado fechado.

    `category_vocab` fica intacto de propósito: reajustá-lo deslocaria os códigos das categorias e
    tornaria o substrato irreprodutível contra qualquer célula bancada.
    """
    keep = corpus.frame["placeid"].astype(np.int64).isin(hierarchy.place_to_index).to_numpy()
    if keep.all():
        return corpus
    logger.info("corpus restrito à hierarquia: %d de %d visitas descartadas (%d lugares fora do "
                "join espacial)", int((~keep).sum()), len(keep),
                corpus.n_places - int(corpus.frame.loc[keep, "placeid"].nunique()))
    return replace(corpus,
                   frame=corpus.frame.loc[keep].reset_index(drop=True),
                   category_codes=corpus.category_codes[keep])


def _place_indices(frame: pd.DataFrame, hierarchy: Hierarchy) -> np.ndarray:
    """Map each check-in's place id into the hierarchy's dense index space.

    A place present in the corpus and absent from the join would otherwise become a NaN that numpy
    casts to a negative index, silently pooling those visits into the last place.
    """
    lookup = pd.Series(hierarchy.place_to_index)
    mapped = pd.Series(frame["placeid"].astype(np.int64)).map(lookup)
    if mapped.isna().any():
        sample = frame["placeid"][mapped.isna().to_numpy()].head(5).tolist()
        raise ValueError(
            f"{int(mapped.isna().sum())} check-ins sit at places absent from the hierarchy "
            f"(sample: {sample}). The corpus and the spatial join disagree.")
    return mapped.to_numpy(dtype=np.int64)


__all__ = ["Hierarchy", "build"]
