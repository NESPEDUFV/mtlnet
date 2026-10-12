"""Tests for embedding utilities and common functionality."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# File-existence sentinels (evaluated at collection time)
# ---------------------------------------------------------------------------
_ALABAMA_HGI = Path("output/hgi/alabama/embeddings.parquet")
_ALABAMA_DGI = Path("output/dgi/alabama/embeddings.parquet")
_ALABAMA_HMRM = Path("output/hmrm/alabama/embeddings.parquet")
_ALABAMA_TIME2VEC = Path("output/time2vec/alabama/embeddings.parquet")
_ALABAMA_CHECK2HGI = Path("output/check2hgi/alabama/embeddings.parquet")
_ALABAMA_FUSION_CATEGORY = Path("output/fusion/alabama/input/category.parquet")

_has_checkin_emb = _ALABAMA_TIME2VEC.exists() or _ALABAMA_CHECK2HGI.exists()


class TestEmbeddingLoading:
    """Test suite for embedding loading utilities."""

    @pytest.mark.skipif(
        not _ALABAMA_HGI.exists(),
        reason="Alabama HGI embeddings not present",
    )
    def test_load_poi_embeddings(self):
        """Test loading POI-level embeddings."""
        from configs.paths import IoPaths, EmbeddingEngine

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.HGI)

        assert "placeid" in df.columns
        assert len(df) > 0
        emb_cols = _embedding_cols(df)
        assert len(emb_cols) > 0
        assert not df[emb_cols].isnull().any().any()

    @pytest.mark.skipif(
        not _has_checkin_emb,
        reason="Alabama check-in level embeddings (time2vec or check2hgi) not present",
    )
    def test_load_checkin_embeddings(self):
        """Test loading check-in level embeddings."""
        from configs.paths import IoPaths, EmbeddingEngine

        if _ALABAMA_TIME2VEC.exists():
            df = IoPaths.load_embedd("alabama", EmbeddingEngine.TIME2VEC)
        else:
            df = IoPaths.load_embedd("alabama", EmbeddingEngine.CHECK2HGI)

        assert "placeid" in df.columns
        assert len(df) > 0
        emb_cols = _embedding_cols(df)
        assert len(emb_cols) > 0
        assert not df[emb_cols].isnull().any().any()


def _embedding_cols(df: pd.DataFrame):
    """Return the numeric embedding columns, excluding metadata columns."""
    return [c for c in df.columns if c not in ("placeid", "category")]


class TestEmbeddingDimensions:
    """Test suite for embedding dimension validation."""

    @pytest.mark.skipif(
        not _ALABAMA_DGI.exists(),
        reason="Alabama DGI embeddings not present",
    )
    def test_dgi_dimensions(self):
        """Test DGI embedding dimensions (64)."""
        from configs.paths import IoPaths, EmbeddingEngine

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.DGI)
        emb_cols = _embedding_cols(df)
        assert len(emb_cols) == 64, f"Expected 64 DGI dims, got {len(emb_cols)}"

    @pytest.mark.skipif(
        not _ALABAMA_HGI.exists(),
        reason="Alabama HGI embeddings not present",
    )
    def test_hgi_dimensions(self):
        """Test HGI embedding dimensions (64 as used in training config)."""
        from configs.paths import IoPaths, EmbeddingEngine

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.HGI)
        emb_cols = _embedding_cols(df)
        assert len(emb_cols) == 64, f"Expected 64 HGI dims, got {len(emb_cols)}"

    @pytest.mark.skipif(
        not _ALABAMA_HMRM.exists(),
        reason="Alabama HMRM embeddings not present",
    )
    def test_hmrm_dimensions(self):
        """Test HMRM embedding dimensions (135 as present in Alabama output)."""
        from configs.paths import IoPaths, EmbeddingEngine

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.HMRM)
        emb_cols = _embedding_cols(df)
        assert len(emb_cols) == 135, f"Expected 135 HMRM dims, got {len(emb_cols)}"

    @pytest.mark.skipif(
        not _ALABAMA_FUSION_CATEGORY.exists(),
        reason="Alabama fusion category input not present",
    )
    def test_fusion_dimensions(self):
        """Test FUSION embedding dimensions (>64, concatenated sources)."""
        df = pd.read_parquet(_ALABAMA_FUSION_CATEGORY)
        # Fusion category format: [placeid, category, emb_0, ..., emb_N]
        non_meta_cols = [c for c in df.columns if c not in ("placeid", "category")]
        assert len(non_meta_cols) > 64, (
            f"Expected fusion dims > 64, got {len(non_meta_cols)}"
        )


class TestEmbeddingAlignment:
    """Test suite for embedding alignment across sources."""

    @pytest.mark.skipif(
        not _ALABAMA_HGI.exists(),
        reason="Alabama HGI embeddings not present",
    )
    def test_poi_alignment(self):
        """Test that each POI appears exactly once (1 row per POI)."""
        from configs.paths import IoPaths, EmbeddingEngine

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.HGI)
        assert df["placeid"].is_unique, (
            f"Expected unique placeids; found {df['placeid'].duplicated().sum()} duplicates"
        )

    @pytest.mark.skipif(
        not _ALABAMA_HGI.exists(),
        reason="Alabama HGI embeddings not present",
    )
    def test_missing_values(self):
        """Test create_embedding_lookup fills missing placeids with zeros."""
        from configs.paths import IoPaths, EmbeddingEngine
        from data.inputs.core import create_embedding_lookup

        df = IoPaths.load_embedd("alabama", EmbeddingEngine.HGI)
        emb_cols = _embedding_cols(df)
        dim = len(emb_cols)

        lookup = create_embedding_lookup(df, dim)

        # Existing POI should have a real (non-zero) vector
        existing_poi = int(df["placeid"].iloc[0])
        assert existing_poi in lookup
        assert lookup[existing_poi].shape == (dim,)

        # A fabricated POI ID that is definitely absent
        fake_poi = -9999
        assert fake_poi not in lookup, (
            "Fabricated POI should not be in lookup"
        )

        # Padding sentinel (-1) should return zero embedding
        from data.inputs.core import PADDING_VALUE
        assert PADDING_VALUE in lookup
        np.testing.assert_array_equal(
            lookup[PADDING_VALUE],
            np.zeros(dim, dtype=np.float32),
            err_msg="Padding embedding should be all zeros",
        )
