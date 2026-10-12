"""
End-to-end equivalence tests against the ACTUAL original HGI source code
imported live from region-embedding-benchmark-main.

These tests are skipped automatically if the reference repo is not present
(e.g. on CI machines without /Users/vitor/...). They are the strongest
form of validation: they prove that, given identical weights, identical
inputs, and identical RNG state, the migrated forward+loss produces
the same loss VALUE and the same GRADIENTS as the original code.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from embeddings.hgi.model.HGIModule import (
    HierarchicalGraphInfomax as MigHGI,
    corruption as mig_corruption,
)
from embeddings.hgi.model.POIEncoder import POIEncoder as MigPOIEncoder
from embeddings.hgi.model.RegionEncoder import POI2Region as MigPOI2Region

REFERENCE_REPO = Path(
    "/Users/vitor/Desktop/mestrado/temp/tarik-new/"
    "region-embedding-benchmark-main/region-embedding-benchmark-main/"
    "region-embedding/baselines/HGI/model"
)
# Deliberately skipped after plans/hgi_paper_alignment.md fixes #2-4:
# our migration now diverges from the third-party region-embedding-benchmark
# reference (channelwise PReLU, GCNConv(cached=True), cross-region w_r=0.4)
# to align with the canonical RightBank/HGI and the paper (Huang et al., ISPRS 2023).
pytestmark = pytest.mark.skip(
    reason="Intentional divergence from third-party reference after paper-alignment fixes",
)


@pytest.fixture(scope="module")
def reference():
    from tests.test_embeddings._hgi_reference_shim import load_original_hgi
    return load_original_hgi()


def _make_synthetic_data(N=40, R=4, dim=16, seed=42):
    """Build a Data-like namespace shared by both implementations."""
    g = torch.Generator().manual_seed(seed)
    data = SimpleNamespace()
    data.x = torch.randn(N, dim, generator=g)
    # Simple chain graph
    src = torch.arange(N - 1)
    dst = torch.arange(1, N)
    data.edge_index = torch.stack([
        torch.cat([src, dst]),
        torch.cat([dst, src]),
    ])
    data.edge_weight = torch.ones(2 * (N - 1))
    # Distribute POIs round-robin across regions
    data.region_id = torch.arange(N) % R
    # Region adjacency (chain)
    data.region_adjacency = torch.stack([
        torch.cat([torch.arange(R - 1), torch.arange(1, R)]),
        torch.cat([torch.arange(1, R), torch.arange(R - 1)]),
    ])
    data.region_area = torch.rand(R, generator=g)
    # Avoid hard-negative regime so the random.random() RNG behaviour
    # doesn't matter for negative selection — we set similarity well
    # below 0.6 so the (>0.6 & <0.8) test is always False and the
    # else-branch (uniform random) is taken.
    data.coarse_region_similarity = torch.rand(R, R, generator=g) * 0.5
    return data


def _build_pair(reference, dim=16, heads=4):
    """Build a migrated and an original HGI model with IDENTICAL weights."""
    torch.manual_seed(0)
    mig = MigHGI(
        hidden_channels=dim,
        poi_encoder=MigPOIEncoder(dim, dim),
        poi2region=MigPOI2Region(dim, heads),
        region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
        corruption=mig_corruption,
        alpha=0.5,
    )

    torch.manual_seed(0)
    ref = reference.HierarchicalGraphInfomax(
        hidden_channels=dim,
        poi_encoder=reference.POIEncoder(dim, dim),
        poi2region=reference.POI2Region(dim, heads),
        region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
        corruption=reference.corruption,
        alpha=0.5,
    )

    # Force exact-weight equality by copying every parameter from mig → ref
    mig_state = mig.state_dict()
    ref_state = ref.state_dict()
    # Both share the same architecture, so keys must match
    missing = set(mig_state.keys()) ^ set(ref_state.keys())
    assert not missing, f"State dict key mismatch: {missing}"
    ref.load_state_dict(mig_state)

    mig.eval()
    ref.eval()
    return mig, ref


# ---------------------------------------------------------------------------
# Equivalence tests
# ---------------------------------------------------------------------------

class TestForwardLossAgainstActualReference:
    """
    Run the migration and the actual unmodified reference side-by-side
    on identical inputs with identical RNG state, and compare the loss
    values and gradients of every shared parameter.
    """

    def _run_pair(self, mig, ref, data, seed=123):
        """Run forward+loss+backward on both, return (mig_loss, ref_loss)."""
        # The hard-negative sampling inside forward() uses Python's `random`
        # module. We seed both runs identically so they sample the same
        # negative regions.
        random.seed(seed)
        torch.manual_seed(seed)
        outputs_mig = mig(data)
        loss_mig = mig.loss(*outputs_mig)

        random.seed(seed)
        torch.manual_seed(seed)
        out_ref = ref(data)
        loss_ref = ref.loss(*out_ref)

        return loss_mig, loss_ref

    @pytest.mark.parametrize("N,R,dim,heads,seed", [
        (40, 4, 16, 4, 0),
        (60, 5, 16, 4, 1),
        (24, 3, 32, 4, 2),
        (80, 8, 16, 2, 3),
    ])
    def test_loss_value_matches_reference(self, reference, N, R, dim, heads, seed):
        mig, ref = _build_pair(reference, dim=dim, heads=heads)
        data = _make_synthetic_data(N=N, R=R, dim=dim, seed=seed)

        loss_mig, loss_ref = self._run_pair(mig, ref, data, seed=seed + 100)

        diff = (loss_mig - loss_ref).abs().item()
        assert diff < 1e-5, (
            f"Loss mismatch (N={N}, R={R}, dim={dim}, heads={heads}, seed={seed}):\n"
            f"  migration: {loss_mig.item():.8f}\n"
            f"  reference: {loss_ref.item():.8f}\n"
            f"  diff:      {diff:.2e}"
        )

    def test_loss_value_default_config(self, reference):
        """Sanity check with the canonical (dim=64, heads=4) config."""
        mig, ref = _build_pair(reference, dim=64, heads=4)
        data = _make_synthetic_data(N=100, R=10, dim=64, seed=7)
        loss_mig, loss_ref = self._run_pair(mig, ref, data, seed=99)

        diff = (loss_mig - loss_ref).abs().item()
        assert diff < 1e-4, (
            f"diff={diff:.2e}, mig={loss_mig.item()}, ref={loss_ref.item()}"
        )

    def test_gradients_match_reference(self, reference):
        """Gradients of every shared parameter must match."""
        mig, ref = _build_pair(reference, dim=16, heads=4)
        mig.train()
        ref.train()
        data = _make_synthetic_data(N=40, R=4, dim=16, seed=11)

        # Migration backward
        random.seed(555)
        torch.manual_seed(555)
        out_mig = mig(data)
        loss_mig = mig.loss(*out_mig)
        loss_mig.backward()

        # Reference backward (fresh model with same weights)
        torch.manual_seed(0)
        ref2 = reference.HierarchicalGraphInfomax(
            hidden_channels=16,
            poi_encoder=reference.POIEncoder(16, 16),
            poi2region=reference.POI2Region(16, 4),
            region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
            corruption=reference.corruption,
            alpha=0.5,
        )
        ref2.load_state_dict(mig.state_dict())
        ref2.train()

        random.seed(555)
        torch.manual_seed(555)
        out_ref = ref2(data)
        loss_ref = ref2.loss(*out_ref)
        loss_ref.backward()

        # Compare gradients of every parameter that exists in both
        mig_params = dict(mig.named_parameters())
        ref_params = dict(ref2.named_parameters())

        report = []
        for name in mig_params:
            if name not in ref_params:
                continue
            g_mig = mig_params[name].grad
            g_ref = ref_params[name].grad
            if g_mig is None or g_ref is None:
                continue
            max_diff = (g_mig - g_ref).abs().max().item()
            report.append((name, max_diff))

        worst = max(report, key=lambda t: t[1])
        for name, d in report:
            assert d < 1e-5, (
                f"Gradient mismatch on `{name}`: max abs diff = {d:.2e}\n"
                f"All params:\n" + "\n".join(f"  {n}: {d2:.2e}" for n, d2 in report)
            )
        # Sanity print on success
        assert worst[1] < 1e-5
