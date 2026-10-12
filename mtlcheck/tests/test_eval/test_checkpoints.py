"""Checkpoint retention — the artifact that converts a campaign into a script.

Class B of the recoverability taxonomy (CKA, calibration, re-scoring, the accumulation curve) is a
pure function of weights plus data, so retaining weights is what decides whether a future question
costs an afternoon or a training run. The project's own record is the argument: probes ran
`--no-checkpoints`, so an independent re-score of the champion was skipped for want of a `.pt`, and a
two-state cell was re-trained purely to recover weights it had already computed.
"""

from __future__ import annotations

import json

import pytest
import torch

from mtlcheck.config import load_recipe
from mtlcheck.train import checkpoints as ckpt
from mtlcheck.train import runner

from test_capture import _fold, _inputs, _spec   # same directory; pytest prepends it


def test_nothing_is_retained_by_default(tmp_path) -> None:
    """Screening is the common workload and cannot consume a checkpoint.

    §5 re-fits winners under sealed confirmation, and under sealing a screening cell never evaluates
    the outer fold at all — so a retained screening checkpoint is write-only output, at 13.7 MB a
    fold and hundreds of cells a week. The plan's own rule (no field without a named consumer)
    decides it: weights are the largest field there is.
    """
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128)
    assert resolved.train.retain_checkpoints == "none", "retention is OPT-IN"
    runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(), run_dir=tmp_path)
    assert not (tmp_path / "checkpoints").exists()


def test_selected_is_one_file_per_fold(tmp_path) -> None:
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=4,
                           batch_size=128, retain_checkpoints="selected")

    outcome = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(),
                                run_dir=tmp_path)
    directory = tmp_path / "checkpoints"
    files = sorted(p.name for p in directory.glob("*.pt"))
    assert files == ["fold0_selected.pt"]
    assert outcome.checkpoints["selected_epoch"] == outcome.selection["epoch"], (
        "the retained file must be the epoch the selector chose, not the last one")


def test_the_retained_weights_are_the_selected_ones_not_the_final_ones(tmp_path) -> None:
    """A reference to the live state dict would be a checkpoint of whatever the model ends up as.

    The training step mutates those tensors in place, so `snapshot` clones. If it did not, a
    'selected' checkpoint would silently be the last epoch's weights whenever selection was earlier.
    """
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=6,
                           batch_size=128, retain_checkpoints="selected")
    outcome = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(),
                                capture_predictions=True, run_dir=tmp_path)
    saved = torch.load(tmp_path / "checkpoints" / "fold0_selected.pt", weights_only=True)

    # Re-run the outer evaluation from the file and reproduce the captured rows exactly.
    assert outcome.rows is not None
    assert set(saved) and all(isinstance(v, torch.Tensor) for v in saved.values())
    assert all(v.device.type == "cpu" for v in saved.values()), "snapshots live on the host"


def test_every_retains_the_whole_trajectory_and_the_selection(tmp_path) -> None:
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128, retain_checkpoints="every")
    outcome = runner.train_joint_fold(resolved, _inputs(), _fold(sealed=True), _spec(),
                                      run_dir=tmp_path)
    files = sorted(p.name for p in (tmp_path / "checkpoints").glob("*.pt"))
    assert files == ["fold0_epoch0.pt", "fold0_epoch1.pt", "fold0_epoch2.pt", "fold0_epoch3.pt",
                     "fold0_selected.pt"]
    assert outcome.checkpoints["epoch0"] == "fold0_epoch0.pt"


def test_none_writes_nothing(tmp_path) -> None:
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128, retain_checkpoints="none")
    outcome = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(), run_dir=tmp_path)
    assert not (tmp_path / "checkpoints").exists()
    assert outcome.checkpoints == {}
    with pytest.raises(ValueError, match="retain_checkpoints"):
        load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, retain_checkpoints="log_spaced")


def test_an_unknown_policy_is_refused() -> None:
    with pytest.raises(ValueError, match="retain_checkpoints"):
        load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, retain_checkpoints="hourly")


def test_the_manifest_indexes_the_files_so_no_reader_has_to_glob(tmp_path) -> None:
    written = ckpt.write_manifest(
        tmp_path, [{"selected": "fold0_selected.pt", "selected_epoch": 12}],
        policy="selected", extra={"cell_id": "joint-alabama-p0s0"})
    payload = json.loads(written.read_text())
    assert payload["policy"] == "selected"
    assert payload["folds"][0]["selected_epoch"] == 12
    assert payload["cell_id"] == "joint-alabama-p0s0"
    assert ckpt.write_manifest(tmp_path, [{}], policy="none") is None


def test_a_compiled_run_retains_loadable_keys(monkeypatch, tmp_path) -> None:
    """The defect that would have wasted a 270-fit campaign.

    Both best-state sites inlined `model.state_dict()` AFTER `torch.compile`. `OptimizedModule`
    defines neither `state_dict` nor `load_state_dict`, so every key came out prefixed with
    `_orig_mod.` and the file would not load into a fresh model. All three v18 recipes pin
    compile=true, so every A40 cell was affected — and nothing in src/ loads a checkpoint, so the
    campaign would have completed and the failure landed when the §8a scorer opened the first file.
    CI could not see it: the shared fixture resolves to CPU, where compile is off.
    """
    import torch

    from mtlcheck.models.joint import JointModel

    real = JointModel(feature_size=64, n_categories=7, n_regions=12)
    compiled = torch.compile(real)

    prefixed = compiled.state_dict()
    assert any(k.startswith("_orig_mod.") for k in prefixed), (
        "if this fails the wrapper no longer prefixes and the guard below is moot")

    state = ckpt.snapshot(compiled)
    assert not any(k.startswith("_orig_mod.") for k in state)
    fresh = JointModel(feature_size=64, n_categories=7, n_regions=12)
    fresh.load_state_dict(state)                       # the assertion: it loads at all

    keep = ckpt.FoldCheckpoints(tmp_path, 0, "selected", epochs=3)
    keep.selected(state, 2, 0.5)
    reloaded = torch.load(tmp_path / "checkpoints" / "fold0_selected.pt", weights_only=True)
    assert set(reloaded) == set(fresh.state_dict())


def test_every_retains_one_file_per_epoch_because_a_max_cannot_be_sampled(tmp_path) -> None:
    """§8a's a1 is a MAX over eligible epochs, and a max is not a sample.

    On 753 real 50-epoch curves an 8-point log grid discards a maximum averaging 1.16 pp — several
    times the quantity §8a exists to measure — and pushes 26% of cells across the "errata is a
    footnote" threshold from the sampling alone. And it is TRANSIENT: §8a prices it as "transient
    checkpoint storage" and scopes its scorer per state, so the shape is retain -> score -> delete,
    one state at a time.
    """
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=4,
                           batch_size=128, retain_checkpoints="every")
    runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(), run_dir=tmp_path)
    epochs = sorted(int(p.stem.split("epoch")[1])
                    for p in (tmp_path / "checkpoints").glob("*_epoch*.pt"))
    assert epochs == [0, 1, 2, 3, 4], "every eligible epoch, plus initialisation"


def test_the_manifest_merges_across_a_fold_fanout(tmp_path) -> None:
    """--only-folds is a supported mode and the run directory is shared.

    A plain write left five checkpoints on disk and three in the index, with no entry naming a fold.
    """
    ckpt.write_manifest(tmp_path, [{"fold": 0, "selected": "fold0_selected.pt"},
                                   {"fold": 1, "selected": "fold1_selected.pt"}],
                        policy="selected")
    ckpt.write_manifest(tmp_path, [{"fold": 2, "selected": "fold2_selected.pt"}],
                        policy="selected")
    folds = json.loads((tmp_path / "checkpoints" / "manifest.json").read_text())["folds"]
    assert [f["fold"] for f in folds] == [0, 1, 2], "the second writer must not erase the first"


def test_a_retained_checkpoint_is_cross_checked_even_without_predictions(monkeypatch, tmp_path) -> None:
    """The guard used to run only under capture_predictions while the file was written regardless.

    A checkpoint labelled "selected" that is not the selected one is worse than no checkpoint,
    because it loads. Forcing the selector to disagree must refuse to retain, not retain quietly.
    """
    from mtlcheck.train import scoring

    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=4,
                           batch_size=128, retain_checkpoints="selected")

    real = scoring.single_task_best

    def shifted(series, metric, min_best_epoch=0):
        out = dict(real(series, metric, min_best_epoch))
        out["epoch"] = out["epoch"] + 1          # a selector that disagrees with the tracker
        return out

    monkeypatch.setattr(scoring, "single_task_best", shifted)
    with pytest.raises(RuntimeError, match="disagrees with the selector"):
        runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec(), run_dir=tmp_path)
