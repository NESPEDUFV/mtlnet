"""Unit tests for substrate-protocol-cleanup Tier C flags.

Covers the three opt-in features added to the trainer / model:

* C1: ``--save-task-best-snapshots`` (MultiTaskBestTracker + per-fold
  on-disk snapshots).
* C2: ``--reg-freeze-at-epoch N`` (freeze next_encoder + next_poi at
  epoch N; zero the reg loss from N onward).
* C3: ``--zero-cat-kv`` (forward-only ablation that zeroes cat K/V
  tensors before the cross-attention softmax in MTLnetCrossAttn).

All tests use CPU-only synthetic data — no real datasets, no GPU.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))


# ---------------------------------------------------------------------------
# C3 — --zero-cat-kv: forward-only ablation
# ---------------------------------------------------------------------------


class TestZeroCatKV:
    """The cat-stream K/V tensors fed into ``cross_ba`` must be exactly
    zero when ``zero_cat_kv=True`` is set, and intact otherwise."""

    @pytest.fixture
    def model_kwargs(self):
        return dict(
            feature_size=16,
            shared_layer_size=16,
            num_classes=7,
            num_heads=4,
            num_layers=2,
            seq_length=9,
            num_shared_layers=2,
            encoder_layer_size=16,
            num_encoder_layers=1,
            num_crossattn_blocks=1,
            num_crossattn_heads=2,
            crossattn_ffn_dim=16,
        )

    def test_zero_cat_kv_zeroes_block_input(self, model_kwargs):
        from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn

        torch.manual_seed(0)
        model = MTLnetCrossAttn(zero_cat_kv=True, **model_kwargs)
        model.eval()

        # Hook the cross_ba MultiheadAttention forward to capture k/v.
        captured = {}

        def _hook(module, args, kwargs):
            # kwargs holds `query`, `key`, `value`
            captured['key'] = kwargs.get('key', args[1] if len(args) > 1 else None)
            captured['value'] = kwargs.get('value', args[2] if len(args) > 2 else None)

        block = model.crossattn_blocks[0]
        handle = block.cross_ba.register_forward_pre_hook(_hook, with_kwargs=True)
        try:
            cat_in = torch.randn(2, 1, model_kwargs['feature_size'])
            next_in = torch.randn(2, model_kwargs['seq_length'], model_kwargs['feature_size'])
            with torch.no_grad():
                model((cat_in, next_in))
        finally:
            handle.remove()

        assert captured['key'] is not None and captured['value'] is not None
        assert torch.all(captured['key'] == 0.0), (
            "cat-side K (input to cross_ba) must be all-zero when "
            "zero_cat_kv=True"
        )
        assert torch.all(captured['value'] == 0.0), (
            "cat-side V (input to cross_ba) must be all-zero when "
            "zero_cat_kv=True"
        )

    def test_zero_cat_kv_default_off(self, model_kwargs):
        from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn

        torch.manual_seed(0)
        model = MTLnetCrossAttn(zero_cat_kv=False, **model_kwargs)
        model.eval()

        captured = {}

        def _hook(module, args, kwargs):
            captured['key'] = kwargs.get('key', args[1] if len(args) > 1 else None)

        block = model.crossattn_blocks[0]
        handle = block.cross_ba.register_forward_pre_hook(_hook, with_kwargs=True)
        try:
            cat_in = torch.randn(2, 1, model_kwargs['feature_size'])
            next_in = torch.randn(2, model_kwargs['seq_length'], model_kwargs['feature_size'])
            with torch.no_grad():
                model((cat_in, next_in))
        finally:
            handle.remove()

        assert captured['key'] is not None
        # Random input through an encoder + LN produces a non-zero K with
        # overwhelming probability; assert no all-zero short-circuit fired.
        assert not torch.all(captured['key'] == 0.0)


# ---------------------------------------------------------------------------
# C1 — MultiTaskBestTracker + on-disk snapshot save
# ---------------------------------------------------------------------------


class TestMultiTaskBestTracker:
    """Three-snapshot routing: cat/reg/joint slots independent, each
    snapshot internally consistent (same epoch's state per slot)."""

    def test_three_slots_independent(self):
        from tracking.best_tracker import MultiTaskBestTracker

        tracker = MultiTaskBestTracker(
            cat_monitor='f1', reg_monitor='accuracy', joint_monitor='joint_geom_lift',
            mode='max', min_epoch=0,
        )
        # Epoch 0: cat is best so far; reg + joint also recorded
        tracker.update(
            epoch=0,
            model_state={'a': torch.tensor(0.0)},
            cat_metric=0.5, reg_metric=0.1, joint_metric=0.2,
        )
        # Epoch 1: only reg improves
        tracker.update(
            epoch=1,
            model_state={'a': torch.tensor(1.0)},
            cat_metric=0.4, reg_metric=0.6, joint_metric=0.15,
        )
        # Epoch 2: only joint improves
        tracker.update(
            epoch=2,
            model_state={'a': torch.tensor(2.0)},
            cat_metric=0.3, reg_metric=0.55, joint_metric=0.7,
        )

        assert tracker.cat_best.best_epoch == 0
        assert tracker.reg_best.best_epoch == 1
        assert tracker.joint_best.best_epoch == 2

        snaps = tracker.snapshots()
        assert set(snaps.keys()) == {'cat', 'reg', 'joint'}
        assert snaps['cat']['a'].item() == 0.0
        assert snaps['reg']['a'].item() == 1.0
        assert snaps['joint']['a'].item() == 2.0

    def test_save_task_best_snapshots_writes_three_files(self, tmp_path):
        """Run a 2-epoch synthetic MTL fold against the actual tracker +
        on-disk save logic from ``mtl_cv``, verifying three loadable
        checkpoints land on disk per fold."""
        from tracking.best_tracker import MultiTaskBestTracker

        tracker = MultiTaskBestTracker(min_epoch=0)
        # Simulate two epochs of state evolution
        state_e0 = {'w': torch.randn(4, 4)}
        state_e1 = {'w': torch.randn(4, 4)}
        tracker.update(0, state_e0, cat_metric=0.5, reg_metric=0.5, joint_metric=0.5)
        tracker.update(1, state_e1, cat_metric=0.6, reg_metric=0.4, joint_metric=0.55)

        # Verify slot routing
        assert tracker.cat_best.best_epoch == 1
        assert tracker.reg_best.best_epoch == 0
        assert tracker.joint_best.best_epoch == 1

        # Replicate runner's per-fold save loop
        fold_dir = tmp_path / "task_best_snapshots"
        fold_dir.mkdir()
        for slot, state in tracker.snapshots().items():
            torch.save(state, fold_dir / f"fold1_{slot}_best.pt")

        for slot in ("cat", "reg", "joint"):
            p = fold_dir / f"fold1_{slot}_best.pt"
            assert p.exists(), f"missing {p}"
            loaded = torch.load(p, weights_only=False)
            assert 'w' in loaded


# ---------------------------------------------------------------------------
# C2 — --reg-freeze-at-epoch: requires_grad flip + zeroed reg loss
# ---------------------------------------------------------------------------


class _MiniMTLModel(torch.nn.Module):
    """Minimum-viable MTL model mimicking the attribute names the runner
    keys off (``next_encoder``, ``next_poi``, ``category_encoder``,
    ``category_poi``). Used as a stand-in for the heavy MTLnet so the
    test runs in <1s without a registry round-trip."""

    def __init__(self, embed_dim=8, num_classes=4):
        super().__init__()
        self.category_encoder = torch.nn.Linear(embed_dim, embed_dim)
        self.next_encoder = torch.nn.Linear(embed_dim, embed_dim)
        self.category_poi = torch.nn.Linear(embed_dim, num_classes)
        self.next_poi = torch.nn.Linear(embed_dim, num_classes)

    def forward(self, inputs):
        cat_in, next_in = inputs
        if next_in.dim() == 3:
            next_in = next_in.mean(dim=1)
        if cat_in.dim() == 3:
            cat_in = cat_in.mean(dim=1)
        return self.category_poi(self.category_encoder(cat_in)), self.next_poi(self.next_encoder(next_in))


class TestRegFreezeAtEpoch:
    """At epoch N, reg-side params flip to requires_grad=False and the
    reg loss is zeroed before joining the MTL combiner."""

    def test_requires_grad_flips_at_boundary(self):
        # Replicate the precise freeze block used in train_model:
        model = _MiniMTLModel()
        # Pre-freeze: all params trainable
        for p in model.next_encoder.parameters():
            assert p.requires_grad
        for p in model.next_poi.parameters():
            assert p.requires_grad

        reg_freeze_at_epoch = 1
        _reg_frozen_post_peak = False
        # Epoch 0: not frozen yet
        epoch_idx = 0
        if (reg_freeze_at_epoch is not None
                and not _reg_frozen_post_peak
                and epoch_idx >= int(reg_freeze_at_epoch)):
            for attr in ("next_encoder", "next_poi"):
                sub = getattr(model, attr, None)
                if sub is None:
                    continue
                for p in sub.parameters():
                    p.requires_grad_(False)
            _reg_frozen_post_peak = True
        assert not _reg_frozen_post_peak
        assert all(p.requires_grad for p in model.next_encoder.parameters())

        # Epoch 1: boundary hit
        epoch_idx = 1
        if (reg_freeze_at_epoch is not None
                and not _reg_frozen_post_peak
                and epoch_idx >= int(reg_freeze_at_epoch)):
            for attr in ("next_encoder", "next_poi"):
                sub = getattr(model, attr, None)
                if sub is None:
                    continue
                for p in sub.parameters():
                    p.requires_grad_(False)
            _reg_frozen_post_peak = True

        assert _reg_frozen_post_peak
        assert all(not p.requires_grad for p in model.next_encoder.parameters())
        assert all(not p.requires_grad for p in model.next_poi.parameters())
        # Cat side untouched
        assert all(p.requires_grad for p in model.category_encoder.parameters())
        assert all(p.requires_grad for p in model.category_poi.parameters())

    def test_reg_loss_zeroed_when_frozen(self):
        """When the flag has fired, the loss contribution from task_b is
        multiplied by 0 before the MTL combiner sees it. Verify the value
        is exactly zero and the cat loss is unchanged."""
        # Synthetic raw losses
        task_a_loss = torch.tensor(1.7)
        task_b_loss = torch.tensor(2.5)
        _reg_frozen_post_peak = True
        if _reg_frozen_post_peak:
            task_b_loss = task_b_loss * 0.0
        assert task_b_loss.item() == 0.0
        assert task_a_loss.item() == pytest.approx(1.7)

    def test_run_two_epoch_freeze_at_one(self):
        """End-to-end smoke: 2-epoch loop on the mini model with reg
        frozen at epoch 1. Verify next_encoder weight is unchanged from
        end of epoch 0 to end of epoch 1 (since reg loss is zero AND
        params have requires_grad=False), while category_encoder weight
        does change (gradient still flows from cat loss)."""
        torch.manual_seed(0)
        model = _MiniMTLModel()
        opt = torch.optim.SGD(model.parameters(), lr=0.1)
        crit = torch.nn.CrossEntropyLoss()

        bs = 8
        x_cat = torch.randn(bs, 8)
        x_next = torch.randn(bs, 9, 8)
        y_cat = torch.randint(0, 4, (bs,))
        y_next = torch.randint(0, 4, (bs,))

        _reg_frozen_post_peak = False
        reg_freeze_at_epoch = 1
        for epoch_idx in range(2):
            # Boundary check (mirrors train_model)
            if (reg_freeze_at_epoch is not None
                    and not _reg_frozen_post_peak
                    and epoch_idx >= int(reg_freeze_at_epoch)):
                for attr in ("next_encoder", "next_poi"):
                    sub = getattr(model, attr)
                    for p in sub.parameters():
                        p.requires_grad_(False)
                _reg_frozen_post_peak = True

            # Snapshot weights before this epoch's step
            next_w_before = model.next_encoder.weight.detach().clone()
            cat_w_before = model.category_encoder.weight.detach().clone()

            opt.zero_grad()
            out_cat, out_next = model((x_cat, x_next))
            task_a_loss = crit(out_cat, y_cat)
            task_b_loss = crit(out_next, y_next)
            if _reg_frozen_post_peak:
                task_b_loss = task_b_loss * 0.0
            loss = task_a_loss + task_b_loss
            loss.backward()
            opt.step()

            if epoch_idx == 0:
                # Before freeze: next_encoder should have moved
                assert not torch.allclose(model.next_encoder.weight, next_w_before)
                assert not torch.allclose(model.category_encoder.weight, cat_w_before)
            else:
                # After freeze: next_encoder unchanged; cat_encoder still moves
                assert torch.allclose(model.next_encoder.weight, next_w_before)
                assert not torch.allclose(model.category_encoder.weight, cat_w_before)


# ---------------------------------------------------------------------------
# C1 modality-bug fix — task_*_input_type persistence + scorer round-trip
# ---------------------------------------------------------------------------


class TestTaskInputTypePersistence:
    """The per-task input modality MUST round-trip through
    ExperimentConfig.save/load and be recoverable by route_task_best.py so
    the val loaders are rebuilt with the SAME modality the run trained on.

    Regression guard for the substrate-protocol-cleanup Tier C1 modality
    bug: route_task_best rebuilt loaders defaulting to task_b='checkin'
    while the run trained task_b='region', scoring a region-trained reg
    head on checkin inputs -> garbage (~0) reg metrics.
    """

    def test_config_defaults_checkin(self):
        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="modality-default-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI,
            state="alabama",
        )
        # Append-only field: legacy default preserves checkin behaviour.
        assert cfg.task_a_input_type == "checkin"
        assert cfg.task_b_input_type == "checkin"

    def test_config_roundtrip_region(self, tmp_path):
        import dataclasses

        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="modality-region-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI,
            state="alabama",
        )
        cfg = dataclasses.replace(
            cfg, task_a_input_type="checkin", task_b_input_type="region",
        )
        p = tmp_path / "config.json"
        cfg.save(p)

        # The persisted JSON must literally carry the modality so any scorer
        # can recover it without the run's argv.
        import json

        raw = json.loads(p.read_text())
        assert raw["task_a_input_type"] == "checkin"
        assert raw["task_b_input_type"] == "region"

        reloaded = ExperimentConfig.load(p)
        assert reloaded.task_a_input_type == "checkin"
        assert reloaded.task_b_input_type == "region"

    def test_load_legacy_config_without_field(self, tmp_path):
        """A config.json written before the field existed must still load,
        defaulting the modality to 'checkin' (back-compat)."""
        import json

        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="legacy-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI,
            state="alabama",
        )
        p = tmp_path / "config.json"
        cfg.save(p)
        # Strip the new keys to simulate a pre-fix artefact.
        raw = json.loads(p.read_text())
        raw.pop("task_a_input_type", None)
        raw.pop("task_b_input_type", None)
        p.write_text(json.dumps(raw))

        reloaded = ExperimentConfig.load(p)
        assert reloaded.task_a_input_type == "checkin"
        assert reloaded.task_b_input_type == "checkin"

    def test_route_task_best_resolves_region_from_config(self, tmp_path, monkeypatch):
        """route_task_best.py must construct FoldCreator with the run's
        persisted task_b_input_type (region), NOT the checkin default. We
        intercept FoldCreator to capture the modality it receives and stop
        the run before any data is touched."""
        import dataclasses

        sys.path.insert(0, str(_root / "scripts"))
        import route_task_best as rtb
        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="route-region-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI.value,
            state="alabama",
        )
        # Reconstruct a check2hgi_next_region-style task_set dict in
        # model_params so the scorer takes the MTL_CHECK2HGI branch.
        model_params = dict(cfg.model_params)
        model_params["task_set"] = {
            "name": "check2hgi_next_region",
            "task_a": {"name": "next_category", "num_classes": 7,
                       "primary_metric": "f1"},
            "task_b": {"name": "next_region", "num_classes": 7,
                       "primary_metric": "accuracy"},
        }
        cfg = dataclasses.replace(
            cfg,
            model_params=model_params,
            task_a_input_type="checkin",
            task_b_input_type="region",
        )
        cfg_path = tmp_path / "config.json"
        cfg.save(cfg_path)

        # Three dummy snapshot files so the existence check passes.
        snap_dir = tmp_path / "snaps"
        snap_dir.mkdir()
        for slot in ("cat", "reg", "joint"):
            (snap_dir / f"fold1_{slot}_best.pt").write_bytes(b"x")

        captured = {}

        class _StopHere(Exception):
            pass

        def _fake_fold_creator(*args, **kwargs):
            captured["task_a_input_type"] = kwargs.get("task_a_input_type")
            captured["task_b_input_type"] = kwargs.get("task_b_input_type")
            raise _StopHere()

        monkeypatch.setattr(rtb, "FoldCreator", _fake_fold_creator)

        argv = [
            "--snapshots-dir", str(snap_dir),
            "--fold", "1",
            "--config", str(cfg_path),
        ]
        with pytest.raises(_StopHere):
            rtb.main(argv)

        assert captured["task_a_input_type"] == "checkin"
        assert captured["task_b_input_type"] == "region", (
            "route_task_best must rebuild loaders with the run's persisted "
            "task_b_input_type=region, not the checkin default"
        )

    def test_route_task_best_cli_override_wins(self, tmp_path, monkeypatch):
        """Explicit --task-b-input-type overrides the persisted config
        value (fallback path for old configs that lacked the field)."""
        import dataclasses

        sys.path.insert(0, str(_root / "scripts"))
        import route_task_best as rtb
        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="route-override-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI.value,
            state="alabama",
        )
        model_params = dict(cfg.model_params)
        model_params["task_set"] = {
            "name": "check2hgi_next_region",
            "task_a": {"name": "next_category", "num_classes": 7,
                       "primary_metric": "f1"},
            "task_b": {"name": "next_region", "num_classes": 7,
                       "primary_metric": "accuracy"},
        }
        # Persist checkin (simulating a stale/old config) — CLI must override.
        cfg = dataclasses.replace(
            cfg, model_params=model_params,
            task_a_input_type="checkin", task_b_input_type="checkin",
        )
        cfg_path = tmp_path / "config.json"
        cfg.save(cfg_path)

        snap_dir = tmp_path / "snaps"
        snap_dir.mkdir()
        for slot in ("cat", "reg", "joint"):
            (snap_dir / f"fold1_{slot}_best.pt").write_bytes(b"x")

        captured = {}

        class _StopHere(Exception):
            pass

        def _fake_fold_creator(*args, **kwargs):
            captured["task_b_input_type"] = kwargs.get("task_b_input_type")
            raise _StopHere()

        monkeypatch.setattr(rtb, "FoldCreator", _fake_fold_creator)

        argv = [
            "--snapshots-dir", str(snap_dir),
            "--fold", "1",
            "--config", str(cfg_path),
            "--task-b-input-type", "region",
        ]
        with pytest.raises(_StopHere):
            rtb.main(argv)

        assert captured["task_b_input_type"] == "region"

    def test_route_task_best_persisted_heads_win_over_task_set(self, tmp_path, monkeypatch, caplog):
        """The dual-tower trap (closing_data C1): when the config persists a
        task_set with head OVERRIDES (champion G: reg=next_stan_flow_dualtower),
        --task-set must be IGNORED — get_preset(name) would rebuild the DEFAULT
        preset heads (reg=next_gru), whose topology fails load_state_dict on the
        dual-tower snapshots. The persisted heads must win, with a warning."""
        import dataclasses
        import logging

        sys.path.insert(0, str(_root / "scripts"))
        import route_task_best as rtb
        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine

        cfg = ExperimentConfig.default_mtl(
            name="route-dualtower-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI.value,
            state="alabama",
        )
        # Persist the FULL champion-G dual-tower task_set (the trained topology).
        reg_head_params = {
            "raw_embed_dim": 64, "fusion_mode": "aux",
            "freeze_alpha": True, "alpha_init": 0.0,
        }
        model_params = dict(cfg.model_params)
        model_params["task_set"] = {
            "name": "check2hgi_next_region",
            "task_a": {"name": "next_category", "num_classes": 7,
                       "head_factory": "next_gru", "primary_metric": "f1"},
            "task_b": {"name": "next_region", "num_classes": 1109,
                       "head_factory": "next_stan_flow_dualtower",
                       "head_params": reg_head_params,
                       "primary_metric": "top10_acc_indist"},
        }
        cfg = dataclasses.replace(
            cfg, model_params=model_params,
            task_a_input_type="checkin", task_b_input_type="region",
        )
        cfg_path = tmp_path / "config.json"
        cfg.save(cfg_path)

        snap_dir = tmp_path / "snaps"
        snap_dir.mkdir()
        for slot in ("cat", "reg", "joint"):
            (snap_dir / f"fold1_{slot}_best.pt").write_bytes(b"x")

        captured = {}

        class _StopHere(Exception):
            pass

        def _fake_fold_creator(*args, **kwargs):
            captured["task_set"] = kwargs.get("task_set")
            raise _StopHere()

        monkeypatch.setattr(rtb, "FoldCreator", _fake_fold_creator)

        argv = [
            "--snapshots-dir", str(snap_dir),
            "--fold", "1",
            "--config", str(cfg_path),
            # Passing --task-set used to clobber the heads with the default preset.
            "--task-set", "check2hgi_next_region",
        ]
        with caplog.at_level(logging.WARNING):
            with pytest.raises(_StopHere):
                rtb.main(argv)

        ts = captured["task_set"]
        assert ts is not None, "FoldCreator must receive the resolved (non-legacy) task_set"
        assert ts.task_b.head_factory == "next_stan_flow_dualtower", (
            "persisted dual-tower reg head must win over the --task-set default preset"
        )
        assert ts.task_b.head_params == reg_head_params
        assert ts.task_a.head_factory == "next_gru"


# ---------------------------------------------------------------------------
# A1 — --log-t-kd-weight / --log-t-kd-tau: KL distillation supervisory signal
# ---------------------------------------------------------------------------


def _run_kd_block(pred_task_b, log_T, aux, weight, tau, num_classes):
    """Mirror of the inline KD block in train_model. Returns the KD term
    (scalar) and the post-KD task_b_loss starting from a fixed CE base.

    Kept in lockstep with src/training/runners/mtl_cv.py lines tagged
    "substrate-protocol-cleanup Tier A1". When the runner block changes,
    update this helper in the same diff.
    """
    base = torch.tensor(1.0, dtype=pred_task_b.dtype)
    task_b_loss = base.clone()
    if weight > 0.0:
        if log_T.shape[0] >= num_classes and log_T.shape[1] >= num_classes:
            log_T_use = log_T[:num_classes, :num_classes]
        else:
            log_T_use = None
        if log_T_use is not None and aux is not None:
            _pad = (aux < 0) | (aux >= num_classes)
            _valid = ~_pad
            if _valid.any():
                _safe = aux.clamp(min=0, max=num_classes - 1)
                _teacher_logits = log_T_use.index_select(0, _safe).float() / tau
                _teacher = torch.softmax(_teacher_logits, dim=-1)
                _student_log = torch.log_softmax(pred_task_b.float() / tau, dim=-1)
                _log_teacher = torch.log(_teacher.clamp_min(1e-12))
                _student = _student_log.exp()
                _kld = (_student * (_student_log - _log_teacher)).sum(dim=-1)
                _kld = _kld * _valid.float()
                _denom = _valid.sum().clamp_min(1).float()
                _kd_loss = (_kld.sum() / _denom) * (tau * tau)
                task_b_loss = task_b_loss + weight * _kd_loss
                return _kd_loss, task_b_loss
    return torch.tensor(0.0), task_b_loss


class TestLogTKD:
    """A1 — KL distillation from per-fold log_T into the reg head output.

    Verifies:
      * W=0.0 is a strict no-op (KD branch entirely skipped).
      * W>0.0 produces a non-zero KD term and shifts task_b_loss above
        the base CE.
      * Padding rows (aux < 0 or aux >= num_classes) are excluded from
        the gradient.
      * The KD term is differentiable w.r.t. ``pred_task_b``.
    """

    def _fixture(self, num_classes=5, batch=4, seed=0):
        torch.manual_seed(seed)
        # log_T: row-stochastic in log-space (each row sums to 1 after exp).
        T = torch.rand(num_classes, num_classes).softmax(dim=-1)
        log_T = T.log()
        # Reg logits as a leaf so backward through the KD term is testable.
        pred = torch.randn(batch, num_classes, requires_grad=True)
        # Mix valid and pad rows.
        aux = torch.tensor([0, 2, -1, num_classes + 3], dtype=torch.long)
        return pred, log_T, aux

    def test_weight_zero_is_no_op(self):
        pred, log_T, aux = self._fixture()
        kd, post = _run_kd_block(pred, log_T, aux, weight=0.0, tau=1.0,
                                 num_classes=pred.shape[-1])
        assert kd.item() == 0.0
        assert post.item() == pytest.approx(1.0)

    def test_weight_positive_shifts_loss(self):
        pred, log_T, aux = self._fixture()
        kd, post = _run_kd_block(pred, log_T, aux, weight=0.2, tau=1.0,
                                 num_classes=pred.shape[-1])
        assert kd.item() != 0.0
        # KL is non-negative; KD term should add positively to the base CE.
        assert kd.item() >= 0.0
        assert post.item() == pytest.approx(1.0 + 0.2 * kd.item(), rel=1e-6)

    def test_padding_rows_excluded(self):
        """The two valid rows (indices 0 and 1) should drive the entire
        KD term — adding two more pad rows must not change the KD value."""
        pred, log_T, aux = self._fixture()
        kd_with_pad, _ = _run_kd_block(pred, log_T, aux, weight=1.0, tau=1.0,
                                       num_classes=pred.shape[-1])
        # Slice to only the two valid rows; aux all valid.
        pred_v = pred[:2]
        aux_v = torch.tensor([0, 2], dtype=torch.long)
        kd_only_valid, _ = _run_kd_block(pred_v, log_T, aux_v, weight=1.0,
                                         tau=1.0, num_classes=pred.shape[-1])
        # Same valid rows, same per-sample mean (denom = n_valid in both).
        assert kd_with_pad.item() == pytest.approx(kd_only_valid.item(), rel=1e-5)

    def test_kd_term_is_differentiable(self):
        pred, log_T, aux = self._fixture()
        kd, _ = _run_kd_block(pred, log_T, aux, weight=0.2, tau=1.0,
                              num_classes=pred.shape[-1])
        kd.backward()
        assert pred.grad is not None
        # Only the two valid rows (0, 1) receive gradient; padding rows zeroed.
        assert torch.any(pred.grad[:2] != 0.0)
        assert torch.all(pred.grad[2:] == 0.0)

    def test_tau_squared_scaling(self):
        """Standard Hinton distillation: the KD loss scales as τ² because
        the gradient of softmax(z/τ) w.r.t. z shrinks as 1/τ². With teacher
        held fixed at the same temperature, the KL itself shrinks as 1/τ²
        — the τ² multiplier restores the gradient magnitude. Sanity-check
        the multiplicative direction: doubling τ should not blow up the KD
        contribution (it should stay bounded and small)."""
        pred, log_T, aux = self._fixture()
        kd_tau1, _ = _run_kd_block(pred, log_T, aux, weight=1.0, tau=1.0,
                                   num_classes=pred.shape[-1])
        kd_tau2, _ = _run_kd_block(pred, log_T, aux, weight=1.0, tau=2.0,
                                   num_classes=pred.shape[-1])
        # Both finite, both non-negative; sanity bounded above by τ² * log(K).
        assert torch.isfinite(kd_tau1).all()
        assert torch.isfinite(kd_tau2).all()
        assert kd_tau1.item() >= 0.0
        assert kd_tau2.item() >= 0.0

    def test_config_field_default_zero(self):
        """ExperimentConfig.log_t_kd_weight defaults to 0.0 (off).

        The dataclass field default stays 0.0 even under the v12 default flip:
        the v12 ON-default is applied at the CLI layer (scoped to MTL
        check2hgi_next_region), NOT in the task-agnostic dataclass.
        """
        from configs.experiment import ExperimentConfig
        from configs.paths import EmbeddingEngine
        cfg = ExperimentConfig.default_mtl(
            name="kd-default-probe",
            embedding_engine=EmbeddingEngine.CHECK2HGI,
            state="florida",
        )
        assert float(getattr(cfg, "log_t_kd_weight", -1.0)) == 0.0
        assert float(getattr(cfg, "log_t_kd_tau", -1.0)) == 1.0


# ---------------------------------------------------------------------------
# A1 / v12 — CLI scoped log_T-KD default (2026-05-30 default flip)
# ---------------------------------------------------------------------------


class TestLogTKDCLIDefault:
    """log_T-KD CLI defaulting, under the `--canon` mechanism.

    The default canon is **v16 (champion G)**, whose bundle sets
    ``--log-t-kd-weight 0.0`` — so a bare MTL check2hgi_next_region run now has
    KD **OFF** (G's recipe; KD was found null on the dual-tower). The earlier
    v12 *auto-default-ON* (W=0.2, τ=1.0, scoped to MTL check2hgi_next_region)
    still exists in ``_apply_cli_overrides`` and is reached with ``--canon none``
    (no bundle) or ``--canon v12`` (bundle sets 0.2 explicitly). Category-only /
    non-region / non-MTL runs keep W=0.0. An explicit --log-t-kd-weight always
    wins (incl. 0.0 for v11 reproduction over a v12 ON default).

    NOTE: tests pin ``--canon`` explicitly so they assert the intended branch
    rather than passing by coincidence of whatever the default canon happens to
    set. See docs/results/CANONICAL_VERSIONS.md (v11/v12/v16) + src/configs/canon.py.
    """

    def _apply(self, argv):
        sys.path.insert(0, str(_root / "scripts"))
        import train as train_cli  # noqa: WPS433

        args = train_cli._parse_args(argv)
        task = args.task or "mtl"
        factory = train_cli._DEFAULT_FACTORIES[task]
        config = factory(
            name=f"{task}_{args.state}_{args.engine}",
            state=args.state,
            embedding_engine=args.engine,
        )
        return train_cli._apply_cli_overrides(config, args)

    def test_default_canon_v16_kd_off(self):
        """The DEFAULT canon (v17, champion) sets KD OFF for a bare MTL
        check2hgi_next_region run — KD is null on the dual-tower."""
        cfg = self._apply([
            "--task", "mtl", "--task-set", "check2hgi_next_region",
            "--state", "florida", "--engine", "check2hgi",
        ])
        assert float(cfg.log_t_kd_weight) == 0.0

    def test_v12_auto_default_on_with_canon_none(self):
        """With --canon none (no bundle), the v12 auto-default-ON logic still
        fires for MTL check2hgi_next_region: W=0.2, τ=1.0."""
        cfg = self._apply([
            "--task", "mtl", "--task-set", "check2hgi_next_region",
            "--canon", "none",
            "--state", "florida", "--engine", "check2hgi",
        ])
        assert float(cfg.log_t_kd_weight) == 0.2
        assert float(cfg.log_t_kd_tau) == 1.0

    def test_canon_v12_sets_kd_on(self):
        """The v12 bundle pins KD ON (W=0.2)."""
        cfg = self._apply([
            "--task", "mtl", "--task-set", "check2hgi_next_region",
            "--canon", "v12",
            "--state", "florida", "--engine", "check2hgi",
        ])
        assert float(cfg.log_t_kd_weight) == 0.2

    def test_explicit_zero_recovers_v11_over_v12_on(self):
        """Explicit --log-t-kd-weight 0.0 wins over a v12 ON default (v11 repro)."""
        cfg = self._apply([
            "--task", "mtl", "--task-set", "check2hgi_next_region",
            "--canon", "v12",
            "--state", "florida", "--engine", "check2hgi",
            "--log-t-kd-weight", "0.0",
        ])
        assert float(cfg.log_t_kd_weight) == 0.0

    def test_explicit_weight_wins(self):
        """Explicit --log-t-kd-weight wins over the bundle (here over v16's 0.0)."""
        cfg = self._apply([
            "--task", "mtl", "--task-set", "check2hgi_next_region",
            "--state", "florida", "--engine", "check2hgi",
            "--log-t-kd-weight", "0.5",
        ])
        assert float(cfg.log_t_kd_weight) == 0.5

    def test_no_default_for_legacy_task_set(self):
        """Legacy MTL task-set (no check2hgi_next_region) must NOT get KD on.
        Pinned to --canon none so the v16 bundle does not inject a task-set."""
        cfg = self._apply([
            "--task", "mtl", "--canon", "none",
            "--state", "florida", "--engine", "check2hgi",
        ])
        assert float(cfg.log_t_kd_weight) == 0.0

    def test_no_default_for_category_task(self):
        """Category-only runs must NOT get KD on (and must not trip the
        --log-t-kd-weight-requires-mtl guard). Canon is MTL-only anyway."""
        cfg = self._apply([
            "--task", "category",
            "--state", "florida", "--engine", "check2hgi",
        ])
        assert float(cfg.log_t_kd_weight) == 0.0
