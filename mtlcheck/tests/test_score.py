"""Re-scoring a banked wave, on the CPU.

The reference's scorer was invoked in a way that swallowed failures, so a whole lane sat empty and
nobody noticed (R10). Scoring here is a separate re-runnable step over `result.json`, and these tests
cover the two things it must not get wrong: which spread it reports, and what it does with a matrix
that has holes.
"""

from __future__ import annotations

import json

import pytest

from mtlcheck.train import score


def _bank(root, family: str, state: str, seed: int, per_fold: list[float], *, wall: float = 100.0,
          eval_stream: str = "outer_fold"):
    directory = root / f"{family}-{state}-seed{seed}-{eval_stream}"
    directory.mkdir(parents=True, exist_ok=True)
    # The REAL schema: identity at the top level, wall-clock per fold, diagnostics inside a fold.
    # An earlier version of this fixture invented a flatter shape, so the tests passed against a
    # collector that read fields no result.json has and reported zeros.
    n = len(per_fold)
    (directory / "result.json").write_text(json.dumps({
        "config_fingerprint": f"fp-{family}-{seed}",
        "family": family, "state": state, "seed": seed,
        "config": {"train": {"family": family, "state": state, "seed": seed}},
        "aggregate": {"metric": "f1", "lane": "diag_best", "eval_stream": eval_stream,
                      "per_fold": [v / 100 for v in per_fold]},
        "folds": [{"fold": i, "seed": seed, "wall_seconds": wall / n, "eval_stream": eval_stream,
                   "diagnostics": {"train_seconds_total": wall * 0.9 / n,
                                   "val_seconds_total": wall * 0.08 / n,
                                   "peak_memory_gb": 3.0, "best_epoch": 12}}
                  for i in range(n)],
    }))
    return directory


def test_collect_skips_unreadable_results(tmp_path) -> None:
    _bank(tmp_path, "cat", "arizona", 0, [30.0, 31.0])
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "result.json").write_text("{ truncated")

    banked = score.collect(tmp_path)
    assert len(banked) == 1, "a truncated result must be skipped, not crash the scorer"


def test_the_reported_spread_is_over_seeds_not_pooled_folds(tmp_path) -> None:
    """Pooling folds answers 'how much do folds differ', which nobody is asking.

    The two seeds below have nearly identical means and wildly different folds. A pooled standard
    deviation would report a large spread for an arm that is in fact very stable across seeds.
    """
    _bank(tmp_path, "cat", "arizona", 0, [20.0, 40.0, 30.0])
    _bank(tmp_path, "cat", "arizona", 1, [29.0, 31.0, 30.0])

    summary = score.summarise(score.collect(tmp_path))["cat/arizona"]
    assert summary["n_seeds"] == 2
    assert summary["mean"] == pytest.approx(30.0)
    assert summary["std_over_seeds"] < 0.1, (
        f"the arm is stable across seeds; got {summary['std_over_seeds']:.3f}, which is the "
        "between-FOLD spread leaking into the report")


def test_compare_is_paired_over_shared_cells(tmp_path) -> None:
    """The joint arm is uniformly 0.5 below the dedicated one on every fold of every seed."""
    for seed in (0, 1):
        _bank(tmp_path, "cat", "arizona", seed, [30.0 + seed, 34.0 + seed, 28.0 + seed])
        _bank(tmp_path, "joint", "arizona", seed, [29.5 + seed, 33.5 + seed, 27.5 + seed])

    result = score.compare(score.collect(tmp_path), "cat", "joint", state="arizona")
    assert result.n_pairs == 6
    assert result.n_seeds == 2
    assert result.delta == pytest.approx(-0.5)
    assert result.delta_std == pytest.approx(0.0, abs=1e-9)


def test_performance_flags_time_the_phase_timers_do_not_see(tmp_path) -> None:
    """A gap between wall and the summed phases is where optimisation effort would be wasted."""
    _bank(tmp_path, "cat", "arizona", 0, [30.0], wall=200.0)
    perf = score.performance(score.collect(tmp_path))
    row = perf["cells"][0]
    assert row["unaccounted_share"] == pytest.approx(0.02, abs=1e-6)
    assert perf["total_wall_seconds"] == pytest.approx(200.0)


def test_a_joint_cell_becomes_two_arms(tmp_path) -> None:
    """A joint cell banks no single aggregate — it has two metrics — and scoring it as one crashed.

    Splitting it into joint:cat and joint:reg is what makes `cat` vs `joint:cat` expressible, which
    is the comparison the whole study exists to make.
    """
    directory = tmp_path / "joint-arizona-seed0"
    directory.mkdir(parents=True)
    (directory / "result.json").write_text(json.dumps({
        "config_fingerprint": "fp", "family": "joint", "state": "arizona", "seed": 0,
        "aggregate": {},                                   # joint banks none
        "folds": [{"fold": i, "wall_seconds": 10.0,
                   "selection": {"cat_diag_best": {"f1": 0.30 + i / 100, "epoch": 5},
                                 "reg_diag_best": {"top10_full": 0.70 + i / 100, "epoch": 6}}}
                  for i in range(3)],
    }))

    banked = score.collect(tmp_path)
    families = {c.family for c in banked}
    assert families == {"joint:cat", "joint:reg"}

    summary = score.summarise(banked)
    assert summary["joint:cat/arizona"]["mean"] == pytest.approx(31.0)
    assert summary["joint:reg/arizona"]["mean"] == pytest.approx(71.0)
    assert summary["joint:cat/arizona"]["metric"] == "f1"
    assert summary["joint:reg/arizona"]["metric"] == "top10_full"


def test_the_report_flags_a_schedule_that_peaks_early(tmp_path) -> None:
    """The anomaly that would have caught the Alabama finding without anyone noticing it.

    AL peaked at epoch 13 of 50 and its banked numbers were 0.35 pp worse than a 20-epoch
    schedule's. The evidence was in every artifact and nothing said it out loud.
    """
    from dataclasses import dataclass, field

    from mtlcheck.train import report

    @dataclass
    class _Fold:
        fold: int
        selection: dict
        wall_seconds: float = 10.0
        ambiguous_rows: dict = field(default_factory=dict)

    @dataclass
    class _Cfg:
        epochs: int = 50

    early = [_Fold(i, {"epoch": 13}) for i in range(5)]
    flagged = report._anomalies(early, _Cfg())
    assert any("first third" in a for a in flagged), flagged

    late = [_Fold(i, {"epoch": 38}) for i in range(5)]
    assert not any("first third" in a for a in report._anomalies(late, _Cfg()))


def test_a_sealed_arm_is_never_paired_against_a_legacy_one(tmp_path) -> None:
    """The comparison the scorer must refuse.

    Under sealing the reported number comes from the inner split; under the legacy rule it comes
    from the fold that also chose the epoch. The measured optimism of that rule is ~0.66 pp — larger
    than the 0.4 pp equivalence margin — so a delta across the two streams reports a change of
    PROTOCOL as a change of MODEL, in the favourable direction, with a tight interval.
    """
    _bank(tmp_path, "cat", "alabama", 0, [30.0, 31.0], eval_stream="outer_fold")
    _bank(tmp_path, "reg", "alabama", 0, [30.0, 31.0], eval_stream="inner_val")
    banked = score.collect(tmp_path)

    with pytest.raises(ValueError, match="different estimands"):
        score.compare(banked, "cat", "reg", state="alabama")


def test_two_arms_on_the_same_stream_still_compare(tmp_path) -> None:
    _bank(tmp_path, "cat", "alabama", 0, [30.0, 31.0], eval_stream="inner_val")
    _bank(tmp_path, "reg", "alabama", 0, [32.0, 33.0], eval_stream="inner_val")
    result = score.compare(score.collect(tmp_path), "cat", "reg", state="alabama")
    assert result is not None


def test_two_states_in_one_study_are_never_silently_collapsed(tmp_path) -> None:
    """The comparison that produced one state's answer and discarded the other.

    `stats.Cell` was keyed on (seed, fold), so two states' cells shared coordinates, the arm
    dictionaries collapsed, and whichever result.json sorted last won. No warning, a plausible
    delta, a plausible n. `mtlcheck score <study> --compare cat joint:cat` over a three-state study
    is exactly the command that triggers it.
    """
    for state, base in (("alabama", 30.0), ("istanbul", 60.0)):
        _bank(tmp_path, "cat", state, 0, [base, base])
        _bank(tmp_path, "reg", state, 0, [base + 1.0, base + 1.0])
    banked = score.collect(tmp_path)

    both = score.compare(banked, "cat", "reg")
    assert both.n_pairs == 4, "all four cells must pair, not two"
    assert both.delta == pytest.approx(1.0)

    one = score.compare(banked, "cat", "reg", state="alabama")
    assert one.n_pairs == 2


def test_a_short_fold_list_pairs_by_real_fold_id(tmp_path) -> None:
    """--only-folds banks a short list; positional pairing compares fold 3 against fold 0."""
    a = _bank(tmp_path, "cat", "alabama", 0, [10.0, 20.0, 30.0])
    b = _bank(tmp_path, "reg", "alabama", 0, [31.0])
    payload = json.loads((b / "result.json").read_text())
    payload["aggregate"]["fold_ids"] = [2]                 # only fold 2 ran
    payload["folds"] = [dict(payload["folds"][0], fold=2)]
    (b / "result.json").write_text(json.dumps(payload))
    payload = json.loads((a / "result.json").read_text())
    payload["aggregate"]["fold_ids"] = [0, 1, 2]
    (a / "result.json").write_text(json.dumps(payload))

    out = score.compare(score.collect(tmp_path), "cat", "reg", state="alabama")
    assert out.n_pairs == 1
    assert out.delta == pytest.approx(1.0), "fold 2 must pair with fold 2, not with fold 0"


def test_two_arms_reporting_different_estimators_are_not_paired(tmp_path) -> None:
    """`reg` vs `joint:reg` is the study's central comparison and its two sides disagreed.

    A dedicated region cell banks `top10_acc` — every held-out row against the full vocabulary. A
    joint cell's diag-best banks `top10_full` — the in-distribution rate discounted by the OOD share.
    Both are written "Acc@10" in prose. They differ by the OOD rows that happen to rank inside the
    top ten, and pairing them reads that difference as a model effect.
    """
    a = _bank(tmp_path, "reg", "alabama", 0, [70.0, 71.0])
    b = _bank(tmp_path, "cat", "alabama", 0, [72.0, 73.0])
    payload = json.loads((b / "result.json").read_text())
    payload["aggregate"]["metric"] = "top10_full"
    (b / "result.json").write_text(json.dumps(payload))

    with pytest.raises(ValueError, match="different estimators"):
        score.compare(score.collect(tmp_path), "reg", "cat", state="alabama")
