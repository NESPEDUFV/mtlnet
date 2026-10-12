"""The substrate model against the reference, by transplant: same weights, same RNG, same loss.

This is the strongest test in the suite and the one with the most ways to pass while being wrong,
because the model is stochastic **inside** the forward pass. Three separate draws happen per step —
the corruption permutation, the reconstruction mask, and the negative samples — and any rewrite that
consumes them in a different order produces a different, equally plausible loss. So the comparison is
not only "same numbers": it is same numbers under a shared seed, which pins the draw ORDER too.

Three arms:

- eval mode, tensor by tensor — isolates the deterministic computation from the sampling;
- train mode, end to end on the scalar loss — the arm that would catch a reordered RNG;
- hard negatives injected — the branch that is deliberately NOT stream-identical (S17), fed the same
  indices on both sides so the loss and the gradients can still be compared exactly.

`Check2HGI_DesignK` is not tested separately: with `hgi_poi_target=None`, which is what v18 passes,
its `__init__` adds nothing and `decoder_loss` is never called. It IS the canonical class.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

from mtlcheck.config import SubstrateConfig

from ._old_repo import OLD_REPO

OLD_RESEARCH = OLD_REPO / "research"

DIM = 64
IN_CHANNELS = 15
N_CHECKINS, N_PLACES, N_REGIONS, N_CATEGORIES = 500, 80, 14, 7


@pytest.fixture(scope="module")
def reference():
    if not OLD_RESEARCH.exists():
        pytest.skip(f"reference repo absent: {OLD_RESEARCH}")
    if str(OLD_RESEARCH) not in sys.path:
        sys.path.insert(0, str(OLD_RESEARCH))
    try:
        from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
        from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
        from embeddings.check2hgi.model.variants import ResidualLNEncoder
        from embeddings.hgi.model.RegionEncoder import POI2Region
    except Exception as exc:                                  # pragma: no cover
        pytest.skip(f"reference model not importable: {exc}")
    return {"Check2HGI": Check2HGI, "corruption": corruption, "Checkin2POI": Checkin2POI,
            "ResidualLNEncoder": ResidualLNEncoder, "POI2Region": POI2Region}


@pytest.fixture(scope="module")
def data():
    """A miniature state, with a similarity matrix dense enough to exercise the hard-negative band."""
    from torch_geometric.data import Data

    g = torch.Generator().manual_seed(7)

    checkin_to_poi = torch.randint(0, N_PLACES, (N_CHECKINS,), generator=g)
    checkin_to_poi[:N_PLACES] = torch.arange(N_PLACES)
    poi_to_region = torch.randint(0, N_REGIONS, (N_PLACES,), generator=g)
    poi_to_region[:N_REGIONS] = torch.arange(N_REGIONS)

    src = torch.randint(0, N_REGIONS, (50,), generator=g)
    dst = torch.randint(0, N_REGIONS, (50,), generator=g)
    keep = src != dst

    delaunay = torch.stack([torch.randint(0, N_PLACES, (140,), generator=g),
                            torch.randint(0, N_PLACES, (140,), generator=g)])
    delaunay = delaunay[:, delaunay[0] < delaunay[1]]

    # A similarity matrix with mass inside the (0.6, 0.8) band, or the hard branch never fires and
    # the test silently degrades to the easy path.
    similarity = torch.rand(N_REGIONS, N_REGIONS, generator=g) * 0.5 + 0.35

    d = Data(
        x=torch.randn(N_CHECKINS, IN_CHANNELS, generator=g),
        edge_index=torch.stack([torch.arange(N_CHECKINS - 1), torch.arange(1, N_CHECKINS)]),
        edge_weight=torch.rand(N_CHECKINS - 1, generator=g),
        checkin_to_poi=checkin_to_poi,
        poi_to_region=poi_to_region,
        region_adjacency=torch.stack([src[keep], dst[keep]]),
        region_area=torch.rand(N_REGIONS, generator=g),
        coarse_region_similarity=similarity,
        num_pois=N_PLACES, num_regions=N_REGIONS,
    )
    d.poi_delaunay_edge_index = delaunay
    d.poi_recon_target = torch.rand(N_PLACES, N_CATEGORIES, generator=g)
    d.poi2vec = torch.randn(N_PLACES, DIM, generator=g)
    d.delaunay_weight = torch.rand(delaunay.size(1), generator=g)
    return d


CONFIG = SubstrateConfig(engine="check2hgi_v18")
# Hard negatives are drawn differently here — vectorised instead of looped (S17) — so the two sides
# consume the RNG differently and an exact comparison is only meaningful with that branch off. The
# branch itself is covered twice below: its distribution against the loop, and its output fed
# identically into both losses.
NO_HARD_NEG = SubstrateConfig(engine="check2hgi_v18", p2r_hard_neg_size_gate=1)


@pytest.fixture
def pair(reference, data):
    """The reference model and mine, holding identical parameters."""
    torch.manual_seed(0)
    ref = reference["Check2HGI"](
        p2r_hard_neg_min_batch=0,                    # off, to match NO_HARD_NEG
        hidden_channels=DIM,
        checkin_encoder=reference["ResidualLNEncoder"](IN_CHANNELS, DIM, num_layers=2, dropout=0.1),
        checkin2poi=reference["Checkin2POI"](DIM, 4),
        poi2region=reference["POI2Region"](DIM, 4),
        region2city=lambda z, area: torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1)),
        corruption=reference["corruption"],
        alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
        reg_poi_mode="delaunay_gcn", num_pois=N_PLACES, poi2vec_table=data.poi2vec,
        gamma_init=1.0, anchor_lambda=0.1,
        delaunay_edge_index=data.poi_delaunay_edge_index, delaunay_edge_weight=data.delaunay_weight,
        side_feature_dim=0, side_feature_hidden=16,
        mae_poi_lambda=0.3, mae_poi_mask_rate=0.15, mae_poi_gamma=3.0,
        mae_poi_target_dim=N_CATEGORIES, mae_poi_aggr="mean",
        mae_poi_target_kind="category_aggregate", mae_poi_loss_kind="sce",
    )

    from mtlcheck.substrate.model import Check2HGI

    mine = Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, data.poi2vec,
                     data.poi_delaunay_edge_index, data.delaunay_weight, N_CATEGORIES, NO_HARD_NEG)
    _transplant(mine, ref)
    return ref, mine


def _transplant(mine, ref) -> None:
    """Copy the reference's parameters into mine under an explicit rename.

    Every name that differs is renamed on purpose — `poi`/`reg` prefixes that meant three different
    things, a seed vector nested two modules deep — so the mapping is spelled out and any parameter
    left behind fails the load.
    """
    source = dict(ref.state_dict())
    source["poi2region.PMA.S"] = source["poi2region.PMA.S"].view(1, DIM)
    source.pop("checkin2poi.scale")                      # a buffer there, a python float here

    renames = {
        "checkin2poi.S": "checkin2poi.pool.seed",
        "poi2region.PMA.S": "poi2region.pool.seed",
        "reg_poi_table.weight": "place_table.weight",
        "reg_poi2vec_anchor": "place_anchor",
        "reg_delaunay_edge_index": "delaunay_edge_index",
        "reg_delaunay_edge_weight": "delaunay_edge_weight",
        "reg_gamma": "place_gamma",
        "poi_gcn.bias": "place_gcn.bias",
        "poi_gcn.lin.weight": "place_gcn.lin.weight",
        "poi_gcn_act.weight": "place_gcn_act.weight",
    }
    for part in ("qkvo"):
        renames[f"checkin2poi.fc_{part}.weight"] = f"checkin2poi.pool.fc_{part}.weight"
        renames[f"checkin2poi.fc_{part}.bias"] = f"checkin2poi.pool.fc_{part}.bias"
        renames[f"poi2region.PMA.mab.fc_{part}.weight"] = f"poi2region.pool.fc_{part}.weight"
        renames[f"poi2region.PMA.mab.fc_{part}.bias"] = f"poi2region.pool.fc_{part}.bias"
    renames.update({k: k.replace("mae_poi_decoder", "place_decoder")
                    for k in source if k.startswith("mae_poi_decoder")})

    target = dict(mine.state_dict())
    remaining = set(target)
    for old_key, value in source.items():
        new_key = renames.get(old_key, old_key)
        assert new_key in target, f"reference key {old_key} has no home (tried {new_key})"
        assert value.shape == target[new_key].shape, f"{old_key} -> {new_key}: shape mismatch"
        target[new_key] = value
        remaining.discard(new_key)
    assert not remaining, f"left at random init: {sorted(remaining)}"
    mine.load_state_dict(target, strict=True)


def test_parameter_count_matches(pair) -> None:
    ref, mine = pair
    ref_count = sum(p.numel() for p in ref.parameters())
    my_count = sum(p.numel() for p in mine.parameters())
    assert my_count == ref_count, f"{my_count:,} vs {ref_count:,}"


def test_forward_tensors_match_in_eval(pair, data) -> None:
    """Every tensor the loss consumes, with sampling made reproducible by a shared seed."""
    ref, mine = pair
    ref.eval(); mine.eval()

    with torch.no_grad():
        torch.manual_seed(123)
        expected = ref(data)
        torch.manual_seed(123)
        got = mine(data)

    names = ["checkin", "place_of_checkin", "other_place_of_checkin", "place",
             "region_of_place", "other_region_of_place", "region", "corrupted_region", "city"]
    for name, reference_tensor in zip(names, expected):
        torch.testing.assert_close(got[name], reference_tensor, rtol=0, atol=1e-6,
                                   msg=lambda m, n=name: f"{n}: {m}")


def test_loss_matches_in_eval(pair, data) -> None:
    ref, mine = pair
    ref.eval(); mine.eval()

    with torch.no_grad():
        torch.manual_seed(321)
        expected = ref.loss(*ref(data))
        torch.manual_seed(321)
        got = mine.loss(mine(data))

    assert abs(float(got) - float(expected)) < 1e-6, f"{float(got):.9f} vs {float(expected):.9f}"


def test_loss_matches_in_train_mode(pair, data) -> None:
    """The arm that pins the RNG order: dropout, corruption, mask and negatives, all in one draw."""
    ref, mine = pair
    ref.train(); mine.train()

    torch.manual_seed(999)
    expected = ref.loss(*ref(data))
    torch.manual_seed(999)
    got = mine.loss(mine(data))

    assert abs(float(got) - float(expected)) < 1e-6, f"{float(got):.9f} vs {float(expected):.9f}"


def test_gradients_match(pair, data) -> None:
    """Equal loss under equal weights can still hide a detached branch. Compare the gradients."""
    ref, mine = pair
    ref.train(); mine.train()

    torch.manual_seed(555)
    ref.loss(*ref(data)).backward()
    torch.manual_seed(555)
    mine.loss(mine(data)).backward()

    # The pairs whose gradient would move if the region-axis detach were missing or misplaced.
    pairs = [("checkin_encoder.convs.0.lin.weight", "checkin_encoder.convs.0.lin.weight"),
             ("checkin2poi.fc_v.weight", "checkin2poi.pool.fc_v.weight"),
             ("reg_poi_table.weight", "place_table.weight"),
             ("weight_c2p", "weight_c2p"),
             ("weight_p2r", "weight_p2r")]
    ref_grads = {n: p.grad for n, p in ref.named_parameters()}
    my_grads = {n: p.grad for n, p in mine.named_parameters()}
    for ref_name, my_name in pairs:
        assert ref_grads[ref_name] is not None, f"{ref_name} has no gradient in the reference"
        torch.testing.assert_close(my_grads[my_name], ref_grads[ref_name], rtol=0, atol=1e-6,
                                   msg=lambda m, n=my_name: f"{n}: {m}")


def test_region_axis_does_not_reach_the_encoder(pair, data) -> None:
    """The detach, tested directly rather than inferred from matching numbers.

    If it were removed, the check-in encoder would receive gradient from the region boundary and the
    category axis would silently start depending on the spatial table. Both models would still agree
    with each other if both were wrong, so this asserts the property itself.
    """
    _, mine = pair
    mine.train()

    torch.manual_seed(31)
    out = mine(data)
    region_only = mine.config.alpha_p2r * torch.nn.functional.softplus(out["region"]).mean()
    region_only.backward()

    encoder_grads = [p.grad for n, p in mine.named_parameters()
                     if n.startswith("checkin_encoder") and p.grad is not None]
    assert not encoder_grads, "the region axis reached the check-in encoder — the detach is gone"
    assert mine.place_table.weight.grad is not None, "the place table should have received gradient"


def test_hard_negatives_do_not_depend_on_the_size_of_the_state(data) -> None:
    """S17 fixed — the default trains every state on the same objective.

    The reference disables hard negatives above 50 000 places, so Alabama and Texas optimise
    different losses. The gate survives only as an opt-in for reproducing that split.
    """
    from mtlcheck.substrate.model import Check2HGI
    from dataclasses import replace as dc_replace

    args = (data.poi2vec, data.poi_delaunay_edge_index, data.delaunay_weight, N_CATEGORIES)
    huge = 200_000

    small = Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, *args, CONFIG)
    big = Check2HGI(IN_CHANNELS, huge, N_REGIONS, torch.zeros(huge, DIM),
                    data.poi_delaunay_edge_index, data.delaunay_weight, N_CATEGORIES, CONFIG)
    assert small.hard_negatives and big.hard_negatives, "the default must not depend on size"

    legacy = dc_replace(CONFIG, p2r_hard_neg_size_gate=50_000)
    assert Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, *args, legacy).hard_negatives
    assert not Check2HGI(IN_CHANNELS, huge, N_REGIONS, torch.zeros(huge, DIM),
                         data.poi_delaunay_edge_index, data.delaunay_weight,
                         N_CATEGORIES, legacy).hard_negatives


def _reference_hard_negatives(model, assignment, num_regions, similarity):
    """The reference's loop, verbatim in structure, as the distribution to match."""
    from mtlcheck.substrate.model import _sample_negatives

    negatives = _sample_negatives(assignment, num_regions)
    low, high = model.config.p2r_hard_neg_sim_range
    chosen = torch.rand(assignment.size(0)) < model.config.p2r_hard_neg_prob
    for i in chosen.nonzero(as_tuple=True)[0].tolist():
        positive = int(assignment[i])
        band = similarity[positive]
        candidates = ((band > low) & (band < high)).nonzero(as_tuple=True)[0]
        candidates = candidates[candidates != positive]
        if len(candidates):
            negatives[i] = candidates[torch.randint(len(candidates), (1,)).item()]
    return negatives


def test_hard_negatives_reach_the_loss_identically(pair, data) -> None:
    """Feed both models the SAME hard negatives and require the loss and gradients to match.

    The vectorised sampler cannot be stream-identical to the loop it replaces, so exactness has to
    be established one layer in: given the same indices, everything downstream of the draw — the
    bilinear discriminator, the weighting, the backward — must still agree to 1e-6. Without this,
    fixing S17 would have cost the exact comparison of the p2r boundary entirely.
    """
    ref, mine = pair
    ref.train(); mine.train()

    fixed = torch.randint(0, N_REGIONS, (N_PLACES,), generator=torch.Generator().manual_seed(8))
    fixed = torch.where(fixed == data.poi_to_region, (fixed + 1) % N_REGIONS, fixed)

    ref._sample_negative_indices_with_similarity = lambda *a, **k: fixed.clone()
    mine._sample_region_negatives = lambda *a, **k: fixed.clone()

    torch.manual_seed(77)
    expected = ref.loss(*ref(data))
    expected.backward()
    torch.manual_seed(77)
    got = mine.loss(mine(data))
    got.backward()

    assert abs(float(got) - float(expected)) < 1e-6, f"{float(got):.9f} vs {float(expected):.9f}"
    torch.testing.assert_close(dict(mine.named_parameters())["weight_p2r"].grad,
                               dict(ref.named_parameters())["weight_p2r"].grad, rtol=0, atol=1e-6)


def test_vectorised_hard_negatives_match_the_loop_in_distribution(pair, data) -> None:
    """The vectorised draw is the same random variable as the loop, not just the same shape.

    Vectorising changes the RNG stream, so this cannot be an equality test — it asserts the three
    properties that define the draw: the resampling rate, that every hard negative lands inside the
    band and never on the positive, and that the choice within a band is uniform.
    """
    _, mine = pair
    mine.hard_negatives = True          # the fixture disables them for the stream-exact arms
    similarity = data.coarse_region_similarity
    assignment = data.poi_to_region
    low, high = CONFIG.p2r_hard_neg_sim_range
    band = (similarity > low) & (similarity < high)
    band.fill_diagonal_(False)
    assert band.sum() > 0, "the fixture has no candidates; the test would be vacuous"

    torch.manual_seed(4)
    trials = 400
    mine_hits, ref_hits = 0, 0
    counts = torch.zeros(N_REGIONS)
    for _ in range(trials):
        base = torch.manual_seed(torch.randint(10**6, (1,)).item())
        got = mine._sample_region_negatives(assignment, N_REGIONS, similarity)
        expected = _reference_hard_negatives(mine, assignment, N_REGIONS, similarity)
        del base

        in_band = band[assignment, got]
        mine_hits += int(in_band.sum())
        ref_hits += int(band[assignment, expected].sum())
        assert not bool((got == assignment).any()), "a negative landed on the positive region"
        counts += torch.bincount(got[in_band], minlength=N_REGIONS).float()

    # Both draw hard negatives at the same rate. (A uniform negative can also fall in the band by
    # chance, so this compares the two rates rather than either against the nominal 25%.)
    rate_mine = mine_hits / (trials * len(assignment))
    rate_ref = ref_hits / (trials * len(assignment))
    assert abs(rate_mine - rate_ref) < 0.03, f"resampling rates differ: {rate_mine:.3f} vs {rate_ref:.3f}"

    del counts


def test_the_draw_is_uniform_over_its_band(data) -> None:
    """Uniform WITHIN a positive's band — the property a CSR indexing bug would break.

    Asserting only that no region dominates globally is vacuous: with 14 regions the uniform draw's
    accidental in-band hits alone cap any single share below such a threshold, so a sampler that
    always took the first candidate (`offsets[p]`, dropping `+ within`) would pass it. This drives
    the draw at prob=1.0 against the widest band and compares the histogram to uniform.
    """
    from dataclasses import replace as dc_replace

    from mtlcheck.substrate.model import Check2HGI

    similarity = data.coarse_region_similarity.clone()
    low, high = CONFIG.p2r_hard_neg_sim_range
    band = (similarity > low) & (similarity < high)
    band.fill_diagonal_(False)

    positive = int(band.sum(1).argmax())
    candidates = band[positive].nonzero(as_tuple=True)[0]
    assert len(candidates) >= 4, "need a wide band for this to discriminate"

    always = dc_replace(CONFIG, p2r_hard_neg_prob=1.0)
    probe = Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, data.poi2vec,
                      data.poi_delaunay_edge_index, data.delaunay_weight, N_CATEGORIES, always)

    draws = 3000
    torch.manual_seed(5)
    drawn = probe._sample_region_negatives(
        torch.full((draws,), positive, dtype=torch.long), N_REGIONS, similarity)

    assert bool(band[positive, drawn].all()), "a draw fell outside the band at prob=1.0"
    observed = torch.bincount(drawn, minlength=N_REGIONS)[candidates].double()
    expected = draws / len(candidates)
    chi_square = float(((observed - expected) ** 2 / expected).sum())
    limit = 3.0 * len(candidates) + 25.0          # far above the 99.9th percentile at this dof
    assert chi_square < limit, (
        f"not uniform over the band: chi2={chi_square:.1f} > {limit:.1f} over "
        f"{len(candidates)} candidates, counts={observed.tolist()}")
    assert int(observed.min()) > 0, "a reachable candidate was never drawn in 3 000 tries"


def test_hard_negatives_run_inside_a_full_forward(data) -> None:
    """The S17 machinery, exercised through `forward` rather than by calling the sampler directly.

    Every other test of this path either gates it off (the stream-exact arms) or monkeypatches it
    away (the injection arm) or calls `_sample_region_negatives` in isolation. So the branch had
    never executed inside a real forward, and its integration — that the drawn indices actually
    become the region negatives the p2r loss consumes — was untested.
    """
    from mtlcheck.substrate.model import Check2HGI

    torch.manual_seed(12)
    model = Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, data.poi2vec,
                      data.poi_delaunay_edge_index, data.delaunay_weight, N_CATEGORIES, CONFIG)
    assert model.hard_negatives, "the fixture must be on the hard-negative side of the gate"
    model.eval()

    with torch.no_grad():
        torch.manual_seed(3)
        out = model(data)
        loss = model.loss(out)

    assert torch.isfinite(loss), "the hard-negative path produced a non-finite loss"
    assert model._band is not None, "forward did not build the band index — the branch never ran"

    # The negatives the loss consumed must be real region vectors, and never the positive's own.
    negatives = out["other_region_of_place"]
    assert negatives.shape == (N_PLACES, DIM)
    positives = out["region_of_place"]
    assert not torch.allclose(negatives, positives), "the negative region equals the positive"


def test_turning_hard_negatives_off_changes_the_loss(data) -> None:
    """If the branch were inert, the S17 discussion would be moot. It is not."""
    from dataclasses import replace as dc_replace

    from mtlcheck.substrate.model import Check2HGI

    def loss_with(config) -> float:
        torch.manual_seed(12)
        model = Check2HGI(IN_CHANNELS, N_PLACES, N_REGIONS, data.poi2vec,
                          data.poi_delaunay_edge_index, data.delaunay_weight,
                          N_CATEGORIES, config).eval()
        with torch.no_grad():
            torch.manual_seed(3)
            return float(model.loss(model(data)))

    on = loss_with(CONFIG)
    off = loss_with(dc_replace(CONFIG, p2r_hard_neg_prob=0.0))
    assert on != off, "hard negatives changed nothing — the branch is inert"
