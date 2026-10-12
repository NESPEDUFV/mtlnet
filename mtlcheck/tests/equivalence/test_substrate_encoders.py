"""The three substrate encoders, against the reference, by weight transplant.

Same form as E7 on the task heads: load the reference's own parameters into my module and compare
outputs. A shared seed proves nothing across a rewrite — the RNG is consumed in a different order —
so the only honest test is identical weights through two independently written forward passes.

`Checkin2POI` and `POI2Region` are two copies of one operation in the reference; here they share
`SeedAttentionPool`. That makes the transplant more valuable, not less: if the shared pool were
wrong, both comparisons would fail, and they are compared against two *different* reference
implementations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

from ._old_repo import OLD_REPO

OLD_RESEARCH = OLD_REPO / "research"

DIM = 64
HEADS = 4
IN_CHANNELS = 15  # v18: 7 categories + 4 temporal + 4 elapsed


@pytest.fixture(scope="module")
def reference():
    if not OLD_RESEARCH.exists():
        pytest.skip(f"reference repo absent: {OLD_RESEARCH}")
    if str(OLD_RESEARCH) not in sys.path:
        sys.path.insert(0, str(OLD_RESEARCH))
    try:
        from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
        from embeddings.check2hgi.model.variants import ResidualLNEncoder
        from embeddings.hgi.model.RegionEncoder import POI2Region
    except Exception as exc:                                  # pragma: no cover
        pytest.skip(f"reference encoders not importable: {exc}")
    return {"Checkin2POI": Checkin2POI, "POI2Region": POI2Region,
            "ResidualLNEncoder": ResidualLNEncoder}


@pytest.fixture(scope="module")
def graph():
    """A small ragged hierarchy: 400 check-ins over 60 POIs over 12 regions.

    Deliberately uneven — a POI with one visit and a POI with dozens exercise the segmented softmax
    differently, and a uniform fan-in would let a wrong grouping still produce plausible numbers.
    """
    g = torch.Generator().manual_seed(11)
    n_checkins, n_pois, n_regions = 400, 60, 12

    checkin_to_poi = torch.randint(0, n_pois, (n_checkins,), generator=g)
    checkin_to_poi[:n_pois] = torch.arange(n_pois)  # every POI gets at least one visit
    poi_to_region = torch.randint(0, n_regions, (n_pois,), generator=g)
    poi_to_region[:n_regions] = torch.arange(n_regions)

    src = torch.randint(0, n_regions, (40,), generator=g)
    dst = torch.randint(0, n_regions, (40,), generator=g)
    keep = src != dst
    region_adjacency = torch.stack([src[keep], dst[keep]])

    return {
        "x_checkin": torch.randn(n_checkins, IN_CHANNELS, generator=g),
        "h_checkin": torch.randn(n_checkins, DIM, generator=g),
        "h_poi": torch.randn(n_pois, DIM, generator=g),
        "checkin_to_poi": checkin_to_poi,
        "poi_to_region": poi_to_region,
        "region_adjacency": region_adjacency,
        "n_checkins": n_checkins, "n_pois": n_pois, "n_regions": n_regions,
        "edge_index": torch.stack([torch.arange(n_checkins - 1), torch.arange(1, n_checkins)]),
        "edge_weight": torch.rand(n_checkins - 1, generator=g),
    }


def _transplant(mine: torch.nn.Module, source: dict, mapping: dict[str, str]) -> None:
    """Copy reference parameters into my module under an explicit name mapping.

    Explicit rather than fuzzy: a renaming that silently skipped a tensor would leave that tensor at
    its random initialisation and the test would compare two different functions.
    """
    target = dict(mine.state_dict())
    unmapped = set(target)
    for old_key, new_key in mapping.items():
        value = source[old_key]
        assert new_key in target, f"{new_key} is not a parameter of {type(mine).__name__}"
        assert value.shape == target[new_key].shape, (
            f"{old_key} -> {new_key}: {tuple(value.shape)} vs {tuple(target[new_key].shape)}")
        target[new_key] = value
        unmapped.discard(new_key)
    assert not unmapped, f"left at random init: {sorted(unmapped)}"
    mine.load_state_dict(target, strict=True)


POOL_MAP = {f"fc_{p}.{w}": f"pool.fc_{p}.{w}" for p in "qkvo" for w in ("weight", "bias")}


def test_residual_ln_encoder(reference, graph) -> None:
    from mtlcheck.substrate.encoders import ResidualLNEncoder

    torch.manual_seed(0)
    ref = reference["ResidualLNEncoder"](IN_CHANNELS, DIM, num_layers=2, dropout=0.1).eval()
    mine = ResidualLNEncoder(IN_CHANNELS, DIM, num_layers=2, dropout=0.1).eval()
    mine.load_state_dict(ref.state_dict(), strict=True)  # names already coincide

    with torch.no_grad():
        expected = ref(graph["x_checkin"], graph["edge_index"], graph["edge_weight"])
        got = mine(graph["x_checkin"], graph["edge_index"], graph["edge_weight"])

    assert torch.equal(got, expected), f"max|delta| = {(got - expected).abs().max():.3e}"


def test_checkin_to_poi_pooling(reference, graph) -> None:
    from mtlcheck.substrate.encoders import Checkin2POI

    torch.manual_seed(1)
    ref = reference["Checkin2POI"](DIM, num_heads=HEADS).eval()
    mine = Checkin2POI(DIM, num_heads=HEADS).eval()
    # `scale` is a buffer in the reference and a python float here — nothing to transplant.
    _transplant(mine, ref.state_dict(),
                {**POOL_MAP, "S": "pool.seed", "prelu.weight": "prelu.weight"})

    with torch.no_grad():
        expected = ref(graph["h_checkin"], graph["checkin_to_poi"], graph["n_pois"])
        got = mine(graph["h_checkin"], graph["checkin_to_poi"], graph["n_pois"])

    assert got.shape == (graph["n_pois"], DIM)
    torch.testing.assert_close(got, expected, rtol=0, atol=1e-6)


def test_poi_to_region_pooling(reference, graph) -> None:
    from mtlcheck.substrate.encoders import POI2Region

    torch.manual_seed(2)
    ref = reference["POI2Region"](DIM, num_heads=HEADS).eval()
    mine = POI2Region(DIM, num_heads=HEADS).eval()
    source = dict(ref.state_dict())
    source["PMA.S"] = source["PMA.S"].view(1, DIM)  # [1, num_seeds=1, D] -> [1, D]
    _transplant(mine, source, {
        **{f"PMA.mab.fc_{p}.{w}": f"pool.fc_{p}.{w}" for p in "qkvo" for w in ("weight", "bias")},
        "PMA.S": "pool.seed",
        "conv.bias": "conv.bias", "conv.lin.weight": "conv.lin.weight",
        "prelu.weight": "prelu.weight",
    })

    with torch.no_grad():
        expected = ref(graph["h_poi"], graph["poi_to_region"], graph["region_adjacency"])
        got = mine(graph["h_poi"], graph["poi_to_region"], graph["region_adjacency"],
                   graph["n_regions"])

    assert got.shape == (graph["n_regions"], DIM)
    torch.testing.assert_close(got, expected, rtol=0, atol=1e-6)


def test_pooling_respects_group_boundaries(graph) -> None:
    """Moving a check-in to another POI must change only the two POIs involved.

    The transplant tests would pass on an implementation that pooled the right values into the wrong
    parents if the reference shared the same mistake — both sides run the same grouping convention.
    This one does not consult the reference at all.
    """
    from mtlcheck.substrate.encoders import Checkin2POI

    torch.manual_seed(3)
    module = Checkin2POI(DIM, num_heads=HEADS).eval()
    parent = graph["checkin_to_poi"].clone()

    with torch.no_grad():
        before = module(graph["h_checkin"], parent, graph["n_pois"])
        moved = parent.clone()
        source_poi, target_poi = int(parent[-1]), (int(parent[-1]) + 1) % graph["n_pois"]
        moved[-1] = target_poi
        after = module(graph["h_checkin"], moved, graph["n_pois"])

    changed = (~torch.isclose(before, after, atol=1e-7)).any(dim=1).nonzero().flatten().tolist()
    assert set(changed) <= {source_poi, target_poi}, f"unrelated POIs moved: {changed}"
    assert target_poi in changed, "the receiving POI did not change — the parent index is ignored"


def test_city_is_area_weighted(graph) -> None:
    from mtlcheck.substrate.encoders import region2city

    torch.manual_seed(4)
    region_emb = torch.randn(graph["n_regions"], DIM)
    area = torch.rand(graph["n_regions"])
    city = region2city(region_emb, area)

    assert city.shape == (DIM,)
    assert torch.allclose(city, torch.sigmoid(region_emb.T @ area), atol=1e-6)
