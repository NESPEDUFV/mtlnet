"""The statistics layer and the result schema.

The statistics layer earns its own tests because a naive version moves verdicts without touching a
line of training code — a failure the reference already made once, differencing unpaired means and
printing the Delta beside an `n` computed over another set of cells.
"""

from __future__ import annotations

import json

import pytest

from mtlcheck.train import stats


def _cells(values: dict[tuple[int, int], float]) -> list[stats.Cell]:
    return [stats.Cell(seed=s, fold=f, value=v) for (s, f), v in values.items()]


def test_delta_is_paired_over_common_cells_only() -> None:
    """The arms differ in coverage; the Delta must use the intersection, not two full means."""
    arm_a = _cells({(0, 0): 10.0, (0, 1): 20.0, (1, 0): 30.0})
    arm_b = _cells({(0, 0): 11.0, (0, 1): 22.0})          # seed 1 never ran

    out = stats.compare(arm_a, arm_b, label="b - a")

    assert out.n_pairs == 2
    assert out.mean_a == pytest.approx(15.0), "the unpaired mean of arm A would be 20.0"
    assert out.delta == pytest.approx(1.5)
    assert out.dropped == [("", 1, 0)]
    assert any("present in one arm only" in w for w in out.warnings)


def test_unpaired_means_would_have_lied() -> None:
    """The failure mode, made explicit: differencing full means gives a different answer."""
    arm_a = _cells({(0, 0): 10.0, (1, 0): 30.0})
    arm_b = _cells({(0, 0): 12.0})

    paired = stats.compare(arm_a, arm_b).delta
    naive = (12.0) - (10.0 + 30.0) / 2
    assert paired == pytest.approx(2.0)
    assert naive == pytest.approx(-8.0)
    assert paired != naive


def test_pooled_pairs_are_flagged_as_non_independent() -> None:
    """Five folds of one seed are not five replicates, and the report must say so."""
    arm_a = _cells({(0, f): 1.0 for f in range(5)})
    arm_b = _cells({(0, f): 2.0 for f in range(5)})
    out = stats.compare(arm_a, arm_b)

    assert out.n_pairs == 5 and out.n_seeds == 1
    assert any("not independent replicates" in w for w in out.warnings)
    assert "NOT independent" in out.describe()


def test_summary_reports_both_units() -> None:
    cells = _cells({(0, 0): 1.0, (0, 1): 3.0, (1, 0): 10.0, (1, 1): 10.0})
    out = stats.summarise(cells, label="reg")

    assert out["n_cells"] == 4 and out["n_seeds"] == 2
    assert out["mean"] == pytest.approx(6.0)
    assert out["seed_means"] == {0: pytest.approx(2.0), 1: pytest.approx(10.0)}
    assert out["mean_of_seed_means"] == pytest.approx(6.0)
    # O fator agrupado, não a palavra deprecada: `summarise` só vê `cell.seed`, e com a partição
    # congelada esses refits são réplicas (NOMENCLATURE §2, §7).
    assert out["independent_unit"] == "model_seed"


def test_no_common_cells_is_an_error() -> None:
    with pytest.raises(ValueError, match="share no"):
        stats.compare(_cells({(0, 0): 1.0}), _cells({(1, 1): 2.0}))


def test_geometric_joint_is_scale_coherent() -> None:
    """Neither head can dominate by scale — the property the arithmetic selector lacked."""
    assert stats.geometric_joint(0.30, 0.70) == pytest.approx((0.30 * 0.70) ** 0.5)
    assert stats.geometric_joint(0.0, 0.9) == 0.0
    assert stats.geometric_joint(-1.0, 0.9) == 0.0, "negative inputs clamp rather than produce NaN"


# ---------------------------------------------------------------- the result schema

def test_result_round_trips_and_carries_its_config(tmp_path) -> None:
    from mtlcheck.config import load_recipe
    from mtlcheck.train import result as result_mod

    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0)

    class _Fold:
        fold, seed, wall_seconds = 0, 0, 1.5
        selection = {"epoch": 3, "metric": "f1", "value": 0.31, "lane": "diag_best"}
        ambiguous_rows = {"top3": 0}
        train_loss = [1.0, 0.9]
        diagnostics = {"train_seconds_total": 1.2, "peak_memory_gb": 0.5}
        parameter_counts = {"head": 10, "total": 10}
        architecture = "Stub()"
        # The stub grows when the record grows. Making the SERIALISER permissive instead is how a
        # field gets computed and silently dropped — which already happened here once, to the
        # diagnostics block, for a week.
        eval_stream = "inner_val"
        checkpoints = {"selected": "fold0_selected.pt", "selected_epoch": 3}
        flops = {"flops_per_sample": 1234.0, "measured_at_batch": 2048}

        class _S:
            values = {"f1": [0.2, 0.31]}
        val = {"cat": _S()}

    cell = result_mod.build(resolved, [_Fold()],
                            {"lane": "diag_best", "metric": "f1", "mean": 0.31, "std": 0.0,
                             "per_fold": [0.31], "n_folds": 1, "best_epochs": [3]})
    path = cell.write(tmp_path)
    payload = json.loads(path.read_text())

    # Diagnostics must survive serialisation: they were computed and dropped here for a week, so a
    # profiling wave banked no profile at all.
    assert payload["folds"][0]["diagnostics"]["peak_memory_gb"] == 0.5
    assert payload["folds"][0]["eval_stream"] == "inner_val"
    assert payload["folds"][0]["flops"]["flops_per_sample"] == 1234.0

    # The provenance is the object the run used, not a hand-written claim about it.
    assert payload["config"]["train"]["precision"] == "fp32"
    assert payload["config"]["train"]["cat_head"]["params"]["num_layers"] == 4
    assert payload["config_fingerprint"] == resolved.fingerprint()
    assert payload["environment"]["torch"]
    assert payload["aggregate"]["lane"] == "diag_best"

    again = result_mod.CellResult.read(path)
    # BOTH seeds in the name: the protocol's §10.4 decomposition varies them independently,
    # and a directory that spells only one makes two of its four cells collide.
    assert again.cell_id == "cat-alabama-p0s0"


def test_result_refuses_a_foreign_schema(tmp_path) -> None:
    from mtlcheck.train import result as result_mod

    path = tmp_path / "result.json"
    path.write_text(json.dumps({"schema_version": 99}))
    with pytest.raises(ValueError, match="schema version"):
        result_mod.CellResult.read(path)


# ---------------------------------------------------------------- the acceptance yardstick

def test_the_paired_band_is_not_the_between_fold_spread() -> None:
    """The tolerance for "are these two arms the same" must come from the PAIRED deltas.

    A round-2 audit found the acceptance criterion using the between-fold standard deviation
    (~1.2 pp at Alabama) as the noise scale for comparing five-fold MEANS. Folds differ from one
    another for reasons that hit both arms identically — different users, different class mixes —
    and pairing cancels exactly that. Judged against the unpaired spread, a real regression walks
    straight through.
    """
    import statistics

    from mtlcheck.train.stats import Cell, compare

    fold_effect = {0: -2.0, 1: -0.5, 2: 0.0, 3: 0.9, 4: 1.7}
    seeds = (0, 1, 7, 100)
    arm_a = [Cell(seed=s, fold=f, value=30.0 + fold_effect[f]) for s in seeds for f in range(5)]
    arm_b = [Cell(seed=s, fold=f, value=30.0 + fold_effect[f] + 0.30)
             for s in seeds for f in range(5)]

    result = compare(arm_a, arm_b, label="regressao")
    between_fold = statistics.stdev([c.value for c in arm_a])

    assert result.delta == pytest.approx(0.30)
    assert between_fold > 1.0, "the fixture needs a large fold effect for this to mean anything"
    assert result.delta_std == pytest.approx(0.0, abs=1e-9)
    assert result.separated(), (
        f"a uniform +0.30 shift must be detectable; against the between-fold spread "
        f"({between_fold:.2f}) it would not be")


def test_the_band_uses_seeds_as_replicates_not_folds() -> None:
    """Folds within a seed share ~80% of their training data, so they are not replicates.

    Counting 20 (seed, fold) pairs as 20 independent samples shrinks the band by sqrt(20/4) and
    claims precision the design never bought.
    """
    import math
    import statistics

    from mtlcheck.train.stats import Cell, compare

    offsets = [0.4, -0.1, 0.2, -0.3]                  # one true offset per seed
    seeds = (0, 1, 7, 100)
    arm_a = [Cell(seed=s, fold=f, value=30.0) for s in seeds for f in range(5)]
    arm_b = [Cell(seed=s, fold=f, value=30.0 + offsets[i])
             for i, s in enumerate(seeds) for f in range(5)]

    result = compare(arm_a, arm_b)
    assert len(result.seed_deltas) == 4, "one delta per seed, not per fold"
    assert result.stderr == pytest.approx(statistics.stdev(offsets) / math.sqrt(4))

    naive = statistics.stdev([b.value - a.value for a, b in zip(arm_a, arm_b)]) / math.sqrt(20)
    assert result.stderr > naive, (
        "treating folds as replicates would give a tighter band than the design earns")


def test_the_band_uses_student_t_not_the_normal_approximation() -> None:
    """At the R this project runs, 2.0 is not the multiplier — and the difference flips verdicts.

    t(0.975) is 3.18 at R=4 and 12.71 at R=2, against the 2.0 originally used. That made every band
    ~37% too narrow at R=4 and turned one banked gate result ("Arizona joint region, 30 epochs,
    +0.148 +/- 0.141, separated") into a non-result at +/- 0.224.
    """
    import statistics

    from mtlcheck.train.stats import Cell, compare

    offsets = {0: 0.10, 1: 0.20, 7: 0.30, 100: 0.40}
    arm_a = [Cell(seed=s, fold=f, value=70.0) for s in offsets for f in range(5)]
    arm_b = [Cell(seed=s, fold=f, value=70.0 + d) for s, d in offsets.items() for f in range(5)]

    result = compare(arm_a, arm_b)
    expected_se = statistics.stdev(list(offsets.values())) / 2.0     # sqrt(4)
    assert result.stderr == pytest.approx(expected_se)
    assert result.band == pytest.approx(3.182 * expected_se, rel=1e-3), "R=4 must use t=3.182"
    assert result.band > 2.0 * expected_se, "the t band must be WIDER than the normal one"


def test_two_repetitions_get_a_very_wide_band() -> None:
    """R=2 has one degree of freedom and t=12.7. A design that small barely constrains anything."""
    from mtlcheck.train.stats import Cell, compare

    arm_a = [Cell(seed=s, fold=f, value=70.0) for s in (0, 7) for f in range(5)]
    arm_b = [Cell(seed=s, fold=f, value=70.0 + (0.10 if s == 0 else 0.14)) for s in (0, 7)
             for f in range(5)]

    result = compare(arm_a, arm_b)
    assert result.delta == pytest.approx(0.12)
    assert not result.separated(), (
        "two repetitions with a 0.04 pp spread cannot separate a 0.12 pp effect; claiming otherwise "
        "is the small-R trap this multiplier exists to prevent")


def test_the_environment_fingerprints_the_code_it_ran() -> None:
    """`git_commit` is null wherever runs actually happen — the A40 holds an rsync'd `src/`.

    So two arms run either side of a code change record the same provenance, which is exactly what
    happened to the probe-cost study: arms C and D differ in the probe's implementation and their
    configs differ only by a flag. A source digest is the version control this deployment has.
    """
    from mtlcheck.train import result as result_mod

    env = result_mod.environment()
    assert len(env["code_fingerprint"]) == 16
    assert env["code_fingerprint"] == result_mod.environment()["code_fingerprint"], "not stable"
