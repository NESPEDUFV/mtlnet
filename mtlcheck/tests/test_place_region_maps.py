"""`place id -> region index` from the substrate's own parquets.

This is the last object that made a substrate built entirely by `mtlcheck` still reach back into the
OLD engine's pickle. `export.py` has been writing the two parquets all along and `check2hgi verify`
already required them — the seam was serialised, verified, and had no reader.

Verified end to end against Alabama's banked artifacts: 11,848 places, the two constructors produce
an equal Series, and `n_regions_from_map` is 1109 either way.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.data.tensors import PlaceRegionMaps


def _write(directory, placeid, poi_idx, region_idx):
    pd.DataFrame({"placeid": placeid, "poi_idx": poi_idx}).to_parquet(
        directory / "place_index.parquet", index=False)
    pd.DataFrame({"poi_idx": np.arange(len(region_idx), dtype=np.int64),
                  "region_idx": region_idx}).to_parquet(
        directory / "poi_to_region.parquet", index=False)


def test_places_resolve_through_their_poi_index(tmp_path) -> None:
    _write(tmp_path, [900, 100, 500, 700], [3, 0, 1, 2],
           np.array([10, 11, 12, 13], dtype=np.int64))

    maps = PlaceRegionMaps.from_parquet(tmp_path)
    assert maps.place_to_region.loc[900] == 13, "place 900 sits at poi 3 -> region 13"
    assert maps.place_to_region.loc[100] == 10
    assert maps.n_regions_from_map == 14, "max over the FULL table + 1, not the count of regions"


def test_row_order_of_the_parquet_does_not_matter(tmp_path) -> None:
    """`from_graph` gets this from dict semantics; a parquet has to be sorted explicitly."""
    _write(tmp_path, [1, 2, 3], [0, 1, 2], np.array([7, 8, 9], dtype=np.int64))
    straight = PlaceRegionMaps.from_parquet(tmp_path)

    pd.DataFrame({"poi_idx": [2, 0, 1], "region_idx": [9, 7, 8]}).to_parquet(
        tmp_path / "poi_to_region.parquet", index=False)
    assert straight.place_to_region.equals(PlaceRegionMaps.from_parquet(tmp_path).place_to_region)


@pytest.mark.parametrize("mutate,message", [
    (lambda d: _write(d, [1, 1, 2], [0, 1, 2], np.array([5, 6, 7])), "duplicate placeids"),
    (lambda d: pd.DataFrame({"poi_idx": [0, 0], "region_idx": [1, 2]}).to_parquet(
        d / "poi_to_region.parquet", index=False), "duplicate poi_idx"),
    (lambda d: _write(d, [1], [9], np.array([3])), "against a region table"),
    (lambda d: _write(d, [1], [0], np.array([-1])), "negative region index"),
])
def test_the_checks_dict_semantics_gave_for_free(tmp_path, mutate, message) -> None:
    """Four things a dict and an ndarray guaranteed, and a parquet does not.

    A duplicated placeid makes the join ambiguous; a duplicated poi_idx likewise; a poi_idx past the
    end indexes off the table. The negative region index is the quiet one — it is a perfectly valid
    position counted from the other end of the array, so it resolves to some real region and nothing
    raises.
    """
    _write(tmp_path, [1, 2, 3], [0, 1, 2], np.array([5, 6, 7], dtype=np.int64))
    mutate(tmp_path)
    with pytest.raises(ValueError, match=message):
        PlaceRegionMaps.from_parquet(tmp_path)


def test_a_gap_in_the_region_table_is_refused(tmp_path) -> None:
    """The fifth check dict semantics also gave for free, and the quietest of them.

    The lookup is positional after the sort, so a table missing poi_idx 3 shifts every place after
    it onto the wrong region — with the right number of rows, the right dtypes, and no error.
    """
    pd.DataFrame({"placeid": [1, 2], "poi_idx": [0, 3]}).to_parquet(
        tmp_path / "place_index.parquet", index=False)
    pd.DataFrame({"poi_idx": [0, 1, 2, 4], "region_idx": [5, 6, 7, 8]}).to_parquet(
        tmp_path / "poi_to_region.parquet", index=False)

    with pytest.raises(ValueError, match="no gaps"):
        PlaceRegionMaps.from_parquet(tmp_path)


def test_the_region_tower_prefers_the_substrates_own_maps(tmp_path, monkeypatch) -> None:
    """The headline behaviour of the change had no test at all.

    `use_parquet = False` hardcoded in dataset._region_tower would have passed the whole suite: the
    fixtures carry no place_index.parquet and every existing caller passes graph_path explicitly.
    """
    import inspect

    from mtlcheck.data import dataset

    source = inspect.getsource(dataset._region_tower)
    assert "PlaceRegionMaps.from_parquet" in source
    # Resolution ORDER: an explicit graph_path must still win, so a caller can pin the legacy pickle.
    assert "graph_path is None and parquet_maps.exists()" in source, (
        "an explicit --graph-path must override the substrate's own maps, not the other way round")


def test_a_negative_region_index_is_refused_on_BOTH_constructors(tmp_path) -> None:
    """The guard existed only on the parquet path, which made the safer constructor the unused one.

    A negative index is a valid position counted from the other end of the array, so it resolves to
    a real region and nothing raises — the failure mode that cannot announce itself.
    """
    import pickle

    from mtlcheck.data.tensors import assert_region_table

    with pytest.raises(ValueError, match="negative region index"):
        assert_region_table(np.array([0, 1, -1]), "wherever")
    with pytest.raises(ValueError, match="empty"):
        assert_region_table(np.array([], dtype=np.int64), "wherever")

    graph = tmp_path / "checkin_graph.pt"
    with open(graph, "wb") as handle:
        pickle.dump({"placeid_to_idx": {7: 0, 8: 1}, "poi_to_region": np.array([0, -3])}, handle)
    with pytest.raises(ValueError, match="negative region index"):
        PlaceRegionMaps.from_graph(graph)
