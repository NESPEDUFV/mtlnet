"""Comprehensive tests for the ml_history package."""

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
import torch

from tracking.metric_store import MetricStore
from tracking.best_tracker import BestModelTracker
from tracking.fold import TaskHistory, FoldHistory
from tracking.experiment import MLHistory, FlopsMetrics
from tracking.parms.neural import NeuralParams
from tracking.utils.dataset import DatasetHistory
from tracking.utils.time_history import TimeHistory


# ── Group A: MetricStore ──────────────────────────────────────────────


class TestMetricStore:

    def test_log_and_retrieve(self):
        store = MetricStore()
        store.log(loss=0.5, accuracy=0.8)
        store.log(loss=0.3, accuracy=0.9)
        store.log(loss=0.1, accuracy=0.95)
        assert store['loss'] == [0.5, 0.3, 0.1]
        assert store['accuracy'] == [0.8, 0.9, 0.95]

    def test_arbitrary_keys(self):
        store = MetricStore()
        store.log(precision=0.7, recall=0.6, custom_thing=42.0)
        assert 'precision' in store
        assert 'recall' in store
        assert 'custom_thing' in store
        assert store['custom_thing'] == [42.0]

    def test_best_max(self):
        store = MetricStore()
        store.log(f1=0.3)
        store.log(f1=0.7)
        store.log(f1=0.5)
        idx, val = store.best('f1', mode='max')
        assert idx == 1
        assert val == 0.7

    def test_best_min(self):
        store = MetricStore()
        store.log(loss=0.9)
        store.log(loss=0.2)
        store.log(loss=0.5)
        idx, val = store.best('loss', mode='min')
        assert idx == 1
        assert val == 0.2

    def test_latest(self):
        store = MetricStore()
        store.log(loss=0.5)
        store.log(loss=0.3)
        assert store.latest('loss') == 0.3

    def test_to_dataframe(self):
        store = MetricStore()
        store.log(loss=0.5, acc=0.8)
        store.log(loss=0.3, acc=0.9)
        df = store.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['epoch', 'loss', 'acc']
        assert list(df['epoch']) == [1, 2]
        assert list(df['loss']) == [0.5, 0.3]

    def test_contains(self):
        store = MetricStore()
        store.log(loss=0.5)
        assert 'loss' in store
        assert 'missing' not in store

    def test_empty(self):
        store = MetricStore()
        assert store.num_epochs() == 0
        assert list(store.keys()) == []
        assert len(store) == 0

    def test_get_with_default(self):
        store = MetricStore()
        assert store.get('missing') is None
        assert store.get('missing', []) == []

    def test_num_epochs(self):
        store = MetricStore()
        store.log(loss=0.5)
        store.log(loss=0.3)
        assert store.num_epochs() == 2

    def test_keys_and_items(self):
        store = MetricStore()
        store.log(a=1.0, b=2.0)
        assert set(store.keys()) == {'a', 'b'}
        items = dict(store.items())
        assert items == {'a': [1.0], 'b': [2.0]}


# ── Group B: BestModelTracker ─────────────────────────────────────────


class TestBestModelTracker:

    def test_improves(self):
        tracker = BestModelTracker(monitor='f1', mode='max')
        result1 = tracker.update(epoch=0, metric_value=0.5, model_state={'w': 1})
        result2 = tracker.update(epoch=1, metric_value=0.7, model_state={'w': 2})
        assert result1 is True
        assert result2 is True
        assert tracker.best_state == {'w': 2}
        assert tracker.best_epoch == 1
        assert tracker.best_value == 0.7

    def test_no_improvement(self):
        tracker = BestModelTracker(monitor='f1', mode='max')
        tracker.update(epoch=0, metric_value=0.7, model_state={'w': 1})
        result = tracker.update(epoch=1, metric_value=0.5, model_state={'w': 2})
        assert result is False
        assert tracker.best_state == {'w': 1}
        assert tracker.best_epoch == 0

    def test_min_mode(self):
        tracker = BestModelTracker(monitor='loss', mode='min')
        tracker.update(epoch=0, metric_value=0.5, model_state={'w': 1})
        result = tracker.update(epoch=1, metric_value=0.3, model_state={'w': 2})
        assert result is True
        assert tracker.best_value == 0.3
        assert tracker.best_state == {'w': 2}

    def test_min_mode_no_improvement(self):
        tracker = BestModelTracker(monitor='loss', mode='min')
        tracker.update(epoch=0, metric_value=0.3, model_state={'w': 1})
        result = tracker.update(epoch=1, metric_value=0.5, model_state={'w': 2})
        assert result is False
        assert tracker.best_value == 0.3

    def test_deepcopy_state(self):
        """Verify model state is deep-copied, not a reference."""
        tracker = BestModelTracker()
        state = {'w': [1, 2, 3]}
        tracker.update(epoch=0, metric_value=0.5, model_state=state)
        state['w'].append(4)  # mutate original
        assert tracker.best_state == {'w': [1, 2, 3]}  # copy unaffected

    def test_elapsed_time(self):
        tracker = BestModelTracker()
        tracker.update(epoch=0, metric_value=0.5, model_state={}, elapsed_time=10.5)
        assert tracker.best_time == 10.5

    def test_torch_state_dict_isolation(self):
        """Verify saved state is isolated from the original model tensors."""
        model = torch.nn.Linear(4, 2)
        tracker = BestModelTracker(monitor='f1', mode='max')
        tracker.update(epoch=0, metric_value=0.5, model_state=model.state_dict())

        # Mutate the model weights
        with torch.no_grad():
            model.weight.fill_(999.0)

        # Saved state must be untouched
        assert (tracker.best_state['weight'] != 999.0).any()

    def test_torch_state_dict_stored_on_cpu(self):
        """Verify state dict tensors are moved to CPU for storage efficiency."""
        model = torch.nn.Linear(4, 2)
        tracker = BestModelTracker(monitor='f1', mode='max')
        tracker.update(epoch=0, metric_value=0.5, model_state=model.state_dict())

        for key, tensor in tracker.best_state.items():
            assert tensor.device == torch.device('cpu'), (
                f"State dict key '{key}' should be on CPU, got {tensor.device}"
            )

    def test_torch_state_dict_loadable(self):
        """Verify the saved state can be loaded back into a model."""
        model = torch.nn.Linear(4, 2)
        tracker = BestModelTracker(monitor='f1', mode='max')

        # Save initial state
        tracker.update(epoch=0, metric_value=0.5, model_state=model.state_dict())
        original_weight = model.weight.data.clone()

        # Mutate the model
        with torch.no_grad():
            model.weight.fill_(0.0)

        # Restore from tracker — must work regardless of storage device
        model.load_state_dict(tracker.best_state)
        assert torch.allclose(model.weight.data, original_weight)

    def test_only_copies_on_improvement(self):
        """Verify that state is NOT stored when metric doesn't improve."""
        tracker = BestModelTracker(monitor='f1', mode='max')
        state_good = {'w': torch.tensor([1.0, 2.0])}
        state_bad = {'w': torch.tensor([99.0, 99.0])}

        tracker.update(epoch=0, metric_value=0.8, model_state=state_good)
        tracker.update(epoch=1, metric_value=0.5, model_state=state_bad)

        # Should still hold the first (better) state
        assert torch.allclose(tracker.best_state['w'], torch.tensor([1.0, 2.0]))

    def test_successive_improvements_keep_latest(self):
        """Verify successive improvements replace the stored state."""
        model = torch.nn.Linear(4, 2)
        tracker = BestModelTracker(monitor='f1', mode='max')

        tracker.update(epoch=0, metric_value=0.5, model_state=model.state_dict())

        # Train (mutate) model and save again with better metric
        with torch.no_grad():
            model.weight.fill_(42.0)
        tracker.update(epoch=1, metric_value=0.9, model_state=model.state_dict())

        # Should hold the second state
        assert (tracker.best_state['weight'] == 42.0).all()
        assert tracker.best_epoch == 1

    def test_training_loop_isolation(self):
        """Simulate a real training loop: save best at epoch 2, train 10 more
        epochs, verify saved state is from epoch 2 and not corrupted.

        This is the exact scenario that deepcopy was originally added to protect
        against — the model keeps training after the best checkpoint is saved.
        """
        model = torch.nn.Linear(8, 4)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        criterion = torch.nn.CrossEntropyLoss()
        tracker = BestModelTracker(monitor='f1', mode='max')

        # Fake F1 scores: peaks at epoch 2, then degrades
        f1_scores = [0.3, 0.5, 0.9, 0.7, 0.6, 0.5, 0.4, 0.4, 0.3, 0.3]

        for epoch, f1 in enumerate(f1_scores):
            # Simulate a training step that mutates model weights
            x = torch.randn(16, 8)
            y = torch.randint(0, 4, (16,))
            loss = criterion(model(x), y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            tracker.update(epoch=epoch, metric_value=f1, model_state=model.state_dict())

        # Best should be from epoch 2
        assert tracker.best_epoch == 2
        assert tracker.best_value == 0.9

        # The saved state must restore a model that produces different outputs
        # than the current (overtrained) model — proving it's not a reference
        x_test = torch.randn(4, 8)
        output_current = model(x_test).detach()

        model.load_state_dict(tracker.best_state)
        output_restored = model(x_test).detach()

        # Outputs must differ (model trained for 7 more epochs after best)
        assert not torch.allclose(output_current, output_restored, atol=1e-6), (
            "Restored model produces identical outputs to current model — "
            "state was likely a reference, not a copy!"
        )

    def test_state_dict_is_not_a_reference_to_model_params(self):
        """Directly verify that state_dict() + _snapshot_state breaks the
        reference chain to the model's live parameters."""
        model = torch.nn.Linear(4, 2)
        tracker = BestModelTracker(monitor='f1', mode='max')

        tracker.update(epoch=0, metric_value=0.5, model_state=model.state_dict())
        saved_weight = tracker.best_state['weight']

        # The saved tensor must not share storage with the model's live weight
        assert saved_weight.data_ptr() != model.weight.data_ptr(), (
            "Saved state shares memory with live model parameter — "
            "this means mutations to the model will corrupt the saved state!"
        )


# ── Group C: TaskHistory & FoldHistory ────────────────────────────────


class TestTaskHistory:

    def test_log_train(self):
        th = TaskHistory()
        th.log_train(loss=0.5, accuracy=0.8, f1=0.6)
        th.log_train(loss=0.3, accuracy=0.9, f1=0.8)
        assert th.train['loss'] == [0.5, 0.3]
        assert th.train['f1'] == [0.6, 0.8]

    def test_log_val_with_best_model(self):
        th = TaskHistory(monitor='f1', mode='max')
        th.log_val(loss=0.4, f1=0.6, model_state={'w': 1})
        th.log_val(loss=0.3, f1=0.8, model_state={'w': 2})
        assert th.val['f1'] == [0.6, 0.8]
        assert th.best.best_state == {'w': 2}
        assert th.best.best_epoch == 1

    def test_log_val_without_model_state(self):
        th = TaskHistory()
        th.log_val(loss=0.4, f1=0.6)
        assert th.val['f1'] == [0.6]
        assert th.best.best_state == {}  # untouched

    def test_log_val_monitor_not_in_kwargs(self):
        """If monitored metric not provided, best tracker not updated."""
        th = TaskHistory(monitor='f1')
        th.log_val(loss=0.4, model_state={'w': 1})
        assert th.best.best_epoch == -1  # not updated

    def test_report(self):
        th = TaskHistory()
        th.report = {'0': {'precision': 0.8}}
        assert th.report == {'0': {'precision': 0.8}}


class TestFoldHistory:

    def test_task_access(self):
        fold = FoldHistory(0, {'next', 'category'})
        assert isinstance(fold.task('next'), TaskHistory)
        assert isinstance(fold.task('category'), TaskHistory)

    def test_task_missing_raises(self):
        fold = FoldHistory(0, {'next'})
        with pytest.raises(ValueError, match="Task 'missing'"):
            fold.task('missing')

    def test_log_train_convenience(self):
        fold = FoldHistory(0, {'next'})
        fold.log_train('next', loss=0.5, f1=0.6)
        assert fold.task('next').train['loss'] == [0.5]

    def test_log_val_convenience(self):
        fold = FoldHistory(0, {'next'})
        fold.log_val('next', loss=0.3, f1=0.8, model_state={'w': 1})
        assert fold.task('next').val['f1'] == [0.8]
        assert fold.task('next').best.best_state == {'w': 1}

    def test_diagnostics(self):
        fold = FoldHistory(0, {'next'})
        fold.log_diagnostic(grad_norm=1.2, learning_rate=1e-3)
        fold.log_diagnostic(grad_norm=0.8, learning_rate=5e-4)
        assert fold.diagnostics['grad_norm'] == [1.2, 0.8]
        assert fold.diagnostics['learning_rate'] == [1e-3, 5e-4]

    def test_artifacts(self):
        fold = FoldHistory(0, {'next'})
        cm = {'matrix': [[10, 2], [3, 15]], 'labels': ['A', 'B']}
        fold.add_artifact('confusion_matrix', cm)
        assert fold.artifacts['confusion_matrix'] == cm

    def test_standalone(self):
        fold = FoldHistory.standalone({'next'})
        assert fold.fold_number == 0
        # Timer should be started
        assert fold.timer.start_time is not None

    def test_timer(self):
        fold = FoldHistory(0, {'next'})
        fold.start()
        time.sleep(0.01)
        fold.end()
        assert fold.timer.duration > 0

    def test_model_task(self):
        """Test optional model-level task for MTL combined metrics."""
        fold = FoldHistory(0, {'next', 'category'})
        fold.model_task = TaskHistory()
        fold.model_task.log_train(loss=0.5)
        assert fold.model_task.train['loss'] == [0.5]

    def test_per_task_monitor_overrides(self):
        """AUDIT-C2: ``task_monitors`` propagates per-task monitor key.

        Default (``monitor='f1'``) should apply to tasks not in the map;
        overridden tasks should track their own metric. This is the fix
        for the F1-vs-Acc@1 mismatch that under-reported FL MTL by ~3.5pp.
        """
        fold = FoldHistory(
            0, {'next_category', 'next_region'},
            monitor='f1', mode='max',
            task_monitors={'next_region': 'accuracy'},
        )
        assert fold.task('next_category').best.monitor == 'f1'
        assert fold.task('next_region').best.monitor == 'accuracy'

    def test_per_task_monitor_default_when_unset(self):
        fold = FoldHistory(0, {'a', 'b'}, monitor='f1', mode='max')
        assert fold.task('a').best.monitor == 'f1'
        assert fold.task('b').best.monitor == 'f1'

    def test_mlhistory_propagates_task_monitors(self):
        """AUDIT-C2: MLHistory threads ``task_monitors`` into every fold."""
        h = MLHistory(
            model_name='test',
            tasks={'next_category', 'next_region'},
            num_folds=3,
            task_monitors={'next_region': 'accuracy'},
        )
        for fold in h.folds:
            assert fold.task('next_category').best.monitor == 'f1'
            assert fold.task('next_region').best.monitor == 'accuracy'

    def test_b1_min_epoch_skips_init_artifact(self):
        """F50 B1: a higher ep>=min_epoch peak must beat the ep<min_epoch peak.

        Mirrors the GETNext alpha_init=2.0 case: ep 1 has top10=80 (init
        prior), ep 3 has top10=70 (post-training trough). Without
        min_epoch, selector picks ep 1; with min_epoch=2, it picks ep 3.
        """
        fold = FoldHistory(0, {'r'}, monitor='top10', mode='max', min_epoch=2)
        # ep 0 — init artifact, would otherwise win
        fold.log_val('r', top10=0.80, model_state={'w': 1})
        assert fold.task('r').best.best_epoch == -1, "ep 0 < min_epoch=2; reject"

        fold.log_val('r', top10=0.65, model_state={'w': 2})  # ep 1
        assert fold.task('r').best.best_epoch == -1, "ep 1 < min_epoch=2; reject"

        fold.log_val('r', top10=0.70, model_state={'w': 3})  # ep 2
        assert fold.task('r').best.best_epoch == 2, "ep 2 eligible"
        assert fold.task('r').best.best_value == 0.70

        fold.log_val('r', top10=0.75, model_state={'w': 4})  # ep 3
        assert fold.task('r').best.best_epoch == 3
        assert fold.task('r').best.best_value == 0.75

    def test_b1_min_epoch_default_zero_legacy_behaviour(self):
        fold = FoldHistory(0, {'r'}, monitor='top10', mode='max')  # no min_epoch
        fold.log_val('r', top10=0.80, model_state={'w': 1})
        assert fold.task('r').best.best_epoch == 0
        assert fold.task('r').best.best_value == 0.80


# ── Group D: MLHistory ────────────────────────────────────────────────


class TestMLHistory:

    def test_init_single_task_string(self):
        h = MLHistory('Test', tasks='next', num_folds=3)
        assert h.tasks == {'next'}
        assert len(h.folds) == 3
        assert h.curr_i_fold == 0

    def test_init_multi_task(self):
        h = MLHistory('Test', tasks={'next', 'category'}, num_folds=2)
        assert h.tasks == {'next', 'category'}
        assert len(h.folds) == 2

    def test_context_manager(self):
        h = MLHistory('Test', tasks='next', num_folds=1)
        with h:
            time.sleep(0.01)
        assert h.start_date is not None
        assert h.end_date is not None
        assert h.timer.duration > 0

    def test_iterator(self):
        h = MLHistory('Test', tasks='next', num_folds=3)
        folds_yielded = list(h)
        assert len(folds_yielded) == 3
        assert all(isinstance(f, FoldHistory) for f in folds_yielded)

    def test_step(self):
        h = MLHistory('Test', tasks='next', num_folds=3)
        h.start()
        assert h.curr_i_fold == 0
        h.step()
        assert h.curr_i_fold == 1
        h.step()
        assert h.curr_i_fold == 2

    def test_step_last_fold_ends(self):
        h = MLHistory('Test', tasks='next', num_folds=2)
        h.start()
        h.step()  # fold 0 -> 1
        h.step()  # fold 1 -> end
        assert h.end_date is not None

    def test_fold_property(self):
        h = MLHistory('Test', tasks='next', num_folds=2)
        assert h.fold is h.get_curr_fold()
        assert h.fold is h.folds[0]

    def test_set_model_parms(self):
        h = MLHistory('Test', tasks='next')
        parms = NeuralParams(batch_size=32, num_epochs=10, learning_rate=1e-3)
        h.set_model_parms(parms)
        assert h.model_parms.batch_size == 32

    def test_set_model_arch(self):
        h = MLHistory('Test', tasks='next')
        h.set_model_arch('Transformer(d_model=64)')
        assert h.model_arch == 'Transformer(d_model=64)'

    def test_set_flops(self):
        h = MLHistory('Test', tasks='next')
        flops = FlopsMetrics(flops=1e6, params=1e4)
        h.set_flops(flops)
        assert h.flops.flops == 1e6

    def test_monitor_propagated_to_folds(self):
        h = MLHistory('Test', tasks='next', num_folds=2, monitor='accuracy', mode='max')
        for fold in h.folds:
            for th in fold.tasks.values():
                assert th.best.monitor == 'accuracy'
                assert th.best.mode == 'max'


# ── Group E: FlopsMetrics ────────────────────────────────────────────


class TestFlopsMetrics:

    def test_to_dict(self):
        fm = FlopsMetrics(flops=1e6, params=5000)
        d = fm.to_dict()
        assert d['flops'] == 1e6
        assert d['params'] == 5000
        assert d['memory'] == []
        assert d['inference_time'] == []

    def test_mutable_lists(self):
        fm = FlopsMetrics(flops=1e6, params=5000)
        fm.memory.append(100.0)
        fm.training_time.append(60.0)
        d = fm.to_dict()
        assert d['memory'] == [100.0]
        assert d['training_time'] == [60.0]


# ── Group F: Utility Classes ─────────────────────────────────────────


class TestTimeHistory:

    def test_start_stop_duration(self):
        th = TimeHistory()
        th.start()
        time.sleep(0.01)
        th.stop()
        assert th.duration > 0

    def test_get_duration_before_stop_raises(self):
        th = TimeHistory()
        th.start()
        th.duration = None  # reset
        with pytest.raises(ValueError):
            th.get_duration()

    def test_timer_running(self):
        th = TimeHistory()
        th.start()
        elapsed = th.timer()
        assert elapsed >= 0


class TestDatasetHistory:

    def test_to_json(self):
        dh = DatasetHistory(raw_data='data/train.csv', description='Training set')
        j = dh.to_json()
        assert j['raw_data'] == 'data/train.csv'
        assert j['description'] == 'Training set'


class TestNeuralParams:

    def test_init(self):
        p = NeuralParams(
            batch_size=64,
            num_epochs=50,
            learning_rate=1e-3,
            optimizer='AdamW',
        )
        assert p.batch_size == 64
        assert p.learning_rate == 1e-3
        assert p.optimizer == 'AdamW'

    def test_kwargs(self):
        p = NeuralParams(batch_size=32, num_epochs=10, learning_rate=1e-4)
        assert p.scheduler == ''
        assert p.criterion == {}


# ── Group G: Integration ─────────────────────────────────────────────


class TestIntegrationSingleTask:
    """Simulate a 2-fold, 3-epoch single-task training loop."""

    def test_full_loop(self):
        h = MLHistory('TestModel', tasks='next', num_folds=2)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=3, learning_rate=1e-3))

        for fold_idx in range(2):
            fold = h.get_curr_fold()

            for epoch in range(3):
                # Train
                fold.log_train('next', loss=1.0 - epoch * 0.2, accuracy=0.5 + epoch * 0.1, f1=0.4 + epoch * 0.15)
                # Val
                fold.log_val(
                    'next',
                    loss=0.8 - epoch * 0.15,
                    accuracy=0.6 + epoch * 0.1,
                    f1=0.5 + epoch * 0.15,
                    model_state={'epoch': epoch},
                    elapsed_time=float(epoch),
                )
                # Diagnostics
                fold.log_diagnostic(grad_norm=1.0 - epoch * 0.2, learning_rate=1e-3 * (0.9 ** epoch))

            # Post-training artifacts
            fold.task('next').report = {'0': {'precision': 0.8, 'recall': 0.7, 'f1-score': 0.75, 'support': 100}}
            fold.add_artifact('confusion_matrix', {'matrix': [[50, 10], [5, 35]], 'labels': ['A', 'B']})

            h.step()

        # Verify fold 0
        f0 = h.folds[0]
        assert f0.task('next').train.num_epochs() == 3
        assert f0.task('next').val.num_epochs() == 3
        assert f0.task('next').best.best_epoch == 2  # last epoch had highest f1
        assert f0.task('next').best.best_state == {'epoch': 2}
        assert f0.diagnostics.num_epochs() == 3
        assert 'confusion_matrix' in f0.artifacts

        # Verify fold 1
        f1 = h.folds[1]
        assert f1.task('next').train.num_epochs() == 3

        # Verify MLHistory state
        assert h.end_date is not None


class TestIntegrationMTL:
    """Simulate a 2-fold, 2-epoch MTL training loop with 2 tasks."""

    def test_full_mtl_loop(self):
        h = MLHistory('MTLNet', tasks={'next', 'category'}, num_folds=2)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=64, num_epochs=2, learning_rate=1e-4))

        for fold_idx in range(2):
            fold = h.get_curr_fold()

            # Optional model-level tracking
            fold.model_task = TaskHistory()

            for epoch in range(2):
                # Combined model loss
                fold.model_task.log_train(loss=2.0 - epoch * 0.5)

                # Per-task metrics
                for task_name in ('next', 'category'):
                    fold.log_train(task_name, loss=1.0 - epoch * 0.2, f1=0.4 + epoch * 0.2)
                    fold.log_val(
                        task_name,
                        loss=0.8 - epoch * 0.1,
                        f1=0.5 + epoch * 0.2,
                        model_state={'epoch': epoch, 'task': task_name},
                        elapsed_time=float(epoch),
                    )

            # Reports
            for task_name in ('next', 'category'):
                fold.task(task_name).report = {
                    'macro avg': {'precision': 0.7, 'recall': 0.6, 'f1-score': 0.65, 'support': 200}
                }

            h.step()

        # Verify both tasks tracked
        f0 = h.folds[0]
        assert f0.task('next').train.num_epochs() == 2
        assert f0.task('category').train.num_epochs() == 2
        assert f0.model_task.train['loss'] == [2.0, 1.5]

        # Best models tracked independently per task
        assert f0.task('next').best.best_epoch == 1
        assert f0.task('category').best.best_epoch == 1


class TestIntegrationStorage:
    """Test that storage.save() produces correct directory structure and files."""

    def test_save_creates_directories(self, tmp_path):
        h = MLHistory('Test', tasks='next', num_folds=1)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=2, learning_rate=1e-3))

        fold = h.get_curr_fold()
        fold.log_train('next', loss=0.5, accuracy=0.8, f1=0.6)
        fold.log_val('next', loss=0.4, accuracy=0.85, f1=0.7)
        fold.task('next').report = {
            '0': {'precision': 0.8, 'recall': 0.7, 'f1-score': 0.75, 'support': 100},
            'macro avg': {'precision': 0.8, 'recall': 0.7, 'f1-score': 0.75, 'support': 100},
        }
        h.step()

        base = h.storage.save(tmp_path, label_map={0: 'Food'})
        assert base.exists()

        # Check subdirectories
        for subdir in ('model', 'metrics', 'folds', 'summary', 'plots'):
            assert (base / subdir).exists(), f"Missing directory: {subdir}"

    def test_save_metrics_csv(self, tmp_path):
        h = MLHistory('Test', tasks='next', num_folds=1)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=2, learning_rate=1e-3))

        fold = h.get_curr_fold()
        for i in range(3):
            fold.log_train('next', loss=1.0 - i * 0.2, accuracy=0.5 + i * 0.1, f1=0.4 + i * 0.1)
            fold.log_val('next', loss=0.8 - i * 0.1, accuracy=0.6 + i * 0.1, f1=0.5 + i * 0.1)
        fold.task('next').report = {
            'macro avg': {'precision': 0.7, 'recall': 0.6, 'f1-score': 0.65, 'support': 200}
        }
        h.step()

        base = h.storage.save(tmp_path)
        metrics_dir = base / 'metrics'

        # Should have train and val CSV for fold 1, task 'next'
        csv_files = list(metrics_dir.glob('*.csv'))
        assert len(csv_files) >= 2

        # Read one and verify columns
        train_csvs = [f for f in csv_files if 'train' in f.name]
        assert len(train_csvs) >= 1
        df = pd.read_csv(train_csvs[0])
        assert 'epoch' in df.columns
        assert len(df) == 3

    def test_mtl_summary_uses_joint_checkpoint_and_labels_diagnostics(self, tmp_path):
        h = MLHistory('MTLNet', tasks={'next', 'category'}, num_folds=1)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=3, learning_rate=1e-3))

        fold = h.get_curr_fold()
        fold.model_task = TaskHistory()

        joint_scores = [0.50, 0.70, 0.65]
        next_f1 = [0.20, 0.60, 0.90]
        category_f1 = [0.80, 0.80, 0.40]
        for epoch, joint in enumerate(joint_scores):
            fold.model_task.log_val(
                loss=1.0 - epoch * 0.1,
                f1=joint,
                accuracy=0.0,
                model_state={'epoch': epoch},
                elapsed_time=float(epoch),
            )
            fold.log_val(
                'next',
                loss=0.0,
                accuracy=0.30 + epoch * 0.1,
                f1=next_f1[epoch],
                model_state={'epoch': epoch},
                elapsed_time=float(epoch),
            )
            fold.log_val(
                'category',
                loss=0.0,
                accuracy=0.50 + epoch * 0.1,
                f1=category_f1[epoch],
                model_state={'epoch': epoch},
                elapsed_time=float(epoch),
            )

        for task_name in ('next', 'category'):
            fold.task(task_name).report = {
                'macro avg': {
                    'precision': 0.7,
                    'recall': 0.6,
                    'f1-score': 0.65,
                    'support': 200,
                }
            }

        h.step()
        base = h.storage.save(tmp_path)

        fold_info = json.loads((base / 'folds' / 'fold1_info.json').read_text())
        assert 'best_epochs' not in fold_info
        assert fold_info['primary_checkpoint']['selection_metric'] == 'joint_score'
        assert fold_info['primary_checkpoint']['epoch'] == 1
        assert fold_info['primary_checkpoint']['joint_score'] == pytest.approx(0.70)
        assert fold_info['primary_checkpoint']['task_metrics']['next']['f1'] == pytest.approx(0.60)
        assert fold_info['diagnostic_best_epochs']['next']['epoch'] == 2
        assert fold_info['diagnostic_best_epochs']['next']['f1'] == pytest.approx(0.90)

        summary = json.loads((base / 'summary' / 'full_summary.json').read_text())
        assert summary['_selection']['primary'] == 'joint_score'
        assert summary['next']['f1']['mean'] == pytest.approx(0.60)
        assert summary['diagnostic_task_best']['next']['f1']['mean'] == pytest.approx(0.90)

        # C7 closure: every aggregate block stamps its aggregation_basis so a
        # downstream reader can disambiguate joint_best vs per_task_f1_best vs
        # per_metric_best without inferring it from the section name.
        assert summary['next']['aggregation_basis'] == 'joint_best'
        assert summary['diagnostic_task_best']['next']['aggregation_basis'] == 'per_task_f1_best'
        assert summary['per_metric_best']['next']['aggregation_basis'] == 'per_metric_best'
        # next.f1 best across the [0.20, 0.60, 0.90] series is 0.90.
        assert summary['per_metric_best']['next']['f1']['mean'] == pytest.approx(0.90)
        assert summary['_selection']['primary_basis'] == 'joint_best'
        assert summary['_selection']['diagnostic_basis'] == 'per_task_f1_best'
        assert summary['_selection']['per_metric_basis'] == 'per_metric_best'


class TestIntegrationNewMetrics:
    """End-to-end checks that the new metric keys (f1_weighted, top3_acc,
    mrr, ndcg_{k}, accuracy_macro) flow through FoldHistory, storage, and
    are reflected in fold_info.json and the auto-generated plots."""

    def _make_history_with_new_metrics(self, tmp_path):
        h = MLHistory('MetricTest', tasks='next', num_folds=1)
        h.start()
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=2, learning_rate=1e-3))

        fold = h.get_curr_fold()
        # Simulate compute_classification_metrics output across 3 epochs.
        series = [
            dict(loss=1.0, accuracy=0.50, accuracy_macro=0.48, f1=0.40,
                 f1_weighted=0.55, top3_acc=0.80, top5_acc=0.90,
                 mrr=0.60, ndcg_3=0.70, ndcg_5=0.75),
            dict(loss=0.8, accuracy=0.60, accuracy_macro=0.58, f1=0.50,
                 f1_weighted=0.65, top3_acc=0.85, top5_acc=0.92,
                 mrr=0.70, ndcg_3=0.77, ndcg_5=0.80),
            dict(loss=0.6, accuracy=0.70, accuracy_macro=0.68, f1=0.65,
                 f1_weighted=0.75, top3_acc=0.90, top5_acc=0.95,
                 mrr=0.80, ndcg_3=0.83, ndcg_5=0.86),
        ]
        for epoch_metrics in series:
            fold.log_train('next', **epoch_metrics)
            fold.log_val('next', model_state={'ok': True}, **epoch_metrics)

        fold.task('next').report = {
            'macro avg': {'precision': 0.7, 'recall': 0.65, 'f1-score': 0.65, 'support': 300}
        }
        h.step()
        return h

    def test_new_metric_keys_are_stored(self, tmp_path):
        h = self._make_history_with_new_metrics(tmp_path)
        val_keys = set(h.folds[0].task('next').val.keys())
        expected = {
            'loss', 'accuracy', 'accuracy_macro', 'f1', 'f1_weighted',
            'top3_acc', 'top5_acc', 'mrr', 'ndcg_3', 'ndcg_5',
        }
        assert expected.issubset(val_keys), (
            f"Missing new metric keys: {expected - val_keys}"
        )

    def test_fold_info_json_contains_all_metrics_at_best_epoch(self, tmp_path):
        h = self._make_history_with_new_metrics(tmp_path)
        base = h.storage.save(tmp_path)
        fold_info = json.loads((base / 'folds' / 'fold1_info.json').read_text())
        metrics_at_best = fold_info['best_epochs']['next']['metrics']
        # Best epoch is epoch 2 (F1 = 0.65), so values should match the
        # third row of the series above.
        assert metrics_at_best['f1'] == pytest.approx(0.65)
        assert metrics_at_best['f1_weighted'] == pytest.approx(0.75)
        assert metrics_at_best['top3_acc'] == pytest.approx(0.90)
        assert metrics_at_best['mrr'] == pytest.approx(0.80)
        assert metrics_at_best['ndcg_3'] == pytest.approx(0.83)
        # Legacy top-level keys still populated for backwards compatibility.
        assert fold_info['best_epochs']['next']['f1'] == pytest.approx(0.65)
        assert fold_info['best_epochs']['next']['accuracy'] == pytest.approx(0.70)

    def test_plots_generated_for_all_metrics(self, tmp_path):
        h = self._make_history_with_new_metrics(tmp_path)
        base = h.storage.save(tmp_path)
        plots_dir = base / 'plots' / 'next'
        # Auto-discovery should produce one plot per tracked metric.
        expected_plots = {
            'loss.png', 'accuracy.png', 'accuracy_macro.png',
            'f1.png', 'f1_weighted.png', 'top3_acc.png', 'top5_acc.png',
            'mrr.png', 'ndcg_3.png', 'ndcg_5.png',
        }
        actual = {p.name for p in plots_dir.glob('*.png')}
        assert expected_plots.issubset(actual), (
            f"Missing plots: {expected_plots - actual}"
        )


# ── Group H: Auto-Lifecycle ──────────────────────────────────────────


class TestMLHistoryAutoLifecycle:
    """Tests for constructor-driven auto-lifecycle (verbose, display_report, save_path, label_map)."""

    def test_constructor_accepts_label_map_and_save_path(self, tmp_path):
        h = MLHistory('M', tasks='next', num_folds=1, label_map={0: 'A'}, save_path=tmp_path)
        assert h._label_map == {0: 'A'}
        assert h._save_path == tmp_path

    def test_constructor_verbose_defaults_false(self):
        h = MLHistory('M', tasks='next', num_folds=1)
        assert h._verbose is False
        assert h._display_report is False

    def test_display_report_implies_verbose(self):
        h = MLHistory('M', tasks='next', num_folds=1, display_report=True)
        assert h._verbose is True
        assert h._display_report is True

    def test_label_map_propagated_to_display(self):
        lm = {0: 'Food', 1: 'Shop'}
        h = MLHistory('M', tasks='next', num_folds=1, label_map=lm, verbose=True)
        assert h.display.label_map == lm

    def test_end_idempotent(self):
        h = MLHistory('M', tasks='next', num_folds=1)
        h.start()
        h.get_curr_fold().log_train('next', loss=0.5)
        h.get_curr_fold().log_val('next', loss=0.4, f1=0.6)
        h.step()
        first_end_date = h.end_date
        h.end()  # second call
        assert h.end_date == first_end_date

    def test_auto_save_on_exit(self, tmp_path):
        h = MLHistory('M', tasks='next', num_folds=1, save_path=tmp_path, label_map={0: 'A'})
        h.set_model_parms(NeuralParams(batch_size=32, num_epochs=1, learning_rate=1e-3))
        with h:
            fold = h.get_curr_fold()
            fold.log_train('next', loss=0.5, accuracy=0.8, f1=0.6)
            fold.log_val('next', loss=0.4, accuracy=0.85, f1=0.7)
            fold.task('next').report = {'macro avg': {'precision': 0.8, 'recall': 0.7, 'f1-score': 0.75, 'support': 100}}
            h.step()
        # Verify files were auto-created
        result_dirs = list(tmp_path.rglob('model'))
        assert len(result_dirs) >= 1

    def test_no_auto_save_on_exception(self, tmp_path):
        h = MLHistory('M', tasks='next', num_folds=1, save_path=tmp_path)
        try:
            with h:
                raise ValueError("simulated error")
        except ValueError:
            pass
        # No save should have happened
        result_dirs = list(tmp_path.rglob('model'))
        assert len(result_dirs) == 0

    def test_no_auto_save_when_save_path_is_none(self):
        h = MLHistory('M', tasks='next', num_folds=1)
        h.start()
        h.get_curr_fold().log_train('next', loss=0.5)
        h.get_curr_fold().log_val('next', loss=0.4, f1=0.6)
        h.step()
        # No crash — end() and __exit__ work fine with no save_path

    def test_set_flops_auto_displays_when_verbose(self):
        h = MLHistory('M', tasks='next', num_folds=1, verbose=True)
        h.start()
        # Mock the display to verify flops() is called
        h._display = MagicMock()
        h.set_flops(FlopsMetrics(flops=1000, params=500))
        h._display.flops.assert_called_once()

    def test_silent_when_not_verbose(self):
        h = MLHistory('M', tasks='next', num_folds=2, verbose=False)
        h._display = MagicMock()
        h.start()
        fold = h.get_curr_fold()
        fold.log_train('next', loss=0.5)
        fold.log_val('next', loss=0.4, f1=0.6)
        h.step()
        h.end()
        # Display methods should never be called when verbose=False
        h._display.start_fold.assert_not_called()
        h._display.end_fold.assert_not_called()
        h._display.end_training.assert_not_called()

    def test_display_fires_when_verbose(self):
        h = MLHistory('M', tasks='next', num_folds=2, verbose=True)
        h._display = MagicMock()
        h.start()
        fold = h.get_curr_fold()
        fold.log_train('next', loss=0.5)
        fold.log_val('next', loss=0.4, f1=0.6)
        h.step()
        # After start() + step(), we should see start_fold (fold 0), end_fold (fold 0), start_fold (fold 1)
        assert h._display.start_fold.call_count == 2
        assert h._display.end_fold.call_count == 1
