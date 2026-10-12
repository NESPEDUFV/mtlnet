"""Tests for ExperimentConfig, DatasetSignature, RunManifest — Phase 3."""

import json
import pytest
from pathlib import Path

from configs.experiment import ExperimentConfig, DatasetSignature, RunManifest


class TestExperimentConfigBasic:
    """Basic construction and validation."""

    def test_minimal_construction(self):
        c = ExperimentConfig(name="test", state="florida", embedding_engine="dgi")
        assert c.name == "test"
        assert c.state == "florida"
        assert c.embedding_engine == "dgi"
        assert c.schema_version == 1

    def test_epochs_zero_raises(self):
        with pytest.raises(ValueError, match="epochs must be > 0"):
            ExperimentConfig(name="t", state="fl", embedding_engine="dgi", epochs=0)

    def test_batch_size_zero_raises(self):
        with pytest.raises(ValueError, match="batch_size must be > 0"):
            ExperimentConfig(name="t", state="fl", embedding_engine="dgi", batch_size=0)

    def test_learning_rate_zero_raises(self):
        with pytest.raises(ValueError, match="learning_rate must be > 0"):
            ExperimentConfig(name="t", state="fl", embedding_engine="dgi", learning_rate=0)

    def test_k_folds_one_raises(self):
        with pytest.raises(ValueError, match="k_folds must be >= 2"):
            ExperimentConfig(name="t", state="fl", embedding_engine="dgi", k_folds=1)

    def test_bad_schema_version_raises(self):
        with pytest.raises(ValueError, match="Unsupported schema_version"):
            ExperimentConfig(name="t", state="fl", embedding_engine="dgi", schema_version=99)

    def test_bad_next_target_raises(self):
        with pytest.raises(ValueError, match="next_target"):
            ExperimentConfig(
                name="t",
                state="fl",
                embedding_engine="dgi",
                next_target="bad",
            )


class TestExperimentConfigSaveLoad:
    """Round-trip serialization."""

    def test_round_trip(self, tmp_path):
        c = ExperimentConfig(name="test", state="florida", embedding_engine="dgi")
        p = tmp_path / "cfg.json"
        c.save(p)
        c2 = ExperimentConfig.load(p)
        assert c == c2

    def test_round_trip_with_all_fields(self, tmp_path):
        c = ExperimentConfig(
            name="full",
            state="texas",
            embedding_engine="hgi",
            model_name="mtlnet",
            model_params={"feature_size": 128, "num_classes": 7},
            task_type="mtl",
            epochs=100,
            batch_size=512,
            learning_rate=3e-4,
            max_lr=3e-3,
            weight_decay=0.01,
            gradient_accumulation_steps=4,
            max_grad_norm=2.0,
            optimizer_eps=1e-7,
            task_loss="focal_loss",
            mtl_loss="nash_mtl",
            mtl_loss_params={"max_norm": 2.2},
            use_class_weights=False,
            k_folds=3,
            seed=123,
            split_relaxation=True,
            min_category_val_fraction=0.03,
            min_next_val_fraction=0.04,
            min_class_count=10,
            min_class_fraction=0.05,
            timeout=3600.0,
            target_cutoff=0.9,
            early_stopping_patience=5,
        )
        p = tmp_path / "full.json"
        c.save(p)
        c2 = ExperimentConfig.load(p)
        assert c == c2

    def test_save_creates_valid_json(self, tmp_path):
        c = ExperimentConfig(name="t", state="fl", embedding_engine="dgi")
        p = tmp_path / "cfg.json"
        c.save(p)
        data = json.loads(p.read_text())
        assert data["name"] == "t"
        assert data["schema_version"] == 1

    def test_load_wrong_schema_version_raises(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({
            "name": "t", "state": "fl", "embedding_engine": "dgi",
            "schema_version": 2
        }))
        with pytest.raises(ValueError, match="schema_version=2"):
            ExperimentConfig.load(p)

    def test_load_missing_schema_version_raises(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({
            "name": "t", "state": "fl", "embedding_engine": "dgi"
        }))
        with pytest.raises(ValueError, match="schema_version=None"):
            ExperimentConfig.load(p)

    def test_load_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ExperimentConfig.load(tmp_path / "nope.json")


class TestExperimentConfigFactories:
    """Factory classmethods produce correct defaults."""

    def test_default_mtl(self):
        c = ExperimentConfig.default_mtl("test", "florida", "hgi")
        assert c.task_type == "mtl"
        assert c.epochs > 0
        assert c.batch_size > 0
        assert c.learning_rate > 0
        assert c.max_lr >= c.learning_rate
        assert c.weight_decay >= 0
        assert c.gradient_accumulation_steps >= 1
        assert c.max_grad_norm > 0
        assert c.use_class_weights is True
        assert c.mtl_loss != ""
        assert c.model_name == "mtlnet"
        assert c.model_params["num_classes"] > 0

    def test_default_category(self):
        c = ExperimentConfig.default_category("test", "florida", "dgi")
        assert c.task_type == "category"
        assert c.epochs > 0
        assert c.batch_size > 0
        assert c.learning_rate > 0
        assert c.max_lr >= c.learning_rate
        assert c.mtl_loss == ""
        assert c.model_name == "category_ensemble"
        assert c.model_params["num_classes"] > 0

    def test_default_next(self):
        c = ExperimentConfig.default_next("test", "alabama", "check2hgi")
        assert c.task_type == "next"
        assert c.epochs > 0
        assert c.batch_size > 0
        assert c.learning_rate > 0
        assert c.max_lr >= c.learning_rate
        assert c.mtl_loss == ""
        assert c.model_name == "next_single"
        assert c.model_params["embed_dim"] > 0
        assert c.model_params["num_heads"] > 0

    def test_factory_overrides(self):
        c = ExperimentConfig.default_mtl(
            "test", "florida", "hgi", epochs=10, learning_rate=3e-4
        )
        assert c.epochs == 10
        assert c.learning_rate == 3e-4
        # Non-overridden defaults preserved
        assert c.batch_size > 0

    def test_factory_round_trip(self, tmp_path):
        for factory in [
            ExperimentConfig.default_mtl,
            ExperimentConfig.default_category,
            ExperimentConfig.default_next,
        ]:
            c = factory("test", "florida", "dgi")
            p = tmp_path / f"{c.task_type}.json"
            c.save(p)
            c2 = ExperimentConfig.load(p)
            assert c == c2


class TestDatasetSignature:
    """DatasetSignature from_path tests."""

    def test_from_path(self, tmp_path):
        p = tmp_path / "data.bin"
        p.write_bytes(b"hello world")
        sig = DatasetSignature.from_path(p)
        assert sig.size_bytes == 11
        assert len(sig.sha256) == 64
        assert sig.path.endswith("data.bin")
        assert "T" in sig.mtime  # ISO 8601 format

    def test_from_path_deterministic(self, tmp_path):
        p = tmp_path / "det.txt"
        p.write_text("same content")
        sig1 = DatasetSignature.from_path(p)
        sig2 = DatasetSignature.from_path(p)
        assert sig1.sha256 == sig2.sha256
        assert sig1.size_bytes == sig2.size_bytes


class TestRunManifest:
    """RunManifest write and from_current_env tests."""

    def test_write_produces_valid_json(self, tmp_path):
        config = ExperimentConfig.default_mtl("test", "florida", "hgi")
        manifest = RunManifest(
            config=config,
            git_commit="abc123",
            seeds={"torch_manual_seed": 42},
            pytorch_version="2.9.1",
            device="cpu",
            deterministic_flags={},
            timestamp="2026-03-26T00:00:00+00:00",
            dataset_signatures={},
        )
        path = manifest.write(tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["git_commit"] == "abc123"
        assert data["config"]["name"] == "test"
        assert data["schema_version"] == 1

    def test_write_with_dataset_signature(self, tmp_path):
        config = ExperimentConfig(name="t", state="fl", embedding_engine="dgi")
        data_file = tmp_path / "data.parquet"
        data_file.write_bytes(b"fake parquet")
        sig = DatasetSignature.from_path(data_file)

        manifest = RunManifest(
            config=config,
            git_commit="def456",
            seeds={},
            pytorch_version="2.9.1",
            device="cpu",
            deterministic_flags={},
            timestamp="2026-03-26T00:00:00+00:00",
            dataset_signatures={"category_input": sig},
        )
        out_dir = tmp_path / "results"
        path = manifest.write(out_dir)
        data = json.loads(path.read_text())
        assert "category_input" in data["dataset_signatures"]
        assert data["dataset_signatures"]["category_input"]["size_bytes"] == 12

    def test_from_current_env(self, tmp_path):
        config = ExperimentConfig.default_mtl("test", "florida", "dgi")
        data_file = tmp_path / "cat.parquet"
        data_file.write_bytes(b"test data")

        manifest = RunManifest.from_current_env(
            config=config,
            dataset_paths={"category_input": data_file},
        )
        assert manifest.pytorch_version  # non-empty
        assert manifest.git_commit  # non-empty (could be "unknown")
        assert manifest.timestamp  # non-empty
        assert "category_input" in manifest.dataset_signatures

    def test_from_current_env_missing_files(self):
        config = ExperimentConfig(name="t", state="fl", embedding_engine="dgi")
        manifest = RunManifest.from_current_env(
            config=config,
            dataset_paths={"missing": Path("/nonexistent/file.parquet")},
        )
        assert "missing" not in manifest.dataset_signatures


class TestAlignedPairingField:
    """pipeline_audit 2026-07-01 — regression for the --aligned-pairing crash.

    train.py:_apply_cli_overrides does ``dataclasses.replace(config,
    aligned_pairing=True)``; before the field existed this raised TypeError
    (docs/studies/log.md 2026-06-19 known bug), and the FoldCreator wiring
    silently read False via getattr. The field must exist, default False.
    """

    def test_field_exists_default_false(self):
        config = ExperimentConfig.default_mtl("test", "alabama", "check2hgi")
        assert config.aligned_pairing is False

    def test_dataclasses_replace_accepts_it(self):
        import dataclasses as _dc
        config = ExperimentConfig.default_mtl("test", "alabama", "check2hgi")
        replaced = _dc.replace(config, aligned_pairing=True)
        assert replaced.aligned_pairing is True
        # original untouched (frozen-recipe safety)
        assert config.aligned_pairing is False
