"""The region spatial join against the banked hierarchy it must reproduce.

This was the last piece standing between the project and building a substrate from raw data, and it
is the one with the most ways to be *nearly* right: a place count that matches while the partition
differs, region indices that permute, an area in the wrong units. So the test compares the
PARTITION rather than the index vector — region numbering follows first appearance in the place
table, so a different-but-equivalent grouping would fail an index comparison for no reason, and an
index comparison that passed would not prove the grouping is the same.
"""

from __future__ import annotations

import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest

from ._old_repo import OLD_REPO

OLD = OLD_REPO
GRAPH = OLD / "output/check2hgi/alabama/temp/checkin_graph.pt"
SHAPEFILE = OLD / "data/miscellaneous/tl_2022_01_tract_AL/tl_2022_01_tract.shp"
CORPUS = OLD / "data/checkins/Alabama.parquet"


@pytest.fixture(scope="module")
def built_and_banked():
    for path in (GRAPH, SHAPEFILE, CORPUS):
        if not path.exists():
            pytest.skip(f"absent: {path}")
    pytest.importorskip("geopandas")

    from mtlcheck.substrate import corpus as corpus_mod, regions

    with GRAPH.open("rb") as handle:
        banked = pickle.load(handle)
    corpus = corpus_mod.load("alabama", path=CORPUS)
    built = regions.build(corpus.frame, SHAPEFILE, category_codes=corpus.category_codes)
    return built, banked


@pytest.mark.artifacts
def test_counts_match_the_banked_hierarchy(built_and_banked) -> None:
    built, banked = built_and_banked
    assert built.num_places == int(banked["num_pois"])
    assert built.num_regions == int(banked["num_regions"])
    assert built.region_adjacency.shape[1] == np.asarray(banked["region_adjacency"]).shape[1]


@pytest.mark.artifacts
def test_the_place_to_region_partition_is_identical(built_and_banked) -> None:
    """Compare the GROUPING, not the numbering.

    Region indices follow first appearance in the place table, so an equivalent grouping under a
    different numbering is correct and would fail a naive index comparison — while a matching index
    vector would not, on its own, prove the grouping is the same.
    """
    built, banked = built_and_banked
    banked_places = {int(k): v for k, v in banked["placeid_to_idx"].items()}
    banked_regions = np.asarray(banked["poi_to_region"])

    assert set(banked_places) == set(built.place_to_index), "the place inventories differ"

    def groups(place_index, region_of) -> set[frozenset]:
        buckets = defaultdict(set)
        for place, index in place_index.items():
            buckets[int(region_of[index])].add(place)
        return {frozenset(v) for v in buckets.values()}

    assert groups(banked_places, banked_regions) == groups(built.place_to_index, built.poi_to_region)


@pytest.mark.artifacts
def test_the_similarity_matrix_is_usable_as_a_hard_negative_band(built_and_banked) -> None:
    """It is what S17's sampler bands on, so its shape and range are load-bearing."""
    built, _ = built_and_banked
    similarity = built.region_similarity

    assert similarity.shape == (built.num_regions, built.num_regions)
    assert np.allclose(similarity, similarity.T, atol=1e-6), "similarity must be symmetric"
    assert similarity.min() >= -1e-6 and similarity.max() <= 1 + 1e-6

    band = (similarity > 0.6) & (similarity < 0.8)
    np.fill_diagonal(band, False)
    assert band.sum() > 0, "an empty band would silently disable hard negatives"


@pytest.mark.artifacts
def test_area_is_in_degrees_squared_and_that_is_recorded(built_and_banked) -> None:
    """Reproduced, not fixed: `region2city` weights by this, so metres would move every number.

    An Alabama tract is on the order of 1e-4 to 1e-1 square DEGREES. If someone reprojects to an
    equal-area CRS the magnitude jumps by ~10 orders and this test says so before the numbers move.
    """
    built, banked = built_and_banked
    assert built.region_area.max() < 10.0, "areas look like metres**2 — the CRS changed"
    assert np.isclose(float(built.region_area.sum()),
                      float(np.asarray(banked["region_area"]).sum()), rtol=1e-3)
