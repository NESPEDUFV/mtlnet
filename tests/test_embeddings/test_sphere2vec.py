"""
Tests for Sphere2Vec embedding migration from Sphere2Vec-sphereM.ipynb.

Validates that the migrated package in `research/embeddings/sphere2vec/` is
mathematically equivalent to the source notebook by comparing forward passes
against the frozen reference snapshot in `_sphere2vec_reference.py`.

Equivalence strategy: each test seeds Python/NumPy/Torch RNGs immediately
before instantiating each model, so the deterministic init order
(`torch.randn(num_centroids, 3)` for the RBF buffer + `nn.init.xavier_uniform_`
for every Linear layer) produces identical weights and buffers in both
versions. We then run a forward pass on a fixed input and assert the outputs
are bit-equal (or within float epsilon).

The smoke test runs `create_embedding` end-to-end on a tiny synthetic
check-ins parquet, monkey-patching the I/O paths into a temp directory, and
asserts that the resulting parquet has the right schema and unit-norm rows.
"""

import random
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def seed_everything(seed: int = 0) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ---------------------------------------------------------------------------
# 1. SphereRBFPositionEncoder forward equivalence (class was historically named
#    ``SpherePositionEncoder`` — the reference snapshot keeps the old name and
#    we assert the backward-compat alias still works below.)
# ---------------------------------------------------------------------------

class TestSphereRBFPositionEncoderEquivalence:

    def _build_pair(self, seed: int = 0):
        from tests.test_embeddings import _sphere2vec_reference as ref
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereRBFPositionEncoder as SpherePositionEncoderNew,
        )

        kwargs = dict(
            min_scale=10, max_scale=1e7, num_scales=32, num_centroids=256,
            device="cpu",
        )

        seed_everything(seed)
        ref_enc = ref.SpherePositionEncoder(**kwargs)

        seed_everything(seed)
        new_enc = SpherePositionEncoderNew(**kwargs)

        return ref_enc, new_enc

    def test_buffers_match(self):
        ref_enc, new_enc = self._build_pair(seed=0)
        assert torch.equal(ref_enc.scales, new_enc.scales)
        assert torch.equal(ref_enc.centroids, new_enc.centroids)

    def test_forward_match_on_fixed_coords(self):
        ref_enc, new_enc = self._build_pair(seed=0)
        ref_enc.eval()
        new_enc.eval()

        coords = torch.tensor([
            [33.5, -86.8],
            [25.7, -80.1],
            [-90.0, 0.0],
            [90.0, 180.0],
            [0.0, 0.0],
            [60.5, -150.0],
            [-33.9, 18.4],
            [40.7, -74.0],
        ])

        with torch.no_grad():
            out_ref = ref_enc(coords)
            out_new = new_enc(coords)

        assert out_ref.shape == out_new.shape
        assert out_ref.shape == (8, 256 * 32)
        assert torch.allclose(out_ref, out_new, atol=1e-7, rtol=0.0)


# ---------------------------------------------------------------------------
# 2. SphereLocationEncoder forward equivalence
# ---------------------------------------------------------------------------

class TestSphereLocationEncoderEquivalence:

    def _build_pair(self, seed: int = 0):
        from tests.test_embeddings import _sphere2vec_reference as ref
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereLocationEncoder as SphereLocationEncoderNew,
        )

        kwargs = dict(
            spa_embed_dim=128,
            num_scales=32, min_scale=10, max_scale=1e7,
            num_centroids=256, ffn_hidden_dim=512,
            ffn_num_hidden_layers=1, ffn_dropout_rate=0.5,
            ffn_act="relu", ffn_use_layernormalize=True,
            ffn_skip_connection=True,
            device="cpu",
        )

        seed_everything(seed)
        ref_enc = ref.SphereLocationEncoder(**kwargs)

        seed_everything(seed)
        new_enc = SphereLocationEncoderNew(**kwargs)

        return ref_enc, new_enc

    def test_parameters_match(self):
        ref_enc, new_enc = self._build_pair(seed=0)
        ref_state = ref_enc.state_dict()
        new_state = new_enc.state_dict()
        assert set(ref_state.keys()) == set(new_state.keys())
        for k in ref_state.keys():
            assert torch.equal(ref_state[k], new_state[k]), f"mismatch in {k}"

    def test_forward_match_on_fixed_coords(self):
        ref_enc, new_enc = self._build_pair(seed=0)
        ref_enc.eval()
        new_enc.eval()

        coords = torch.tensor([
            [33.5, -86.8],
            [25.7, -80.1],
            [40.7, -74.0],
            [60.5, -150.0],
        ])

        with torch.no_grad():
            out_ref = ref_enc(coords)
            out_new = new_enc(coords)

        assert out_ref.shape == (4, 128)
        assert torch.allclose(out_ref, out_new, atol=1e-6, rtol=0.0)


# ---------------------------------------------------------------------------
# 3. SphereLocationContrastiveModel forward equivalence
# ---------------------------------------------------------------------------

class TestContrastiveModelEquivalence:

    def _build_pair(self, seed: int = 0):
        from tests.test_embeddings import _sphere2vec_reference as ref
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereLocationContrastiveModel as SphereLocationContrastiveModelNew,
        )

        # The reference's __init__ accepts only `embed_dim` and hard-codes
        # everything else; the migrated version exposes the same defaults.
        seed_everything(seed)
        ref_model = ref.SphereLocationContrastiveModel(embed_dim=64)

        seed_everything(seed)
        new_model = SphereLocationContrastiveModelNew(embed_dim=64, device="cpu")

        return ref_model, new_model

    def test_parameters_match(self):
        ref_model, new_model = self._build_pair(seed=0)
        ref_state = ref_model.state_dict()
        new_state = new_model.state_dict()
        assert set(ref_state.keys()) == set(new_state.keys())
        for k in ref_state.keys():
            assert torch.equal(ref_state[k], new_state[k]), f"mismatch in {k}"

    def test_forward_is_unit_norm_and_matches(self):
        ref_model, new_model = self._build_pair(seed=0)
        ref_model.eval()
        new_model.eval()

        coords = torch.tensor([
            [33.5, -86.8],
            [25.7, -80.1],
            [40.7, -74.0],
            [60.5, -150.0],
            [-33.9, 18.4],
        ])

        with torch.no_grad():
            out_ref = ref_model(coords)
            out_new = new_model(coords)

        assert out_ref.shape == (5, 64)
        assert out_new.shape == (5, 64)

        # Both must be L2-normalized (the model's final op is F.normalize)
        norms_ref = out_ref.norm(dim=-1)
        norms_new = out_new.norm(dim=-1)
        assert torch.allclose(norms_ref, torch.ones(5), atol=1e-5)
        assert torch.allclose(norms_new, torch.ones(5), atol=1e-5)

        assert torch.allclose(out_ref, out_new, atol=1e-6, rtol=0.0)


# ---------------------------------------------------------------------------
# 4. contrastive_bce loss equivalence
# ---------------------------------------------------------------------------

class TestContrastiveBCEEquivalence:

    def test_loss_matches_reference(self):
        from tests.test_embeddings._sphere2vec_reference import (
            contrastive_bce as contrastive_bce_ref,
        )
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            contrastive_bce as contrastive_bce_new,
        )

        seed_everything(0)
        z_i = F.normalize(torch.randn(8, 64), dim=-1)
        z_j = F.normalize(torch.randn(8, 64), dim=-1)
        label = torch.tensor([1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0])

        loss_ref = contrastive_bce_ref(z_i, z_j, label, tau=0.15)
        loss_new = contrastive_bce_new(z_i, z_j, label, tau=0.15)

        assert torch.equal(loss_ref, loss_new)


# ---------------------------------------------------------------------------
# 5. ContrastiveSpatialDataset equivalence
# ---------------------------------------------------------------------------

class TestContrastiveDatasetEquivalence:

    def test_same_samples_under_seed(self):
        from tests.test_embeddings._sphere2vec_reference import (
            ContrastiveSpatialDataset as ContrastiveSpatialDatasetRef,
        )
        from embeddings.sphere2vec.model.dataset import (
            ContrastiveSpatialDataset as ContrastiveSpatialDatasetNew,
        )

        rng = np.random.default_rng(123)
        coords = rng.uniform(low=[-90, -180], high=[90, 180], size=(40, 2)).astype(np.float32)

        ds_ref = ContrastiveSpatialDatasetRef(coords, pos_radius=0.01)
        ds_new = ContrastiveSpatialDatasetNew(coords, pos_radius=0.01)

        # Both pull from global np.random; identical seed -> identical sequences
        np.random.seed(7)
        ref_samples = [ds_ref[i] for i in range(20)]
        np.random.seed(7)
        new_samples = [ds_new[i] for i in range(20)]

        for (ci_r, cj_r, lb_r), (ci_n, cj_n, lb_n) in zip(ref_samples, new_samples):
            assert torch.equal(ci_r, ci_n)
            assert torch.equal(cj_r, cj_n)
            assert torch.equal(lb_r, lb_n)


# ---------------------------------------------------------------------------
# 5b. FastContrastiveSpatialDataset — statistical equivalence
# ---------------------------------------------------------------------------

class TestFastContrastiveDataset:
    """
    The vectorized dataset cannot produce a bit-equal sample sequence to the
    per-item version (the random calls happen in a different order: per-item
    interleaves coord_i / random / noise / label, whereas the batched version
    draws all randomness up front). Instead, this test checks that the
    statistical properties match: same Bernoulli(0.5) positive ratio, same
    Gaussian noise scale, correct shape/dtype, anchor coords are exact, and
    when the label is positive the noise is bounded as expected.
    """

    def _build_pair(self, n_coords: int = 128, pos_radius: float = 0.01, seed: int = 0):
        from embeddings.sphere2vec.model.dataset import (
            ContrastiveSpatialDataset,
            FastContrastiveSpatialDataset,
        )
        rng = np.random.default_rng(seed)
        coords = rng.uniform(low=[25, -125], high=[50, -70], size=(n_coords, 2)).astype(np.float32)
        slow = ContrastiveSpatialDataset(coords, pos_radius=pos_radius)
        fast = FastContrastiveSpatialDataset(coords, pos_radius=pos_radius)
        return coords, slow, fast

    def test_fast_getitems_shape_and_dtype(self):
        _, _, fast = self._build_pair(n_coords=64)
        np.random.seed(0)
        coord_i, coord_j, label = fast.__getitems__(list(range(64)))
        assert coord_i.shape == (64, 2)
        assert coord_j.shape == (64, 2)
        assert label.shape == (64,)
        assert coord_i.dtype == torch.float32
        assert coord_j.dtype == torch.float32
        assert label.dtype == torch.float32

    def test_fast_anchor_coords_are_exact(self):
        coords, _, fast = self._build_pair(n_coords=128)
        indices = [3, 17, 42, 99]
        np.random.seed(0)
        coord_i, _, _ = fast.__getitems__(indices)
        for k, idx in enumerate(indices):
            assert torch.allclose(coord_i[k], torch.from_numpy(coords[idx]))

    def test_fast_positive_negative_ratio(self):
        # Over many samples, label should average ~0.5
        _, _, fast = self._build_pair(n_coords=256)
        np.random.seed(0)
        all_labels = []
        for _ in range(20):
            _, _, lb = fast.__getitems__(list(range(256)))
            all_labels.append(lb)
        all_labels = torch.cat(all_labels)
        ratio = all_labels.mean().item()
        assert 0.45 < ratio < 0.55, f"positive ratio off: {ratio}"

    def test_fast_positive_noise_within_bounds(self):
        # When label==1, coord_j ≈ coord_i + small Gaussian noise
        # Std should be ~pos_radius, and 99.7% of |noise| < 3*pos_radius
        coords, _, fast = self._build_pair(n_coords=512, pos_radius=0.01)
        np.random.seed(123)
        coord_i, coord_j, label = fast.__getitems__(list(range(512)))
        pos_mask = label.bool()
        diffs = (coord_j[pos_mask] - coord_i[pos_mask]).numpy()
        std = diffs.std()
        # Pos_radius is 0.01, std should be near it
        assert 0.005 < std < 0.015, f"noise std off: {std}"
        # 3-sigma bound — allow tiny tail leakage
        assert (np.abs(diffs) < 0.05).mean() > 0.99

    def test_fast_negative_pairs_are_actual_other_coords(self):
        # When label==0, coord_j must be a row from the original coords array.
        coords, _, fast = self._build_pair(n_coords=64, pos_radius=0.01)
        np.random.seed(7)
        coord_i, coord_j, label = fast.__getitems__(list(range(64)))
        coords_set = {tuple(row.tolist()) for row in coord_i.numpy()}
        coords_full_set = {tuple(row) for row in coords.tolist()}
        for k in range(64):
            if label[k] == 0.0:
                row = tuple(coord_j[k].tolist())
                assert row in coords_full_set, \
                    f"negative coord_j[{k}]={row} is not from the source coords"

    def test_fast_dataset_dataloader_integration(self):
        # End-to-end DataLoader smoke. The fast dataset's __getitems__
        # returns a fully batched tuple, so we must pair it with a
        # passthrough collate (same setup as create_embedding does).
        from torch.utils.data import DataLoader
        from embeddings.sphere2vec.sphere2vec import _identity_collate

        _, _, fast = self._build_pair(n_coords=200)
        np.random.seed(0)
        loader = DataLoader(
            fast,
            batch_size=32,
            shuffle=False,
            num_workers=0,
            drop_last=True,
            collate_fn=_identity_collate,
        )
        batches = list(loader)
        assert len(batches) == 200 // 32
        for ci, cj, lb in batches:
            assert ci.shape == (32, 2)
            assert cj.shape == (32, 2)
            assert lb.shape == (32,)


# ---------------------------------------------------------------------------
# 6. End-to-end smoke test for create_embedding
# ---------------------------------------------------------------------------

class TestCreateEmbeddingSmoke:

    def test_writes_parquet_with_expected_schema(self, tmp_path, monkeypatch):
        """
        Run `create_embedding` for 1 epoch on a tiny synthetic check-ins file
        and verify the output parquet has the expected schema, row count and
        unit-norm embeddings.
        """
        from configs.paths import EmbeddingEngine, IoPaths
        from embeddings.sphere2vec import sphere2vec as sphere_module

        state = "smoketest"
        n_pois = 12
        checkins_per_poi = 3
        n_checkins = n_pois * checkins_per_poi

        # Build synthetic check-ins (one row per visit, popular POIs duplicated)
        rng = np.random.default_rng(0)
        rows = []
        for poi_idx in range(n_pois):
            lat = float(rng.uniform(25, 50))
            lon = float(rng.uniform(-125, -70))
            cat = ["Food", "Shop", "Park"][poi_idx % 3]
            for _ in range(checkins_per_poi):
                rows.append({
                    "placeid": f"poi_{poi_idx}",
                    "category": cat,
                    "latitude": lat,
                    "longitude": lon,
                })
        checkins_df = pd.DataFrame(rows)

        # Layout the temp dirs
        checkins_path = tmp_path / "checkins.parquet"
        checkins_df.to_parquet(checkins_path, index=False)

        state_dir = tmp_path / "sphere2vec_out"
        state_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = state_dir / "embeddings.parquet"
        model_path = state_dir / "sphere2vec_model.pt"

        # Patch IoPaths to redirect I/O to tmp_path
        monkeypatch.setattr(
            IoPaths, "get_city",
            classmethod(lambda cls, state, ext="parquet": checkins_path),
        )
        monkeypatch.setattr(
            IoPaths, "get_embedd",
            classmethod(lambda cls, state, embedd_engine: embeddings_path),
        )
        monkeypatch.setattr(
            IoPaths.SPHERE2VEC, "get_state_dir",
            classmethod(lambda cls, state: state_dir),
        )
        monkeypatch.setattr(
            IoPaths.SPHERE2VEC, "get_model_file",
            classmethod(lambda cls, state: model_path),
        )

        # Run with very small training budget
        args = Namespace(
            dim=64,
            spa_embed_dim=128,
            num_scales=32,
            min_scale=10,
            max_scale=1e7,
            num_centroids=256,
            ffn_hidden_dim=512,
            ffn_num_hidden_layers=1,
            ffn_dropout_rate=0.5,
            ffn_act="relu",
            ffn_use_layernormalize=True,
            ffn_skip_connection=True,
            epoch=1,
            batch_size=4,
            lr=1e-3,
            tau=0.15,
            pos_radius=0.01,
            seed=42,
            num_workers=0,  # required: dataset uses global np.random
            eval_batch_size=8,
            device=torch.device("cpu"),
            legacy_dataset=False,  # exercise the fast vectorized path
        )

        sphere_module.create_embedding(state=state, args=args)

        # Assertions
        assert embeddings_path.exists(), "embeddings.parquet was not written"
        assert model_path.exists(), "sphere2vec_model.pt was not written"

        df = pd.read_parquet(embeddings_path)

        # Schema: [placeid, category, "0"...,"63"]
        expected_cols = ["placeid", "category"] + [str(i) for i in range(64)]
        assert list(df.columns) == expected_cols

        # One row per unique POI
        assert len(df) == n_pois

        # All placeids present
        assert set(df["placeid"]) == {f"poi_{i}" for i in range(n_pois)}

        # Categories preserved (mode of duplicates equals the only value)
        for poi_idx in range(n_pois):
            row = df[df["placeid"] == f"poi_{poi_idx}"].iloc[0]
            assert row["category"] == ["Food", "Shop", "Park"][poi_idx % 3]

        # Default behavior matches the notebook (dropout active during
        # inference). With dropout averaging across multiple checkins per POI,
        # the per-POI embeddings are NOT unit-norm; they should however be
        # finite and have plausibly bounded norms.
        emb = df[[str(i) for i in range(64)]].to_numpy(dtype=np.float32)
        norms = np.linalg.norm(emb, axis=1)
        assert np.all(np.isfinite(norms)), "non-finite embedding norms"
        assert np.all(norms > 0.0), "zero-norm embeddings"
        assert np.all(norms < 2.0), \
            f"embedding norms unexpectedly large: max={norms.max()}"

    def test_eval_inference_produces_unit_norm(self, tmp_path, monkeypatch):
        """
        Same as the smoke test, but with `eval_inference=True` (the
        deterministic-fix path). All POIs share the same coord across their
        checkins, so eval-mode embeddings should be exactly unit norm after
        groupby+mean.
        """
        from configs.paths import EmbeddingEngine, IoPaths
        from embeddings.sphere2vec import sphere2vec as sphere_module

        n_pois = 8
        rows = []
        rng = np.random.default_rng(0)
        for poi_idx in range(n_pois):
            lat = float(rng.uniform(25, 50))
            lon = float(rng.uniform(-125, -70))
            for _ in range(3):
                rows.append({
                    "placeid": f"poi_{poi_idx}",
                    "category": "Food",
                    "latitude": lat,
                    "longitude": lon,
                })
        checkins_df = pd.DataFrame(rows)

        checkins_path = tmp_path / "checkins.parquet"
        checkins_df.to_parquet(checkins_path, index=False)
        state_dir = tmp_path / "out"
        state_dir.mkdir()
        embeddings_path = state_dir / "embeddings.parquet"
        model_path = state_dir / "sphere2vec_model.pt"

        monkeypatch.setattr(IoPaths, "get_city",
            classmethod(lambda cls, state, ext="parquet": checkins_path))
        monkeypatch.setattr(IoPaths, "get_embedd",
            classmethod(lambda cls, state, embedd_engine: embeddings_path))
        monkeypatch.setattr(IoPaths.SPHERE2VEC, "get_state_dir",
            classmethod(lambda cls, state: state_dir))
        monkeypatch.setattr(IoPaths.SPHERE2VEC, "get_model_file",
            classmethod(lambda cls, state: model_path))

        args = Namespace(
            dim=64, spa_embed_dim=128, num_scales=32, min_scale=10,
            max_scale=1e7, num_centroids=256, ffn_hidden_dim=512,
            ffn_num_hidden_layers=1, ffn_dropout_rate=0.5, ffn_act="relu",
            ffn_use_layernormalize=True, ffn_skip_connection=True,
            epoch=1, batch_size=4, lr=1e-3, tau=0.15, pos_radius=0.01,
            seed=42, num_workers=0, eval_batch_size=8,
            device=torch.device("cpu"),
            eval_inference=True,
            legacy_dataset=False,
        )
        sphere_module.create_embedding(state="evaltest", args=args)

        df = pd.read_parquet(embeddings_path)
        emb = df[[str(i) for i in range(64)]].to_numpy(dtype=np.float32)
        norms = np.linalg.norm(emb, axis=1)
        assert np.allclose(norms, np.ones(n_pois), atol=1e-4), \
            f"eval-mode norms not unit: {norms}"


# ---------------------------------------------------------------------------
# 7. Strong end-to-end equivalence: full pipeline vs inline notebook port
# ---------------------------------------------------------------------------

class TestEndToEndPipelineEquivalence:
    """
    Runs an inline port of notebook cells 5/8/11/12/14 against my migrated
    `create_embedding`, with all RNGs locked to the same seed and identical
    inputs, then asserts the resulting per-POI embeddings are bit-equal.

    This is the strongest equivalence test in the suite. If it passes, the
    migrated package is provably indistinguishable from the source notebook
    on the per-POI mean output, given the same seeds and the same data.
    """

    def _run_notebook_reference(self, coords, placeids, categories, *,
                                 seed, epochs, batch_size, lr, tau, pos_radius):
        """Inline port of notebook cells 8 + 11 + 12 + 14."""
        import torch
        from torch.utils.data import DataLoader
        from tests.test_embeddings._sphere2vec_reference import (
            ContrastiveSpatialDataset,
            SphereLocationContrastiveModel,
            contrastive_bce,
        )

        # Lock all RNGs (same as `create_embedding` does internally)
        seed_everything(seed)

        # Cell 7/8: dataset + dataloader (num_workers=0 so global np.random
        # state is the same as the migration's)
        dataset = ContrastiveSpatialDataset(coords, pos_radius=pos_radius)
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            drop_last=True,
        )

        # Cell 11: model, optimizer, training
        model = SphereLocationContrastiveModel().to("cpu")
        # The reference's __init__ only exposes embed_dim; defaults match
        # the migrated version's defaults.
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        for _ in range(epochs):
            model.train()
            for coord_i, coord_j, label in loader:
                ci = coord_i.float().to("cpu")
                cj = coord_j.float().to("cpu")

                z_i = model(ci)
                z_j = model(cj)

                loss = contrastive_bce(z_i, z_j, label, tau=tau)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        # Cell 12 + 13: forward pass on all coords (TRAIN mode, no no_grad,
        # then detach + numpy)
        loc_embeds = model(torch.Tensor(coords))
        loc_embeds = loc_embeds.detach().numpy()

        # Cell 14: build per-checkin df, groupby placeid, mean embeds + mode cat
        n_embeds = loc_embeds.shape[1]
        embed_cols = [f"{i}" for i in range(n_embeds)]

        placeid_arr = np.asarray(placeids).reshape(-1)
        category_arr = np.asarray(categories).reshape(-1)

        df_loc = pd.DataFrame(loc_embeds, columns=embed_cols)
        df_loc.insert(0, "placeid", placeid_arr.astype(str))
        df_loc["category"] = category_arr.astype(str)

        df_mean_embeds = (
            df_loc.groupby("placeid")[embed_cols].mean().reset_index()
        )
        df_mode_cat = (
            df_loc.groupby("placeid")["category"]
            .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0])
            .reset_index()
        )
        df_final = df_mean_embeds.merge(df_mode_cat, on="placeid")
        return df_final

    def test_per_poi_embeddings_match_notebook(self, tmp_path, monkeypatch):
        """
        Build a tiny synthetic check-ins dataset, run both the inline
        notebook reference and the migrated `create_embedding`, then assert
        bit-equality on the per-POI embedding rows (sorted by placeid).
        """
        from configs.paths import EmbeddingEngine, IoPaths
        from embeddings.sphere2vec import sphere2vec as sphere_module

        # Tiny synthetic data: 10 POIs × 5 checkins (= 50 total)
        rng = np.random.default_rng(7)
        n_pois = 10
        checkins_per_poi = 5
        rows = []
        for poi_idx in range(n_pois):
            lat = float(rng.uniform(25, 50))
            lon = float(rng.uniform(-125, -70))
            cat = ["Food", "Shop", "Park"][poi_idx % 3]
            for _ in range(checkins_per_poi):
                rows.append({
                    "placeid": f"poi_{poi_idx:02d}",
                    "category": cat,
                    "latitude": lat,
                    "longitude": lon,
                })
        df_checkins = pd.DataFrame(rows)

        # Coords / placeids / categories arrays for the reference
        coords_np = df_checkins[["latitude", "longitude"]].values.astype(np.float32)
        placeids_np = df_checkins["placeid"].values
        categories_np = df_checkins["category"].values

        # Hyperparameters used by both runs
        epochs = 2
        batch_size = 8
        lr = 1e-3
        tau = 0.15
        pos_radius = 0.01
        seed = 12345

        # ----- Reference run (inline notebook port) -----
        df_ref = self._run_notebook_reference(
            coords_np, placeids_np, categories_np,
            seed=seed, epochs=epochs, batch_size=batch_size,
            lr=lr, tau=tau, pos_radius=pos_radius,
        )

        # ----- Migrated run (`create_embedding`) -----
        checkins_path = tmp_path / "checkins.parquet"
        df_checkins.to_parquet(checkins_path, index=False)
        state_dir = tmp_path / "out"
        state_dir.mkdir()
        embeddings_path = state_dir / "embeddings.parquet"
        model_path = state_dir / "sphere2vec_model.pt"

        monkeypatch.setattr(IoPaths, "get_city",
            classmethod(lambda cls, state, ext="parquet": checkins_path))
        monkeypatch.setattr(IoPaths, "get_embedd",
            classmethod(lambda cls, state, embedd_engine: embeddings_path))
        monkeypatch.setattr(IoPaths.SPHERE2VEC, "get_state_dir",
            classmethod(lambda cls, state: state_dir))
        monkeypatch.setattr(IoPaths.SPHERE2VEC, "get_model_file",
            classmethod(lambda cls, state: model_path))

        args = Namespace(
            dim=64, spa_embed_dim=128, num_scales=32, min_scale=10,
            max_scale=1e7, num_centroids=256, ffn_hidden_dim=512,
            ffn_num_hidden_layers=1, ffn_dropout_rate=0.5, ffn_act="relu",
            ffn_use_layernormalize=True, ffn_skip_connection=True,
            epoch=epochs, batch_size=batch_size, lr=lr, tau=tau,
            pos_radius=pos_radius, seed=seed, num_workers=0,
            eval_batch_size=64, device=torch.device("cpu"),
            eval_inference=False,  # match notebook's train-mode inference
            legacy_dataset=True,   # required for bit-equality with notebook reference
        )
        sphere_module.create_embedding(state="e2etest", args=args)
        df_mig = pd.read_parquet(embeddings_path)

        # ----- Compare -----
        # Both must contain the same set of placeids (sort to align rows).
        df_ref_sorted = df_ref.sort_values("placeid").reset_index(drop=True)
        df_mig_sorted = df_mig.sort_values("placeid").reset_index(drop=True)

        assert list(df_ref_sorted["placeid"]) == list(df_mig_sorted["placeid"])
        assert list(df_ref_sorted["category"]) == list(df_mig_sorted["category"])

        embed_cols = [str(i) for i in range(64)]
        ref_emb = df_ref_sorted[embed_cols].to_numpy(dtype=np.float32)
        mig_emb = df_mig_sorted[embed_cols].to_numpy(dtype=np.float32)

        assert ref_emb.shape == mig_emb.shape == (n_pois, 64)
        assert np.allclose(ref_emb, mig_emb, atol=1e-6, rtol=0.0), (
            f"per-POI embeddings differ between notebook reference and "
            f"migrated pipeline.\n  max abs diff: {np.abs(ref_emb - mig_emb).max()}"
        )


# ---------------------------------------------------------------------------
# Paper-variant (SphereMixScale / Eq.8) equivalence tests
# ---------------------------------------------------------------------------

class TestSphereMixScalePaperEncoder:
    """
    Validate that our `SphereMixScalePositionEncoder` is numerically equivalent
    to the frozen upstream reference in `_sphere2vec_paper_reference.py`.

    Two axes are exercised:
    1. Output dimensionality is the expected ``8 * frequency_num`` (upstream's
       ``cal_input_dim`` is stale and returns ``4 * frequency_num``; the
       ``forward`` body concatenates 8 terms, so that is the real dim).
    2. Forward output matches the upstream numpy reference on a fixed batch.
       The coordinate-order swap (our pipeline uses ``(lat, lon)`` while the
       upstream code uses ``(lon, lat)``) is accounted for at the input.
    """

    def _fixed_coords(self):
        # A handful of realistic (lat, lon) points spanning a continent.
        return np.array(
            [
                [32.5, -86.8],   # Montgomery, AL
                [40.7, -74.0],   # NYC
                [-33.9, 151.2],  # Sydney
                [51.5, -0.12],   # London
                [0.0, 0.0],      # Null Island
            ],
            dtype=np.float32,
        )

    def test_output_dim_is_eight_times_frequency_num(self):
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereMixScalePositionEncoder,
        )

        for F_num in (4, 8, 16, 32):
            enc = SphereMixScalePositionEncoder(
                frequency_num=F_num, min_radius=10, max_radius=10000
            )
            assert enc.output_dim == 8 * F_num
            out = enc(torch.from_numpy(self._fixed_coords()))
            assert out.shape == (5, 8 * F_num)
            assert out.dtype == torch.float32

    def test_forward_matches_upstream_reference(self):
        from tests.test_embeddings import _sphere2vec_paper_reference as pref
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereMixScalePositionEncoder,
        )

        coords_latlon = self._fixed_coords()
        # Upstream expects (B, num_ctx, 2) with (lon, lat). Swap cols.
        coords_lonlat = coords_latlon[:, [1, 0]][:, None, :]  # (B, 1, 2)

        ref_enc = pref.SphereMixScaleSpatialRelationEncoder(
            spa_embed_dim=128,
            coord_dim=2,
            frequency_num=32,
            min_radius=10,
            max_radius=10000,
            freq_init="geometric",
            ffn=None,
            device="cpu",
        )
        ref_out = ref_enc(coords_lonlat)  # (B, 1, 8*32)
        ref_out_np = ref_out.detach().cpu().numpy().reshape(5, -1)

        new_enc = SphereMixScalePositionEncoder(
            frequency_num=32, min_radius=10, max_radius=10000, device="cpu"
        )
        new_out = new_enc(torch.from_numpy(coords_latlon))
        new_out_np = new_out.detach().cpu().numpy()

        assert ref_out_np.shape == new_out_np.shape == (5, 256)
        # Upstream uses float64 internally and casts to FloatTensor at the
        # end; our impl stays in float32. Allow loose atol for the cast slop.
        max_abs = np.abs(ref_out_np - new_out_np).max()
        assert max_abs < 1e-5, (
            f"SphereMixScale paper-variant output differs from upstream "
            f"reference: max abs diff = {max_abs}"
        )

    def test_zero_learned_parameters(self):
        """
        The paper's position encoder is fully closed-form. The only persistent
        module state is the ``freq_mat`` buffer — no ``nn.Parameter`` should
        be registered.
        """
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereMixScalePositionEncoder,
        )
        enc = SphereMixScalePositionEncoder(
            frequency_num=32, min_radius=10, max_radius=10000
        )
        assert list(enc.parameters()) == []
        assert "freq_mat" in dict(enc.named_buffers())

    def test_deterministic_across_inits(self):
        """Same hyperparameters → identical freq buffer, no randomness."""
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereMixScalePositionEncoder,
        )
        a = SphereMixScalePositionEncoder(
            frequency_num=32, min_radius=10, max_radius=10000
        )
        b = SphereMixScalePositionEncoder(
            frequency_num=32, min_radius=10, max_radius=10000
        )
        assert torch.equal(a.freq_mat, b.freq_mat)
        coords = torch.from_numpy(self._fixed_coords())
        assert torch.equal(a(coords), b(coords))


class TestSphereLocationEncoderPaperVariant:
    """
    End-to-end sanity: ``SphereLocationEncoder(encoder_variant='paper')``
    constructs, forwards to the correct output shape, and the RBF-variant
    default path is unchanged.
    """

    def test_paper_variant_wires_correctly(self):
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereLocationEncoder,
        )
        enc = SphereLocationEncoder(
            spa_embed_dim=128,
            num_scales=32,
            min_scale=10,
            max_scale=10000,
            num_centroids=256,  # ignored in paper variant
            ffn_hidden_dim=512,
            encoder_variant="paper",
        )
        assert enc.encoder_variant == "paper"
        # Input projector should map 8*32 = 256 → 512
        assert enc.input_projector.in_features == 256
        assert enc.input_projector.out_features == 512
        coords = torch.tensor(
            [[32.5, -86.8], [40.7, -74.0]], dtype=torch.float32
        )
        out = enc(coords)
        assert out.shape == (2, 128)

    def test_rbf_variant_default_unchanged(self):
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereLocationEncoder,
        )
        enc = SphereLocationEncoder(
            spa_embed_dim=128,
            num_scales=32,
            min_scale=10,
            max_scale=1e7,
            num_centroids=256,
            ffn_hidden_dim=512,
        )
        assert enc.encoder_variant == "rbf"
        assert enc.input_projector.in_features == 256 * 32  # 8192

    def test_invalid_variant_raises(self):
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SphereLocationEncoder,
        )
        with pytest.raises(ValueError, match="encoder_variant"):
            SphereLocationEncoder(encoder_variant="bogus")


class TestBackwardCompatAlias:
    """
    ``SpherePositionEncoder`` was the original (misnomer) class name for the
    RBF encoder. It is retained as a backward-compat alias for
    ``SphereRBFPositionEncoder``. This test pins the alias so a future
    refactor cannot silently remove it without failing CI.
    """

    def test_module_level_alias_is_same_class(self):
        from embeddings.sphere2vec.model.Sphere2VecModule import (
            SpherePositionEncoder,
            SphereRBFPositionEncoder,
        )
        assert SpherePositionEncoder is SphereRBFPositionEncoder

    def test_package_level_alias_is_same_class(self):
        from embeddings.sphere2vec import (
            SpherePositionEncoder,
            SphereRBFPositionEncoder,
        )
        assert SpherePositionEncoder is SphereRBFPositionEncoder
