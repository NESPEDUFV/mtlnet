"""
End-to-end tests: synthetic data -> pipeline -> model forward pass.

Validates that data pipeline output dimensions are compatible with model inputs.
Catches dimension mismatches that would be silent runtime bugs.
"""

import numpy as np
import pandas as pd
import pytest
import torch
import torch.nn as nn

from configs.embedding_fusion import EmbeddingLevel, EmbeddingSpec
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine
from data.inputs.core import (
    convert_sequences_to_poi_embeddings,
    convert_user_checkins_to_sequences,
    create_category_lookup,
    create_embedding_lookup,
    generate_sequences,
)
from data.inputs.fusion import EmbeddingAligner, EmbeddingFuser
from models.registry import create_model
from tests.test_integration.conftest import NUM_CLASSES, seed_everything
from tests.test_integration.test_data_pipeline import make_pipeline_data

WINDOW_SIZE = InputsConfig.SLIDE_WINDOW  # 9


def _pipeline_to_tensors_poi(data, dim):
    """Run POI-level pipeline and return (category_tensor, next_tensor)."""
    poi_df = data["poi_embeddings_hgi"]
    checkins_df = data["checkins_df"]

    embedding_lookup = create_embedding_lookup(poi_df, dim)
    category_lookup = create_category_lookup(checkins_df)

    all_seqs = []
    for uid, udf in checkins_df.groupby("userid"):
        for s in generate_sequences(udf["placeid"].tolist(), WINDOW_SIZE):
            all_seqs.append(s + [uid])

    seq_cols = [f"poi_{i}" for i in range(WINDOW_SIZE)] + ["target_poi", "userid"]
    sequences_df = pd.DataFrame(all_seqs, columns=seq_cols)

    results = convert_sequences_to_poi_embeddings(
        sequences_df, embedding_lookup, category_lookup,
        WINDOW_SIZE, dim, show_progress=False,
    )

    # Build next tensor: extract flattened embeddings, reshape to (N, WINDOW, dim)
    n = len(results)
    next_flat = np.array([r[:WINDOW_SIZE * dim].astype(np.float32) for r in results])
    next_tensor = torch.from_numpy(next_flat.reshape(n, WINDOW_SIZE, dim))

    # Build category tensor: one embedding per POI
    emb_cols = [str(i) for i in range(dim)]
    cat_tensor = torch.from_numpy(poi_df[emb_cols].values.astype(np.float32))

    return cat_tensor, next_tensor


def _pipeline_to_tensors_fusion(data, dim):
    """Run fusion pipeline (HGI + Space2Vec) and return (category_tensor, next_tensor)."""
    total_dim = 2 * dim
    spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
    spec_space = EmbeddingSpec(EmbeddingEngine.SPACE2VEC, EmbeddingLevel.POI, dim)

    # Category: align + fuse POI embeddings
    base_df = data["poi_embeddings_hgi"][["placeid"]].copy()
    base_df["category"] = base_df["placeid"].map(data["categories"])
    aligned_cat = EmbeddingAligner.align_poi_level(
        base_df,
        [data["poi_embeddings_hgi"], data["poi_embeddings_space"]],
        [spec_hgi, spec_space],
    )
    fused_cat = EmbeddingFuser.fuse_embeddings(aligned_cat, [spec_hgi, spec_space])
    fused_cat_cols = [f"fused_{i}" for i in range(total_dim)]
    cat_tensor = torch.from_numpy(fused_cat[fused_cat_cols].values.astype(np.float32))

    # Next: align + fuse, then generate sequences
    fused_renamed = fused_cat.rename(columns={f"fused_{i}": str(i) for i in range(total_dim)})
    embedding_lookup = create_embedding_lookup(fused_renamed, total_dim)
    category_lookup = create_category_lookup(data["checkins_df"])

    all_seqs = []
    for uid, udf in data["checkins_df"].groupby("userid"):
        for s in generate_sequences(udf["placeid"].tolist(), WINDOW_SIZE):
            all_seqs.append(s + [uid])

    seq_cols = [f"poi_{i}" for i in range(WINDOW_SIZE)] + ["target_poi", "userid"]
    sequences_df = pd.DataFrame(all_seqs, columns=seq_cols)

    results = convert_sequences_to_poi_embeddings(
        sequences_df, embedding_lookup, category_lookup,
        WINDOW_SIZE, total_dim, show_progress=False,
    )

    n = len(results)
    next_flat = np.array([r[:WINDOW_SIZE * total_dim].astype(np.float32) for r in results])
    next_tensor = torch.from_numpy(next_flat.reshape(n, WINDOW_SIZE, total_dim))

    return cat_tensor, next_tensor


class TestDataToModel:
    """Verify pipeline outputs feed into models without dimension errors."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    def test_single_engine_category_to_model(self):
        data = make_pipeline_data(embedding_dim=64)
        cat_tensor, _ = _pipeline_to_tensors_poi(data, 64)

        model = create_model(
            "category_single",
            input_dim=64,
            hidden_dims=(128, 64),
            num_classes=NUM_CLASSES,
            dropout=0.1,
        )
        model.eval()
        with torch.no_grad():
            out = model(cat_tensor)

        assert out.shape == (len(data["poi_ids"]), NUM_CLASSES)

    def test_single_engine_next_to_model(self):
        data = make_pipeline_data(embedding_dim=64)
        _, next_tensor = _pipeline_to_tensors_poi(data, 64)

        model = create_model(
            "next_single",
            embed_dim=64,
            num_classes=NUM_CLASSES,
            num_heads=8,
            seq_length=WINDOW_SIZE,
            num_layers=2,
        )
        model.eval()
        with torch.no_grad():
            out = model(next_tensor)

        assert out.shape[1] == NUM_CLASSES
        assert out.shape[0] == next_tensor.shape[0]

    def test_fused_category_to_model(self):
        data = make_pipeline_data(embedding_dim=64)
        cat_tensor, _ = _pipeline_to_tensors_fusion(data, 64)

        model = create_model(
            "category_single",
            input_dim=128,  # 2 * 64
            hidden_dims=(256, 128),
            num_classes=NUM_CLASSES,
            dropout=0.1,
        )
        model.eval()
        with torch.no_grad():
            out = model(cat_tensor)

        assert out.shape == (len(data["poi_ids"]), NUM_CLASSES)

    def test_fused_mtl_to_model(self):
        data = make_pipeline_data(embedding_dim=64)
        cat_tensor, next_tensor = _pipeline_to_tensors_fusion(data, 64)

        model = create_model(
            "mtlnet",
            feature_size=128,  # 2 * 64
            shared_layer_size=256,
            num_classes=NUM_CLASSES,
            num_heads=8,
            num_layers=4,
            seq_length=WINDOW_SIZE,
            num_shared_layers=4,
        )
        model.eval()

        # MTLnet expects (cat_input_3d, next_input)
        cat_3d = cat_tensor.unsqueeze(1)  # (N, 1, 128)
        # Use same batch size for both
        batch = min(cat_3d.shape[0], next_tensor.shape[0])
        with torch.no_grad():
            out_cat, out_next = model((cat_3d[:batch], next_tensor[:batch]))

        assert out_cat.shape == (batch, NUM_CLASSES)
        assert out_next.shape == (batch, NUM_CLASSES)
