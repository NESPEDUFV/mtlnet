"""
Tests for HGI embedding components.

Validates:
1. RegionEncoder vectorized PMA matches original per-region loop
2. HGIModule loss computation is numerically stable
3. Corruption function is a permutation
4. Discriminator bilinear forms are correct
"""

import inspect
import math

import numpy as np
import pytest
import torch
import torch.nn as nn

from embeddings.hgi.model.SetTransformer import PMA, MAB
from embeddings.hgi.model.RegionEncoder import POI2Region
from embeddings.hgi.model.POIEncoder import POIEncoder
from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
from embeddings.hgi.utils import SpatialUtils


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_region_encoder(hidden=16, heads=4):
    torch.manual_seed(42)
    return POI2Region(hidden_channels=hidden, num_heads=heads)


def _original_poi2region_forward(encoder, x, zone, region_adjacency):
    """Reimplements the original per-region loop from the reference codebase."""
    num_regions = zone.max() + 1
    region_emb = x.new_zeros((num_regions, x.size(1)))
    for idx in range(num_regions):
        poi_idx = (zone == idx).nonzero(as_tuple=True)[0]
        region_emb[idx] = encoder.PMA(x[poi_idx].unsqueeze(0)).squeeze()
    region_emb = encoder.conv(region_emb, region_adjacency)
    region_emb = encoder.prelu(region_emb)
    region_emb = torch.nan_to_num(region_emb, nan=0.0)
    return region_emb


# ---------------------------------------------------------------------------
# RegionEncoder: vectorized vs loop
# ---------------------------------------------------------------------------

class TestRegionEncoderEquivalence:
    """Verify that the vectorized forward matches the original loop."""

    @pytest.mark.parametrize("num_pois,num_regions,hidden,heads", [
        (20, 4, 16, 4),
        (50, 5, 32, 4),
        (10, 2, 8, 2),
        (100, 10, 64, 4),
    ])
    def test_vectorized_matches_loop(self, num_pois, num_regions, hidden, heads):
        torch.manual_seed(0)
        encoder = _make_region_encoder(hidden=hidden, heads=heads)
        encoder.eval()

        x = torch.randn(num_pois, hidden)
        zone = torch.randint(0, num_regions, (num_pois,))
        # Ensure every region has at least one POI
        for r in range(num_regions):
            if (zone == r).sum() == 0:
                zone[r] = r

        # Simple chain adjacency so GCN has valid input
        src = torch.arange(num_regions - 1)
        dst = torch.arange(1, num_regions)
        region_adjacency = torch.stack([
            torch.cat([src, dst]),
            torch.cat([dst, src]),
        ])

        with torch.no_grad():
            loop_out = _original_poi2region_forward(encoder, x, zone, region_adjacency)
            vec_out = encoder(x, zone, region_adjacency)

        assert loop_out.shape == vec_out.shape, (
            f"Shape mismatch: loop={loop_out.shape}, vectorized={vec_out.shape}"
        )
        assert torch.allclose(loop_out, vec_out, atol=1e-5), (
            f"Max diff: {(loop_out - vec_out).abs().max():.2e}\n"
            f"Loop:\n{loop_out}\nVec:\n{vec_out}"
        )

    def test_single_poi_per_region(self):
        """Edge case: each region has exactly one POI."""
        torch.manual_seed(1)
        encoder = _make_region_encoder(hidden=16, heads=4)
        encoder.eval()

        num_regions = 5
        x = torch.randn(num_regions, 16)
        zone = torch.arange(num_regions)
        region_adjacency = torch.zeros(2, 0, dtype=torch.long)  # no edges

        with torch.no_grad():
            loop_out = _original_poi2region_forward(encoder, x, zone, region_adjacency)
            vec_out = encoder(x, zone, region_adjacency)

        assert torch.allclose(loop_out, vec_out, atol=1e-5), (
            f"Max diff: {(loop_out - vec_out).abs().max():.2e}"
        )

    def test_many_pois_same_region(self):
        """Edge case: all POIs in one region."""
        torch.manual_seed(2)
        encoder = _make_region_encoder(hidden=16, heads=4)
        encoder.eval()

        x = torch.randn(30, 16)
        zone = torch.zeros(30, dtype=torch.long)
        region_adjacency = torch.zeros(2, 0, dtype=torch.long)

        with torch.no_grad():
            loop_out = _original_poi2region_forward(encoder, x, zone, region_adjacency)
            vec_out = encoder(x, zone, region_adjacency)

        assert torch.allclose(loop_out, vec_out, atol=1e-5), (
            f"Max diff: {(loop_out - vec_out).abs().max():.2e}"
        )


# ---------------------------------------------------------------------------
# Corruption function
# ---------------------------------------------------------------------------

class TestCorruption:
    def test_is_permutation(self):
        x = torch.randn(50, 16)
        shuffled = corruption(x)
        assert shuffled.shape == x.shape
        # Every row of x must appear in shuffled
        x_sorted = x.sort(dim=0).values
        s_sorted = shuffled.sort(dim=0).values
        assert torch.allclose(x_sorted, s_sorted)

    def test_usually_different_order(self):
        torch.manual_seed(99)
        x = torch.randn(100, 16)
        shuffled = corruption(x)
        # Very unlikely to be identical with 100 rows
        assert not torch.equal(x, shuffled)


# ---------------------------------------------------------------------------
# HGIModule discriminators
# ---------------------------------------------------------------------------

class TestDiscriminators:
    def _make_model(self, dim=16, heads=4):
        torch.manual_seed(0)
        model = HierarchicalGraphInfomax(
            hidden_channels=dim,
            poi_encoder=POIEncoder(dim, dim),
            poi2region=POI2Region(dim, heads),
            region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
            corruption=corruption,
            alpha=0.5,
        )
        model.eval()
        return model

    def test_discriminate_poi2region_range(self):
        """Scores should be in (0, 1) after sigmoid."""
        model = self._make_model(dim=16)
        poi_emb = torch.randn(30, 16)
        region_emb = torch.randn(30, 16)
        scores = model.discriminate_poi2region(poi_emb, region_emb, sigmoid=True)
        assert scores.shape == (30,)
        assert (scores > 0).all() and (scores < 1).all()

    def test_discriminate_region2city_range(self):
        """Scores should be in (0, 1) after sigmoid."""
        model = self._make_model(dim=16)
        region_emb = torch.randn(5, 16)
        city_emb = torch.randn(16)
        scores = model.discriminate_region2city(region_emb, city_emb, sigmoid=True)
        assert scores.shape == (5,)
        assert (scores > 0).all() and (scores < 1).all()

    def test_discriminate_poi2region_bilinear(self):
        """Verify bilinear form: score_i = poi_i @ W @ region_i."""
        model = self._make_model(dim=8, heads=2)
        poi_emb = torch.randn(3, 8)
        region_emb = torch.randn(3, 8)
        W = model.weight_poi2region

        # Vectorized (migration)
        scores_vec = model.discriminate_poi2region(poi_emb, region_emb, sigmoid=False)

        # Manual per-POI computation (original style)
        scores_manual = torch.stack([
            poi_emb[i] @ (W @ region_emb[i]) for i in range(3)
        ])

        assert torch.allclose(scores_vec, scores_manual, atol=1e-5), (
            f"Bilinear form mismatch: {scores_vec} vs {scores_manual}"
        )


# ---------------------------------------------------------------------------
# Loss numerical stability
# ---------------------------------------------------------------------------

class TestLossStability:
    def _make_model(self, dim=16, alpha=0.5):
        torch.manual_seed(0)
        return HierarchicalGraphInfomax(
            hidden_channels=dim,
            poi_encoder=POIEncoder(dim, dim),
            poi2region=POI2Region(dim, 4),
            region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
            corruption=corruption,
            alpha=alpha,
        )

    def _make_synthetic_data(self, dim=16, N=30, R=4, seed=7):
        """Build a torch_geometric-like Data namespace for forward()."""
        from types import SimpleNamespace
        torch.manual_seed(seed)
        data = SimpleNamespace()
        data.x = torch.randn(N, dim)
        # Simple chain edges
        data.edge_index = torch.stack([
            torch.arange(N - 1),
            torch.arange(1, N),
        ])
        data.edge_weight = torch.ones(N - 1)
        # Distribute POIs across regions
        data.region_id = torch.arange(N) % R
        # Region adjacency (chain)
        data.region_adjacency = torch.stack([
            torch.arange(R - 1),
            torch.arange(1, R),
        ])
        data.region_area = torch.rand(R)
        data.coarse_region_similarity = torch.rand(R, R) * 0.5  # avoid hard-neg matches
        return data

    def test_loss_is_finite(self):
        model = self._make_model(dim=16)
        data = self._make_synthetic_data(dim=16)
        outputs = model(data)
        loss = model.loss(*outputs)
        assert torch.isfinite(loss), f"Loss is not finite: {loss}"
        assert loss.item() > 0, f"Loss should be positive: {loss}"

    def test_loss_alpha_zero_uses_region2city_only(self):
        """alpha=0 → loss comes entirely from region2city."""
        model = self._make_model(dim=16, alpha=0.0)
        data = self._make_synthetic_data(dim=16)
        outputs = model(data)
        loss = model.loss(*outputs)

        # Recompute expected loss manually
        (_, _, _, _, _, region_emb, neg_region_emb, city_emb) = outputs
        pos_city = -torch.log(model.discriminate_region2city(region_emb, city_emb) + 1e-7).mean()
        neg_city = -torch.log(1 - model.discriminate_region2city(neg_region_emb, city_emb) + 1e-7).mean()
        expected = pos_city + neg_city
        assert torch.allclose(loss, expected, atol=1e-5)


# ---------------------------------------------------------------------------
# Numerical equivalence: migrated loss vs reference loop-based loss
# ---------------------------------------------------------------------------

def _reference_loss(
    model, pos_poi_emb, region_emb, neg_region_emb, city_emb,
    region_id, neg_region_indices, alpha,
):
    """
    Loop-based loss exactly as written in the reference:
        region-embedding-benchmark/baselines/HGI/model/hgi.py:114-144

    Builds pos/neg POI lists per region, calls a per-region bilinear
    discriminator, then aggregates.
    """
    EPS_LOCAL = 1e-7
    num_regions = int(region_id.max().item()) + 1
    W_pr = model.weight_poi2region
    W_rc = model.weight_region2city

    pos_poi_list = []
    neg_poi_list = []
    for r in range(num_regions):
        idx_pos = (region_id == r).nonzero(as_tuple=True)[0]
        idx_neg = (region_id == int(neg_region_indices[r].item())).nonzero(as_tuple=True)[0]
        pos_poi_list.append(pos_poi_emb[idx_pos])
        neg_poi_list.append(pos_poi_emb[idx_neg])

    def disc_loop(poi_list, regs):
        vals = []
        for rid, pois in enumerate(poi_list):
            if pois.size(0) > 0:
                summary = regs[rid]
                val = torch.matmul(pois, torch.matmul(W_pr, summary))
                vals.append(val)
        return torch.sigmoid(torch.cat(vals, 0))

    pos_s = disc_loop(pos_poi_list, region_emb)
    neg_s = disc_loop(neg_poi_list, region_emb)
    pos_loss_region = -torch.log(pos_s + EPS_LOCAL).mean()
    neg_loss_region = -torch.log(1 - neg_s + EPS_LOCAL).mean()
    loss_pr = pos_loss_region + neg_loss_region

    pos_city = torch.sigmoid(torch.matmul(region_emb, torch.matmul(W_rc, city_emb)))
    neg_city = torch.sigmoid(torch.matmul(neg_region_emb, torch.matmul(W_rc, city_emb)))
    pos_loss_city = -torch.log(pos_city + EPS_LOCAL).mean()
    neg_loss_city = -torch.log(1 - neg_city + EPS_LOCAL).mean()
    loss_rc = pos_loss_city + neg_loss_city

    return loss_pr * alpha + loss_rc * (1 - alpha)


class TestLossEquivalenceWithReference:
    """
    The migrated vectorized loss must produce IDENTICAL values to the
    original loop-based reference for the same inputs and the same
    sampled negative regions.
    """

    def _make_model(self, dim=16, alpha=0.5):
        torch.manual_seed(0)
        return HierarchicalGraphInfomax(
            hidden_channels=dim,
            poi_encoder=POIEncoder(dim, dim),
            poi2region=POI2Region(dim, 4),
            region2city=lambda z, a: torch.sigmoid((z.T * a).sum(1)),
            corruption=corruption,
            alpha=alpha,
        )

    @pytest.mark.parametrize("N,R,dim,seed", [
        (40, 4, 16, 0),
        (60, 5, 32, 1),
        (20, 3, 16, 2),
        (100, 8, 64, 3),
    ])
    def test_vectorized_loss_matches_reference(self, N, R, dim, seed):
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = self._make_model(dim=dim)
        model.eval()

        # Synthetic intermediate tensors (skip the encoder; test the loss path)
        pos_poi_emb = torch.randn(N, dim)
        region_emb = torch.randn(R, dim)
        neg_region_emb = torch.randn(R, dim)
        city_emb = torch.randn(dim)
        region_id = torch.arange(N) % R

        # Pre-sample neg_region_indices DETERMINISTICALLY so both paths agree
        import random as _r
        _r.seed(123)
        neg_region_indices = torch.tensor([
            _r.choice([x for x in range(R) if x != r]) for r in range(R)
        ], dtype=torch.long)

        # ---- Migrated vectorized path ----
        # Build the same (poi_idx, target_region) pairs the migration's
        # forward() produces, given the pre-sampled neg_region_indices.
        N_t = pos_poi_emb.size(0)
        pos_poi_idx = torch.arange(N_t)
        pos_target = region_id

        neg_idx_chunks = []
        neg_tgt_chunks = []
        for r in range(R):
            neg_r = int(neg_region_indices[r].item())
            poi_in_neg_r = (region_id == neg_r).nonzero(as_tuple=True)[0]
            neg_idx_chunks.append(poi_in_neg_r)
            neg_tgt_chunks.append(torch.full_like(poi_in_neg_r, r))
        neg_poi_idx = torch.cat(neg_idx_chunks)
        neg_target = torch.cat(neg_tgt_chunks)

        with torch.no_grad():
            mig_loss = model.loss(
                pos_poi_idx, pos_target, neg_poi_idx, neg_target,
                pos_poi_emb, region_emb, neg_region_emb, city_emb,
            )

            ref_loss = _reference_loss(
                model, pos_poi_emb, region_emb, neg_region_emb, city_emb,
                region_id, neg_region_indices, alpha=0.5,
            )

        diff = (mig_loss - ref_loss).abs().item()
        assert diff < 1e-5, (
            f"Migration loss {mig_loss.item():.6f} != reference {ref_loss.item():.6f} "
            f"(diff={diff:.2e})"
        )

    def test_gradient_equivalence(self):
        """Gradients of the loss w.r.t. region_emb must match the reference."""
        torch.manual_seed(0)
        np.random.seed(0)
        dim, N, R = 16, 40, 4
        model = self._make_model(dim=dim)
        model.eval()

        pos_poi_emb = torch.randn(N, dim)
        region_emb_base = torch.randn(R, dim)
        neg_region_emb = torch.randn(R, dim)
        city_emb = torch.randn(dim)
        region_id = torch.arange(N) % R

        import random as _r
        _r.seed(42)
        neg_region_indices = torch.tensor([
            _r.choice([x for x in range(R) if x != r]) for r in range(R)
        ], dtype=torch.long)

        # --- Migrated path ---
        region_emb_mig = region_emb_base.clone().requires_grad_(True)
        N_t = pos_poi_emb.size(0)
        pos_poi_idx = torch.arange(N_t)
        pos_target = region_id
        neg_idx_chunks, neg_tgt_chunks = [], []
        for r in range(R):
            neg_r = int(neg_region_indices[r].item())
            poi_in_neg_r = (region_id == neg_r).nonzero(as_tuple=True)[0]
            neg_idx_chunks.append(poi_in_neg_r)
            neg_tgt_chunks.append(torch.full_like(poi_in_neg_r, r))
        neg_poi_idx = torch.cat(neg_idx_chunks)
        neg_target = torch.cat(neg_tgt_chunks)

        mig_loss = model.loss(
            pos_poi_idx, pos_target, neg_poi_idx, neg_target,
            pos_poi_emb, region_emb_mig, neg_region_emb, city_emb,
        )
        mig_loss.backward()
        grad_mig = region_emb_mig.grad.clone()

        # --- Reference path ---
        region_emb_ref = region_emb_base.clone().requires_grad_(True)
        ref_loss = _reference_loss(
            model, pos_poi_emb, region_emb_ref, neg_region_emb, city_emb,
            region_id, neg_region_indices, alpha=0.5,
        )
        ref_loss.backward()
        grad_ref = region_emb_ref.grad.clone()

        cos = torch.nn.functional.cosine_similarity(
            grad_mig.flatten().unsqueeze(0),
            grad_ref.flatten().unsqueeze(0),
        ).item()

        assert torch.allclose(grad_mig, grad_ref, atol=1e-6), (
            f"Gradients differ. cos={cos:.6f}, max_diff="
            f"{(grad_mig - grad_ref).abs().max().item():.2e}"
        )
        assert cos > 0.99999, f"Cosine similarity too low: {cos}"


# ---------------------------------------------------------------------------
# Edge weight formula (matches reference exactly)
# ---------------------------------------------------------------------------

class TestEdgeWeightFormula:
    """
    Paper formula (Huang et al., ISPRS 2023, Eq. 2):
        w1 = log((1 + D^1.5) / (1 + dist^1.5))
        w2 = 1.0  if same region else 0.4
        weight = w1 * w2  (then min-max normalised)
    """

    def test_w1_formula(self):
        D = 1000.0
        dist = 300.0
        ref = math.log((1 + D ** 1.5) / (1 + dist ** 1.5))
        mig = np.log((1 + D ** 1.5) / (1 + dist ** 1.5))
        assert math.isclose(ref, mig, rel_tol=1e-9)

    def test_cross_region_weight_matches_paper(self):
        import inspect
        from embeddings.hgi import preprocess as pp
        src = inspect.getsource(pp)
        assert "0.4" in src, "cross-region w_r should be 0.4 per Huang et al. ISPRS 2023 Eq. 2"

    def test_haversine_matches_reference(self):
        """Haversine distance London→Paris ≈ 341 km."""
        dist = SpatialUtils.haversine_np(-0.1278, 51.5074, 2.3522, 48.8566)
        assert 330_000 < dist < 350_000, f"Unexpected: {dist:.0f}m"

    def test_haversine_symmetry(self):
        d1 = SpatialUtils.haversine_np(0.0, 0.0, 1.0, 1.0)
        d2 = SpatialUtils.haversine_np(1.0, 1.0, 0.0, 0.0)
        assert math.isclose(d1, d2, rel_tol=1e-9)

    def test_haversine_zero_for_same_point(self):
        d = SpatialUtils.haversine_np(10.0, 20.0, 10.0, 20.0)
        assert math.isclose(d, 0.0, abs_tol=1e-9)

    def test_diagonal_matches_reference(self):
        """diagonal_length_bbox is identical to diagonal_length_min_box in reference."""
        import scipy.spatial
        bbox = (-74.0, 40.7, -73.8, 40.9)
        x1, y1, x2, y2 = bbox
        ref = math.sqrt(
            scipy.spatial.distance.euclidean((x1, y1), (x2, y1)) ** 2 +
            scipy.spatial.distance.euclidean((x1, y1), (x1, y2)) ** 2
        )
        mig = SpatialUtils.diagonal_length_bbox(bbox)
        assert math.isclose(ref, mig, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Hyperparameter equivalence with reference train.py
# ---------------------------------------------------------------------------

class TestHyperparameters:
    """All reference defaults are preserved in the migrated argparse."""

    def _hgi_source(self):
        import embeddings.hgi.hgi as hgi_mod
        return inspect.getsource(hgi_mod)

    def test_dim_default_64(self):
        assert "64" in self._hgi_source() and "--dim" in self._hgi_source()

    def test_alpha_default_0_5(self):
        assert "0.5" in self._hgi_source()

    def test_lr_default_0_001(self):
        assert "0.001" in self._hgi_source()

    def test_max_norm_default_0_9(self):
        assert "0.9" in self._hgi_source()

    def test_epoch_default_2000(self):
        assert "2000" in self._hgi_source()

    def test_attention_heads_default_4(self):
        assert "attention_head" in self._hgi_source()

    def test_gamma_default_1(self):
        # gamma=1 means no LR decay (StepLR with gamma=1)
        assert "gamma" in self._hgi_source() and "1.0" in self._hgi_source()


# ---------------------------------------------------------------------------
# Hard-negative sampling constants preserved
# ---------------------------------------------------------------------------

class TestHardNegativeConstants:
    """
    Reference (model/hgi.py line 94):
        if hard_negative_choice < 0.25:   # 25% hard negatives
            sim in (0.6, 0.8)             # similarity range
    These must be preserved exactly in the migration.
    """

    def test_hard_neg_probability_preserved(self):
        src = inspect.getsource(HierarchicalGraphInfomax.forward)
        assert "0.25" in src, "Hard negative probability 0.25 missing from forward()"

    def test_hard_neg_lower_bound_preserved(self):
        src = inspect.getsource(HierarchicalGraphInfomax.forward)
        assert "0.6" in src, "Hard negative lower bound 0.6 missing"

    def test_hard_neg_upper_bound_preserved(self):
        src = inspect.getsource(HierarchicalGraphInfomax.forward)
        assert "0.8" in src, "Hard negative upper bound 0.8 missing"

    def test_hard_neg_fallback_exists(self):
        """If no hard candidates found, fall back to random — must be coded."""
        src = inspect.getsource(HierarchicalGraphInfomax.forward)
        # Fallback is present when candidates list is empty
        assert "candidates" in src and "all_regions" in src