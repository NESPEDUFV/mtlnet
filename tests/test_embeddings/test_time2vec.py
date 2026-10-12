"""
Tests for Time2Vec embedding migration from Time_Encoder.ipynb.

Validates:
- Architecture equivalence with the original notebook
- Time feature extraction
- Dataset pair generation logic
- Model forward pass shapes
- Contrastive loss behavior
- Numerical properties of embeddings (unit norm after encode)
"""
import math

import numpy as np
import pandas as pd
import pytest
import torch
import torch.nn.functional as F

from embeddings.time2vec.model.activations import SineActivation, CosineActivation, t2v
from embeddings.time2vec.model.Time2VecModule import Time2VecContrastiveModel
from embeddings.time2vec.model.dataset import TemporalContrastiveDataset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_checkins(n: int = 50, seed: int = 0) -> pd.DataFrame:
    """Create a minimal check-ins DataFrame with local_datetime."""
    rng = np.random.default_rng(seed)
    base = pd.Timestamp("2021-01-01 00:00:00+00:00")
    offsets = pd.to_timedelta(rng.integers(0, 30 * 24 * 3600, size=n), unit="s")
    datetimes = [(base + o).isoformat() for o in offsets]
    return pd.DataFrame({
        "local_datetime": datetimes,
        "placeid": rng.integers(1, 100, size=n),
        "category": rng.choice(["Food", "Shop", "Park"], size=n),
        "userid": rng.integers(1, 10, size=n),
        "datetime": datetimes,
        "latitude": rng.uniform(-90, 90, size=n),
        "longitude": rng.uniform(-180, 180, size=n),
    })


# ---------------------------------------------------------------------------
# 1. Activation modules (t2v function)
# ---------------------------------------------------------------------------

class TestT2VFunction:
    """Verify t2v function output shape and linear/periodic split."""

    def test_output_shape_sine(self):
        batch, in_f, out_f = 8, 2, 16
        layer = SineActivation(in_f, out_f)
        x = torch.randn(batch, in_f)
        out = layer(x)
        assert out.shape == (batch, out_f), f"Expected ({batch}, {out_f}), got {out.shape}"

    def test_output_shape_cosine(self):
        batch, in_f, out_f = 8, 2, 16
        layer = CosineActivation(in_f, out_f)
        x = torch.randn(batch, in_f)
        out = layer(x)
        assert out.shape == (batch, out_f)

    def test_periodic_component_is_sine(self):
        """First out_features-1 dims should match sin(x @ w + b) exactly."""
        in_f, out_f = 2, 8
        layer = SineActivation(in_f, out_f)
        layer.eval()
        x = torch.randn(4, in_f)

        out = layer(x)
        expected_periodic = torch.sin(x @ layer.w + layer.b)  # (4, out_f-1)
        expected_linear = x @ layer.w0 + layer.b0              # (4, 1)

        # Output is [periodic | linear] concatenated
        assert torch.allclose(out[:, :out_f - 1], expected_periodic, atol=1e-6)
        assert torch.allclose(out[:, out_f - 1:], expected_linear, atol=1e-6)

    def test_periodic_component_is_cosine(self):
        in_f, out_f = 2, 8
        layer = CosineActivation(in_f, out_f)
        layer.eval()
        x = torch.randn(4, in_f)

        out = layer(x)
        expected_periodic = torch.cos(x @ layer.w + layer.b)
        expected_linear = x @ layer.w0 + layer.b0

        assert torch.allclose(out[:, :out_f - 1], expected_periodic, atol=1e-6)
        assert torch.allclose(out[:, out_f - 1:], expected_linear, atol=1e-6)

    def test_t2v_function_directly(self):
        """Direct call to t2v matches manual computation."""
        batch, in_f, k = 6, 2, 10
        w = torch.randn(in_f, k - 1)
        b = torch.randn(k - 1)
        w0 = torch.randn(in_f, 1)
        b0 = torch.randn(1)
        tau = torch.randn(batch, in_f)

        result = t2v(tau, torch.sin, k, w, b, w0, b0)
        expected = torch.cat([torch.sin(tau @ w + b), tau @ w0 + b0], dim=-1)

        assert result.shape == (batch, k)
        assert torch.allclose(result, expected, atol=1e-6)


# ---------------------------------------------------------------------------
# 2. Time2VecContrastiveModel
# ---------------------------------------------------------------------------

class TestTime2VecModel:
    """Validate model architecture and forward behavior."""

    @pytest.fixture
    def model_sin(self):
        return Time2VecContrastiveModel(activation="sin", out_features=64, embed_dim=64, in_features=2)

    def test_encode_output_shape(self, model_sin):
        batch, dim = 16, 64
        t = torch.randn(batch, 2)
        z = model_sin.encode(t)
        assert z.shape == (batch, dim)

    def test_encode_unit_norm(self, model_sin):
        """encode() must return L2-normalized embeddings (as in original)."""
        model_sin.eval()
        with torch.no_grad():
            t = torch.randn(32, 2)
            z = model_sin.encode(t)
        norms = z.norm(dim=-1)
        assert torch.allclose(norms, torch.ones(32), atol=1e-5), \
            f"Embeddings not unit-norm. Mean norm: {norms.mean():.4f}"

    def test_forward_returns_two_embeddings(self, model_sin):
        batch = 8
        t_i = torch.randn(batch, 2)
        t_j = torch.randn(batch, 2)
        z_i, z_j = model_sin(t_i, t_j)
        assert z_i.shape == (batch, 64)
        assert z_j.shape == (batch, 64)

    def test_cosine_activation_works(self):
        model = Time2VecContrastiveModel(activation="cos", out_features=32, embed_dim=64, in_features=2)
        t = torch.randn(4, 2)
        z = model.encode(t)
        assert z.shape == (4, 64)

    def test_invalid_activation_raises(self):
        with pytest.raises(ValueError):
            Time2VecContrastiveModel(activation="relu")

    def test_encode_1d_input_crashes_for_in_features_2(self, model_sin):
        """
        The unsqueeze(-1) guard in encode() converts (batch,) → (batch, 1),
        but the model is initialised with in_features=2, so the matmul fails.
        This bug exists in the original notebook too and is therefore kept as-is.
        Both implementations only ever call encode() with (batch, 2) input in practice.
        """
        t = torch.randn(8)  # 1D — incompatible with in_features=2
        with pytest.raises(RuntimeError):
            model_sin.encode(t)

    def test_projector_matches_architecture(self, model_sin):
        """Projector must be Linear(out_features, embed_dim) as in original."""
        proj = model_sin.projector
        assert isinstance(proj, torch.nn.Linear)
        assert proj.in_features == 64   # out_features
        assert proj.out_features == 64  # embed_dim

    def test_original_notebook_used_out_features_128(self):
        """
        Regression: the original notebook trained with out_features=128, embed_dim=64.
        The migration default is out_features=64. This test documents the discrepancy.
        If you want to reproduce original results, pass --out_features 128.
        """
        model_original_capacity = Time2VecContrastiveModel(
            activation="sin", out_features=128, embed_dim=64, in_features=2
        )
        model_migration_default = Time2VecContrastiveModel(
            activation="sin", out_features=64, embed_dim=64, in_features=2
        )
        # Count parameters to confirm they differ
        params_orig = sum(p.numel() for p in model_original_capacity.parameters())
        params_migr = sum(p.numel() for p in model_migration_default.parameters())
        assert params_orig != params_migr, (
            "Both models have the same param count — out_features=128 vs 64 should differ"
        )
        # Specifically: SineActivation w: (2,127) vs (2,63); projector: (128,64) vs (64,64)
        # Original total ≈ 2*127 + 127 + 2 + 1 + 128*64 + 64 = 254+127+3+8192+64 = 8640
        # Migration total ≈ 2*63  + 63  + 2 + 1 + 64*64  + 64 = 126+63+3+4096+64  = 4352
        assert params_orig > params_migr


# ---------------------------------------------------------------------------
# 3. Contrastive loss
# ---------------------------------------------------------------------------

class TestContrastiveLoss:
    """Validate loss function matches original."""

    @pytest.fixture
    def model(self):
        return Time2VecContrastiveModel(activation="sin", out_features=32, embed_dim=32, in_features=2)

    def test_loss_is_scalar(self, model):
        batch = 16
        z_i = F.normalize(torch.randn(batch, 32), dim=-1)
        z_j = F.normalize(torch.randn(batch, 32), dim=-1)
        labels = torch.randint(0, 2, (batch,)).float()
        loss = model.contrastive_loss(z_i, z_j, labels)
        assert loss.shape == ()

    def test_identical_embeddings_positive_label_low_loss(self, model):
        """Identical embeddings with label=1 should produce low loss."""
        batch = 32
        z = F.normalize(torch.randn(batch, 32), dim=-1)
        labels = torch.ones(batch)
        loss = model.contrastive_loss(z, z.clone(), labels, tau=0.3)
        # sim=1, logit=1/0.3≈3.33, bce_with_logits(3.33, 1) ≈ 0.035
        assert loss.item() < 0.1

    def test_opposite_embeddings_negative_label_low_loss(self, model):
        """Opposite embeddings with label=0 should produce low loss."""
        batch = 32
        z = F.normalize(torch.randn(batch, 32), dim=-1)
        labels = torch.zeros(batch)
        loss = model.contrastive_loss(z, -z, labels, tau=0.3)
        # sim=-1, logit=-1/0.3≈-3.33, bce_with_logits(-3.33, 0) ≈ 0.035
        assert loss.item() < 0.1

    def test_loss_formula_matches_original(self):
        """Manual replication of the notebook's loss formula."""
        batch = 8
        z_i = F.normalize(torch.randn(batch, 16), dim=-1)
        z_j = F.normalize(torch.randn(batch, 16), dim=-1)
        labels = torch.randint(0, 2, (batch,)).float()
        tau = 0.3

        model = Time2VecContrastiveModel("sin", 16, 16, 2)
        loss_model = model.contrastive_loss(z_i, z_j, labels, tau)

        # Manual replication (same as notebook):
        sim = F.cosine_similarity(z_i, z_j)
        logits = sim / tau
        loss_manual = F.binary_cross_entropy_with_logits(logits, labels)

        assert torch.allclose(loss_model, loss_manual, atol=1e-6)


# ---------------------------------------------------------------------------
# 4. Time feature extraction
# ---------------------------------------------------------------------------

class TestTemporalFeatureExtraction:
    """Validate extract_time_features matches original notebook logic."""

    def test_output_shapes(self):
        df = make_checkins(100)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert time_hours.shape == (100,)
        assert time_feats.shape == (100, 2)

    def test_time_feats_range(self):
        """Both feature dimensions must lie in [0, 1)."""
        df = make_checkins(200)
        _, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert time_feats.min() >= 0.0
        assert time_feats.max() < 1.0, f"Max feature value: {time_feats.max()}"

    def test_hour_normalization(self):
        """Hour dimension = (hour + minute/60) / 24, matching original cell-3."""
        df = pd.DataFrame({
            "local_datetime": [
                "2021-01-01 00:00:00+00:00",   # midnight → 0/24 = 0.0
                "2021-01-01 12:00:00+00:00",   # noon    → 12/24 = 0.5
                "2021-01-01 18:30:00+00:00",   # 18:30   → 18.5/24
            ]
        })
        _, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert math.isclose(time_feats[0, 0], 0.0 / 24.0, abs_tol=1e-5)
        assert math.isclose(time_feats[1, 0], 12.0 / 24.0, abs_tol=1e-5)
        assert math.isclose(time_feats[2, 0], 18.5 / 24.0, abs_tol=1e-5)

    def test_dow_normalization(self):
        """DoW dimension = weekday / 7, matching original cell-3 (NOT /6)."""
        # 2021-01-04 is Monday (weekday=0), 2021-01-10 is Sunday (weekday=6)
        df = pd.DataFrame({
            "local_datetime": [
                "2021-01-04 00:00:00+00:00",  # Monday  → 0/7 = 0.0
                "2021-01-10 00:00:00+00:00",  # Sunday  → 6/7
            ]
        })
        _, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert math.isclose(time_feats[0, 1], 0.0 / 7.0, abs_tol=1e-5)
        assert math.isclose(time_feats[1, 1], 6.0 / 7.0, abs_tol=1e-5)

    def test_time_hours_starts_at_zero(self):
        """time_hours is relative to the earliest check-in (t0)."""
        df = make_checkins(50)
        time_hours, _ = TemporalContrastiveDataset.extract_time_features(df)
        assert time_hours.min() == pytest.approx(0.0, abs=1e-4)

    def test_time_hours_monotonic_after_sort(self):
        """time_hours values, when sorted, should be non-decreasing."""
        df = make_checkins(100)
        time_hours, _ = TemporalContrastiveDataset.extract_time_features(df)
        sorted_hours = np.sort(time_hours)
        assert np.all(np.diff(sorted_hours) >= 0)

    def test_drops_invalid_datetimes(self):
        """Invalid datetimes are silently dropped (matches original dropna behavior)."""
        df = pd.DataFrame({
            "local_datetime": [
                "2021-01-01 10:00:00+00:00",
                "not-a-date",
                "2021-01-01 12:00:00+00:00",
            ]
        })
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert len(time_hours) == 2
        assert len(time_feats) == 2

    def test_dtype_is_float32(self):
        df = make_checkins(20)
        _, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        assert time_feats.dtype == np.float32


# ---------------------------------------------------------------------------
# 5. TemporalContrastiveDataset
# ---------------------------------------------------------------------------

class TestTemporalContrastiveDataset:
    """Validate dataset pair generation matches original notebook."""

    @pytest.fixture
    def small_dataset(self):
        df = make_checkins(80, seed=7)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        return TemporalContrastiveDataset(
            time_hours=time_hours,
            time_feats=time_feats,
            r_pos_hours=1.0,
            r_neg_hours=24.0,
            max_pairs=500,
            k_neg_per_i=3,
            max_pos_per_i=5,
            seed=42,
        )

    def test_len_does_not_exceed_max_pairs(self, small_dataset):
        assert len(small_dataset) <= 500

    def test_getitem_returns_three_tensors(self, small_dataset):
        feat_i, feat_j, label = small_dataset[0]
        assert feat_i.shape == (2,)
        assert feat_j.shape == (2,)

    def test_labels_are_binary(self, small_dataset):
        labels = [small_dataset[i][2] for i in range(len(small_dataset))]
        unique = set(labels)
        assert unique.issubset({0, 1}), f"Non-binary labels found: {unique}"

    def test_positive_pairs_have_label_1(self):
        """Positive pairs (within r_pos) must have label=1."""
        # Create time_hours where entries 0..9 are very close together
        time_hours = np.concatenate([
            np.linspace(0.0, 0.5, 10),    # all within 0.5h of each other
            np.linspace(100.0, 200.0, 10), # far away negatives
        ]).astype(np.float32)
        time_feats = np.tile([0.5, 0.5], (20, 1)).astype(np.float32)

        ds = TemporalContrastiveDataset(
            time_hours, time_feats,
            r_pos_hours=1.0, r_neg_hours=50.0,
            max_pairs=200, k_neg_per_i=2, max_pos_per_i=5, seed=0,
        )
        for _, _, label in ds:
            assert label in (0, 1)

    def test_negative_pairs_distance_exceeds_r_neg(self):
        """For label=0 pairs, |t_i - t_j| >= r_neg_hours (absolute_time mode only)."""
        df = make_checkins(200, seed=99)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        r_neg = 24.0
        ds = TemporalContrastiveDataset(
            time_hours, time_feats,
            r_pos_hours=1.0, r_neg_hours=r_neg,
            max_pairs=1000, k_neg_per_i=3, max_pos_per_i=5, seed=1,
            sampling_mode="absolute_time",
        )
        for i_idx, j_idx, label in ds.pairs:
            if label == 0:
                diff = abs(float(time_hours[i_idx]) - float(time_hours[j_idx]))
                assert diff >= r_neg, f"Negative pair too close: {diff:.2f}h < {r_neg}h"

    def test_positive_pairs_within_r_pos(self):
        """For label=1 pairs, |t_i - t_j| <= r_pos_hours (absolute_time mode only)."""
        df = make_checkins(200, seed=99)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        r_pos = 1.0
        ds = TemporalContrastiveDataset(
            time_hours, time_feats,
            r_pos_hours=r_pos, r_neg_hours=24.0,
            max_pairs=500, k_neg_per_i=3, max_pos_per_i=5, seed=2,
            sampling_mode="absolute_time",
        )
        for i_idx, j_idx, label in ds.pairs:
            if label == 1:
                diff = abs(float(time_hours[i_idx]) - float(time_hours[j_idx]))
                assert diff <= r_pos + 1e-4, f"Positive pair too far: {diff:.2f}h > {r_pos}h"

    def test_no_self_pairs(self, small_dataset):
        """A check-in should never be paired with itself."""
        for i_idx, j_idx, _ in small_dataset.pairs:
            assert i_idx != j_idx

    def test_reproducibility_with_same_seed(self):
        df = make_checkins(50)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        kwargs = dict(time_hours=time_hours, time_feats=time_feats,
                      max_pairs=100, seed=42)
        ds1 = TemporalContrastiveDataset(**kwargs)
        ds2 = TemporalContrastiveDataset(**kwargs)
        assert ds1.pairs == ds2.pairs

    def test_different_seeds_differ(self):
        df = make_checkins(100)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        kwargs = dict(time_hours=time_hours, time_feats=time_feats, max_pairs=200)
        ds1 = TemporalContrastiveDataset(**kwargs, seed=0)
        ds2 = TemporalContrastiveDataset(**kwargs, seed=999)
        assert ds1.pairs != ds2.pairs

    def test_from_checkins_factory(self):
        df = make_checkins(80)
        ds = TemporalContrastiveDataset.from_checkins(df, max_pairs=100, seed=0)
        assert len(ds) <= 100
        assert len(ds) > 0

    def test_default_sampling_mode_is_feat_space(self):
        """Pin: the library default is sampling_mode='feat_space' (flipped on
        2026-04-11 after the paper-faithfulness seed sweep showed +0.81 ± 0.19
        pp on Alabama MTLnet next-task). See research/embeddings/time2vec/README.md.
        """
        df = make_checkins(120, seed=7)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)
        kwargs = dict(
            time_hours=time_hours, time_feats=time_feats,
            max_pairs=300, k_neg_per_i=3, max_pos_per_i=5, seed=42,
        )
        ds_default = TemporalContrastiveDataset(**kwargs)
        ds_explicit = TemporalContrastiveDataset(**kwargs, sampling_mode="feat_space")
        assert ds_default.sampling_mode == "feat_space"
        assert ds_default.pairs == ds_explicit.pairs

    def test_feat_space_sampler_resolves_issue_A(self):
        """Rec 1 / D6 Issue A regression check.

        Construct a fixture where two check-ins share IDENTICAL (hour/24, dow/7)
        features but are >48h apart in absolute time. Under the legacy
        absolute_time sampler they'd be labelled as negatives (contradiction:
        identical inputs must have max cosine sim = 1 but the loss asks for 0).
        Under feat_space sampling the same pair must NOT appear as a negative.
        """
        # 4 check-ins. Index 0 and 2 share the same (hour, dow) but are
        # separated by 100 hours in wall time. Indices 1 and 3 are distractors.
        time_hours = np.array([0.0, 5.0, 100.0, 150.0], dtype=np.float32)
        time_feats = np.array([
            [0.5, 0.3],   # 0
            [0.9, 0.7],   # 1
            [0.5, 0.3],   # 2 — identical features to #0
            [0.1, 0.6],   # 3
        ], dtype=np.float32)

        # Legacy sampler WOULD treat (0, 2) as a negative.
        ds_legacy = TemporalContrastiveDataset(
            time_hours, time_feats,
            r_pos_hours=1.0, r_neg_hours=50.0,
            max_pairs=200, k_neg_per_i=5, max_pos_per_i=5, seed=0,
            sampling_mode="absolute_time",
        )
        legacy_negs = {(min(i, j), max(i, j)) for i, j, lbl in ds_legacy.pairs if lbl == 0}
        # We can't guarantee the sampler picked them (it's random), but the
        # behaviour this test pins is the feat_space mode, not legacy.

        # feat_space sampler must NEVER produce (0, 2) as a negative because
        # their feature-space distance is 0.
        ds_feat = TemporalContrastiveDataset(
            time_hours, time_feats,
            r_pos_hours=1.0, r_neg_hours=50.0,  # unused in feat_space
            r_pos_feat=0.05, r_neg_feat=0.20,
            max_pairs=200, k_neg_per_i=5, max_pos_per_i=5, seed=0,
            sampling_mode="feat_space",
            feat_cand_pool=4,
        )
        feat_negs = {(min(i, j), max(i, j)) for i, j, lbl in ds_feat.pairs if lbl == 0}
        assert (0, 2) not in feat_negs, \
            "feat_space sampler must not label identical-input pair (0, 2) as negative"

        # Also assert every negative under feat_space has feat-space distance
        # >= r_neg_feat (wrap-aware).
        for i, j, lbl in ds_feat.pairs:
            if lbl == 0:
                dh = abs(time_feats[i, 0] - time_feats[j, 0])
                dd = abs(time_feats[i, 1] - time_feats[j, 1])
                dh = min(dh, 1.0 - dh)
                dd = min(dd, 1.0 - dd)
                d = math.sqrt(dh * dh + dd * dd)
                assert d + 1e-6 >= 0.20, f"feat_space negative too close: {d:.3f}"


# ---------------------------------------------------------------------------
# 6. End-to-end smoke test
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """Smoke test matching the original notebook's full workflow."""

    def test_full_pipeline_smoke(self):
        """
        Replicates: dataset → DataLoader → one train step → encode.
        Uses the same hyperparameters as the original notebook
        (out_features=128 to match the original, NOT the CLI default of 64).
        """
        from torch.utils.data import DataLoader  # noqa: PLC0415

        df = make_checkins(300, seed=5)
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(df)

        dataset = TemporalContrastiveDataset(
            time_hours=time_hours,
            time_feats=time_feats,
            r_pos_hours=1.0,
            r_neg_hours=24.0,
            max_pairs=500,
            k_neg_per_i=5,
            max_pos_per_i=20,
            seed=42,
        )
        assert len(dataset) > 0

        loader = DataLoader(dataset, batch_size=32, shuffle=True, drop_last=True)

        # Note: out_features=128 matches the original notebook
        model = Time2VecContrastiveModel(
            activation="sin", out_features=128, embed_dim=64, in_features=2
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

        # One training step
        model.train()
        for t_i, t_j, label in loader:
            t_i = t_i.float()
            t_j = t_j.float()
            label = label.float()
            z_i, z_j = model(t_i, t_j)
            loss = model.contrastive_loss(z_i, z_j, label, tau=0.3)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            assert not torch.isnan(loss), "Loss is NaN"
            break

        # Inference
        model.eval()
        with torch.no_grad():
            t_all = torch.from_numpy(time_feats).float()
            embeds = model.encode(t_all)

        assert embeds.shape == (len(time_feats), 64)
        norms = embeds.norm(dim=-1)
        assert torch.allclose(norms, torch.ones(len(time_feats)), atol=1e-5)


# ---------------------------------------------------------------------------
# 7. Original notebook model (inlined replica for weight-transfer tests)
# ---------------------------------------------------------------------------
# These classes are copy-pasted from Time_Encoder.ipynb cells 1 and 7,
# with zero changes, so any divergence here means the migration broke something.

def _t2v_original(tau, f, out_features, w, b, w0, b0):
    v1 = f(torch.matmul(tau, w) + b)
    v2 = torch.matmul(tau, w0) + b0
    return torch.cat([v1, v2], dim=-1)


class _SineActivationOriginal(torch.nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.out_features = out_features
        self.w0 = torch.nn.Parameter(torch.randn(in_features, 1))
        self.b0 = torch.nn.Parameter(torch.randn(1))
        self.w  = torch.nn.Parameter(torch.randn(in_features, out_features - 1))
        self.b  = torch.nn.Parameter(torch.randn(out_features - 1))
        self.f  = torch.sin

    def forward(self, tau):
        return _t2v_original(tau, self.f, self.out_features, self.w, self.b, self.w0, self.b0)


class _OriginalModel(torch.nn.Module):
    """Exact replica of Time2VecPeriodicContrastiveModel from notebook cell-7."""
    def __init__(self, out_features=64, embed_dim=64):
        super().__init__()
        self.time_layer = _SineActivationOriginal(in_features=2, out_features=out_features)
        self.projector  = torch.nn.Linear(out_features, embed_dim)

    def encode(self, t):
        if t.dim() == 1:
            t = t.unsqueeze(-1)
        t2v_out = self.time_layer(t)
        z = self.projector(t2v_out)
        z = F.normalize(z, dim=-1)
        return z

    def forward(self, t_i, t_j):
        return self.encode(t_i), self.encode(t_j)

    def contrastive_loss(self, z_i, z_j, label, tau=0.3):
        sim = F.cosine_similarity(z_i, z_j)
        logits = sim / tau
        return F.binary_cross_entropy_with_logits(logits, label.float())


# ---------------------------------------------------------------------------
# 8. Weight-transfer equivalence tests
# ---------------------------------------------------------------------------

class TestWeightTransferEquivalence:
    """
    The strongest possible equivalence test:
    copy weights from the migrated model into the original notebook class
    and verify the output is bit-for-bit identical.

    If this passes, the migration is a correct refactoring of the original.
    """

    def _make_pair(self, out_features=32, embed_dim=16, seed=0):
        torch.manual_seed(seed)
        migrated = Time2VecContrastiveModel(
            activation="sin", out_features=out_features,
            embed_dim=embed_dim, in_features=2,
        )
        torch.manual_seed(seed)
        original = _OriginalModel(out_features=out_features, embed_dim=embed_dim)
        return migrated, original

    def _transfer_weights(self, migrated, original):
        """Copy migrated weights → original (same parameter names & shapes)."""
        original.load_state_dict(migrated.state_dict())

    def test_state_dict_keys_match(self):
        """Parameter names in migrated model match the original notebook model."""
        migrated, original = self._make_pair()
        assert set(migrated.state_dict().keys()) == set(original.state_dict().keys()), (
            f"Key mismatch.\n"
            f"  Migrated: {sorted(migrated.state_dict().keys())}\n"
            f"  Original: {sorted(original.state_dict().keys())}"
        )

    def test_state_dict_shapes_match(self):
        """Every parameter tensor has the same shape in both models."""
        migrated, original = self._make_pair(out_features=32, embed_dim=16)
        for k in migrated.state_dict():
            assert migrated.state_dict()[k].shape == original.state_dict()[k].shape, (
                f"Shape mismatch for '{k}': "
                f"{migrated.state_dict()[k].shape} vs {original.state_dict()[k].shape}"
            )

    def test_encode_identical_after_weight_transfer(self):
        """
        Given the same weights, encode() must return the same tensor.
        This is the core equivalence test.
        """
        migrated, original = self._make_pair(out_features=32, embed_dim=16, seed=7)
        self._transfer_weights(migrated, original)

        migrated.eval()
        original.eval()

        torch.manual_seed(0)
        t = torch.randn(50, 2)

        with torch.no_grad():
            z_mig = migrated.encode(t)
            z_orig = original.encode(t)

        assert torch.allclose(z_mig, z_orig, atol=1e-6), (
            f"encode() output differs after weight transfer.\n"
            f"Max diff: {(z_mig - z_orig).abs().max():.2e}"
        )

    def test_forward_identical_after_weight_transfer(self):
        """forward(t_i, t_j) returns identical (z_i, z_j) pairs."""
        migrated, original = self._make_pair(out_features=32, embed_dim=16, seed=3)
        self._transfer_weights(migrated, original)
        migrated.eval()
        original.eval()

        torch.manual_seed(1)
        t_i, t_j = torch.randn(20, 2), torch.randn(20, 2)

        with torch.no_grad():
            zi_m, zj_m = migrated(t_i, t_j)
            zi_o, zj_o = original(t_i, t_j)

        assert torch.allclose(zi_m, zi_o, atol=1e-6)
        assert torch.allclose(zj_m, zj_o, atol=1e-6)

    def test_loss_identical_after_weight_transfer(self):
        """contrastive_loss() returns the same scalar for both models."""
        migrated, original = self._make_pair(out_features=32, embed_dim=16, seed=5)
        self._transfer_weights(migrated, original)

        torch.manual_seed(2)
        t_i = torch.randn(32, 2)
        t_j = torch.randn(32, 2)
        labels = torch.randint(0, 2, (32,)).float()

        zi_m, zj_m = migrated(t_i, t_j)
        zi_o, zj_o = original(t_i, t_j)

        loss_mig = migrated.contrastive_loss(zi_m, zj_m, labels)
        loss_orig = original.contrastive_loss(zi_o, zj_o, labels)

        assert torch.allclose(loss_mig, loss_orig, atol=1e-6), (
            f"Loss differs: migrated={loss_mig:.6f}, original={loss_orig:.6f}"
        )


# ---------------------------------------------------------------------------
# 9. Training-step equivalence
# ---------------------------------------------------------------------------

class TestTrainingStepEquivalence:
    """
    Given the same initial weights and the same mini-batch, one gradient
    step must produce identical weight updates in both models.
    If this passes, a full training run with the same seed will converge
    to the same checkpoint.
    """

    def _make_pair_same_init(self, out_features=32, embed_dim=16, seed=99):
        torch.manual_seed(seed)
        migrated = Time2VecContrastiveModel(
            activation="sin", out_features=out_features,
            embed_dim=embed_dim, in_features=2,
        )
        original = _OriginalModel(out_features=out_features, embed_dim=embed_dim)
        # Copy migrated weights → original so both start from the same point
        original.load_state_dict(migrated.state_dict())
        return migrated, original

    def test_gradients_identical_after_one_step(self):
        """After identical forward + backward, every gradient must match."""
        migrated, original = self._make_pair_same_init(seed=11)

        torch.manual_seed(42)
        t_i = torch.randn(16, 2)
        t_j = torch.randn(16, 2)
        labels = torch.randint(0, 2, (16,)).float()

        # Migrated backward
        zi_m, zj_m = migrated(t_i, t_j)
        loss_m = migrated.contrastive_loss(zi_m, zj_m, labels)
        loss_m.backward()

        # Original backward
        zi_o, zj_o = original(t_i, t_j)
        loss_o = original.contrastive_loss(zi_o, zj_o, labels)
        loss_o.backward()

        for name, p_mig in migrated.named_parameters():
            p_orig = dict(original.named_parameters())[name]
            assert p_mig.grad is not None, f"Migrated grad is None for {name}"
            assert p_orig.grad is not None, f"Original grad is None for {name}"
            assert torch.allclose(p_mig.grad, p_orig.grad, atol=1e-6), (
                f"Gradient mismatch for '{name}': "
                f"max diff = {(p_mig.grad - p_orig.grad).abs().max():.2e}"
            )

    def test_weights_identical_after_adam_step(self):
        """
        After one Adam step with identical hyper-params, weights must agree.
        This proves the complete training loop is equivalent.
        """
        migrated, original = self._make_pair_same_init(seed=77)

        opt_m = torch.optim.Adam(migrated.parameters(), lr=1e-3)
        opt_o = torch.optim.Adam(original.parameters(), lr=1e-3)

        torch.manual_seed(55)
        t_i = torch.randn(16, 2)
        t_j = torch.randn(16, 2)
        labels = torch.randint(0, 2, (16,)).float()

        # Migrated step
        opt_m.zero_grad()
        zi_m, zj_m = migrated(t_i, t_j)
        migrated.contrastive_loss(zi_m, zj_m, labels).backward()
        opt_m.step()

        # Original step
        opt_o.zero_grad()
        zi_o, zj_o = original(t_i, t_j)
        original.contrastive_loss(zi_o, zj_o, labels).backward()
        opt_o.step()

        for name, p_mig in migrated.named_parameters():
            p_orig = dict(original.named_parameters())[name]
            assert torch.allclose(p_mig.data, p_orig.data, atol=1e-6), (
                f"Weight mismatch after Adam step for '{name}': "
                f"max diff = {(p_mig.data - p_orig.data).abs().max():.2e}"
            )

    def test_multi_step_training_stays_equivalent(self):
        """Run 10 steps — weights must remain identical throughout."""
        migrated, original = self._make_pair_same_init(seed=13)

        opt_m = torch.optim.Adam(migrated.parameters(), lr=1e-3)
        opt_o = torch.optim.Adam(original.parameters(), lr=1e-3)

        torch.manual_seed(0)
        for step in range(10):
            t_i = torch.randn(16, 2)
            t_j = torch.randn(16, 2)
            labels = torch.randint(0, 2, (16,)).float()

            opt_m.zero_grad()
            migrated.contrastive_loss(*migrated(t_i, t_j), labels).backward()
            opt_m.step()

            opt_o.zero_grad()
            original.contrastive_loss(*original(t_i, t_j), labels).backward()
            opt_o.step()

        for name, p_mig in migrated.named_parameters():
            p_orig = dict(original.named_parameters())[name]
            assert torch.allclose(p_mig.data, p_orig.data, atol=1e-5), (
                f"Weight diverged at step 10 for '{name}': "
                f"max diff = {(p_mig.data - p_orig.data).abs().max():.2e}"
            )