"""Tests for path configuration and management."""

import os
import pytest
from pathlib import Path

from configs.paths import EmbeddingEngine, IoPaths, DATA_ROOT


class TestEmbeddingEngine:
    """Test suite for EmbeddingEngine enum."""

    def test_all_engines_defined(self):
        """The canonical embedding engines must all be defined. Research/ablation
        variants (check2hgi_design_*, *_resln, gat, rgcn, …) get added to the enum
        over time, so this is a subset check on the canonical set, not exact equality."""
        canonical = {"dgi", "hgi", "hmrm", "time2vec", "space2vec", "sphere2vec",
                     "check2hgi", "poi2hgi", "fusion"}
        actual_values = {e.value for e in EmbeddingEngine}
        assert canonical <= actual_values, f"missing canonical engines: {canonical - actual_values}"

    def test_fusion_engine(self):
        """Test FUSION engine configuration."""
        assert EmbeddingEngine.FUSION.value == "fusion"


class TestIoPaths:
    """Test suite for IoPaths path management."""

    def test_get_embedd(self):
        """Test get_embedd() path resolution."""
        path = IoPaths.get_embedd("florida", EmbeddingEngine.HGI)
        assert isinstance(path, Path)
        assert "hgi" in str(path)
        assert "florida" in str(path)
        assert path.name == "embeddings.parquet"

        # FUSION raises ValueError
        with pytest.raises(ValueError):
            IoPaths.get_embedd("florida", EmbeddingEngine.FUSION)

    def test_get_category(self):
        """Test get_category() path resolution."""
        path = IoPaths.get_category("florida", EmbeddingEngine.DGI)
        assert isinstance(path, Path)
        assert "dgi" in str(path)
        assert "florida" in str(path)
        assert path.name == "category.parquet"

        # FUSION routes to fusion path
        fusion_path = IoPaths.get_category("florida", EmbeddingEngine.FUSION)
        assert isinstance(fusion_path, Path)
        assert "fusion" in str(fusion_path)

    def test_get_next(self):
        """Test get_next() path resolution."""
        path = IoPaths.get_next("florida", EmbeddingEngine.DGI)
        assert isinstance(path, Path)
        assert "dgi" in str(path)
        assert "florida" in str(path)
        assert path.name == "next.parquet"

        # FUSION routes to fusion path
        fusion_path = IoPaths.get_next("florida", EmbeddingEngine.FUSION)
        assert isinstance(fusion_path, Path)
        assert "fusion" in str(fusion_path)

    def test_get_results_dir(self):
        """Test get_results_dir() path resolution."""
        path = IoPaths.get_results_dir("florida", EmbeddingEngine.HGI)
        assert isinstance(path, Path)
        assert "hgi" in str(path)
        assert "florida" in str(path)

        # FUSION routes to fusion path
        fusion_path = IoPaths.get_results_dir("florida", EmbeddingEngine.FUSION)
        assert isinstance(fusion_path, Path)
        assert "fusion" in str(fusion_path)

    def test_fusion_routing(self):
        """Test FUSION engine routing to fusion-specific paths."""
        cat_path = IoPaths.get_category("texas", EmbeddingEngine.FUSION)
        next_path = IoPaths.get_next("texas", EmbeddingEngine.FUSION)
        results_path = IoPaths.get_results_dir("texas", EmbeddingEngine.FUSION)

        assert "fusion" in str(cat_path)
        assert "fusion" in str(next_path)
        assert "fusion" in str(results_path)

    def test_data_root_env_var(self, monkeypatch, tmp_path):
        """Test $DATA_ROOT environment variable handling."""
        # DATA_ROOT is a Path
        assert isinstance(DATA_ROOT, Path)

        # Verify it can be overridden via env var (reimport to check module-level behaviour)
        monkeypatch.setenv("DATA_ROOT", str(tmp_path))
        import importlib
        import configs.paths as paths_module
        importlib.reload(paths_module)
        assert paths_module.DATA_ROOT == tmp_path

        # Restore by reloading without the env var
        monkeypatch.delenv("DATA_ROOT", raising=False)
        importlib.reload(paths_module)

