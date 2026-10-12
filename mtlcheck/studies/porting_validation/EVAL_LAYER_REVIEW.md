# Review da camada de avaliação — 2026-08-18

> 45 agentes, 30 achados sobreviveram a refutação independente, 10 caíram. **Veredito: NÃO seguro
> para rodar confirmatório ainda.** A wave `sealed_bridge` foi parada na célula 6 de 36 por causa
> disto — só células `cat` tinham rodado, todas seladas e válidas, e nenhuma joint. Nada inválido foi
> bancado.
>
> **Já corrigido depois do review** (commit seguinte): o veredito de direção errada
> (`superior = low > 0 or high < 0`, que chamava de SUPERIOR um intervalo inteiramente abaixo de
> zero) e o no-op silencioso na captura do joint (agora recusa em vez de completar sem linhas).
>
> **Ainda aberto: os itens 1, 2 e 5–8 do §2 abaixo.** O item 1 é o que bloqueia a wave.

---

# Verdict: mtlcheck evaluation layer

## 1. Is it safe to run a confirmatory experiment on?

**No — not tonight.** **A sealed confirmatory wave launched now will complete "successfully" with the headline arm missing: `cli.py:257` silently drops `capture_predictions` for the joint family, `train_joint_fold` has no capture path and (under sealing) never evaluates the outer fold at all, so joint cells produce no rows, no outer number, and no saved weights — the joint-vs-STL Tier A comparison the protocol exists for is unproducible, and the only remedy is retraining every joint cell.** Second invalidator: the §10 repetition/replicate confound is reproduced inside the new schema — `splits.build(seed=train_cfg.seed)` plus `split_seed=model_seed=cfg.seed` in the sidecar means every `--seed` is a new partition, so the pre-registered frozen-partition R=2 replicate design cannot be executed by this CLI, and running seeds {0,7} anyway yields repetitions mislabeled as replicates. Third: the comparison layer's verdict logic prints "SUPERIOR (interval above 0)" for a significantly *inferior* result and cannot express the pre-registered four-way NI-gatekept verdict. Stage 1's dedicated-arm sealing itself is sound (the ~0.66 pp optimism is genuinely removed for STL cells) — but the wave is not safe until the three items above are fixed.

## 2. Must fix before the numbers are used (ranked)

1. **Joint capture + outer evaluation** (`cli.py:257`, `runner.py::train_joint_fold`). Add `capture_predictions` to `train_joint_fold`: track best_state at the geom_simple/min_best_epoch-gated epoch on the *inner* series, reload, run one outer pass per task, emit rows for both tasks with the same `selected_epoch`; drop the `if joint` special case. Until implemented, make `_train_cell` **raise** when `save_predictions` is requested on a joint recipe — never silently no-op.
2. **Split the seed knob** (`cli.py:242,316-317`, `config.py`). Add `--split-seed` (default 0, feeds `splits.build` only) and `--model-seed` (feeds `fold_seed`/`seed_everything` only); refuse to write a sidecar where both came from one bare `seed`. Without this, cross-seed Tier A is structurally blocked by `assert_comparable` and §10.3/§10.4 are unrunnable.
3. **Four-way verdict** (`compare.py:222-249`). Replace `superior=bool(low>0 or high<0)` with an enum {superior, non_inferior, inferior, inconclusive}: NI first (lower bound > −δ), superiority only where NI passes, inferior when upper < −δ; fix `describe()`; add a test with an all-negative interval. The pre-registered *primary* hypothesis (NI) currently has no implementation anywhere.
4. **Make `assert_comparable` raise on unsealed cells** (`predictions.py:200-214`), default `confirmatory=True` with explicit opt-out. A WARNING line is the only thing between a mixed bridge/sealed directory and a verdict flipped by the measured 0.66 pp > 0.4 pp margin.
5. **Region selection-lane mismatch** (`runner.py:204-226` vs `scoring.py:147-179`). Tracker follows gated `top10_acc_indist`; the cross-checked selector returns ungated argmax of raw `top10_acc`. Freeze ONE (metric, min_best_epoch) pair — raw `top10_acc`, matching the top10_raw estimand, is the natural choice — pass the gate into `single_task_best`, keep the cross-check. As-is it burns fully-trained folds stochastically, and any surviving fold's checkpoint rule agrees with the banked contract only by coincidence.
6. **Thread an interval level through `tier_a`** (`compare.py:157,201-206`). The registered TOST (90% CI) and NI bound (5th percentile) cannot be produced from a `TierA` result — 95% is hard-coded. Conservative, but it silently deviates from the frozen pre-registration and flips equivalent→inconclusive exactly in the measured Alabama half-width regime (§6's power=0.94 no longer describes the implemented test).
7. **The <15-contributing-users-per-class hard-fail** (`compare.py::tier_a`, cat branch). Mandated by §3, absent; emptied-class replicates bias the bootstrap toward |Δ|=0 — the direction of the paper's own equivalence claims. Count users with (tp+fp+fn)>0 per class, raise below 15, report the min.
8. **Label the evaluation stream in banked aggregates** (`runner.py::evaluate_folds`, `scoring.py`, `score.py`). Sealed cells bank inner-val numbers under the same `diag_best`/`dedicated_banked` labels as legacy outer numbers; `score.collect` will pair estimands ~0.66 pp apart with no guard. Stamp `inner_diag_best`/sealed into aggregate + index and make Tier-B pairing refuse mismatched streams.

## 3. Should fix soon (real, not invalidating)

- **Tests that cannot fail**: both `tier_a` fixtures are weight-invariant (delete the bootstrap, suite stays green), BCa has zero coverage, `predictions.py` — "the first item, nothing may start before it" — has no tests at all (no round-trip, no hash-mismatch rejection), and the "rows reproduce the training-time metric" test compares a function to itself while its docstring narrates an A40 verification the suite doesn't perform. Add: heterogeneous-user bootstrap fixture with width assertions, BCa-vs-percentile direction check, parquet round-trip, one cross-implementation test (StreamingMetrics vs estimands on identical logits). Do this before the freeze — it's the project's documented no-op failure class, unguarded.
- **Unstudentized permutation** (`compare.py:160-167`): protocol says Chung-Romano studentized; consequence is modest in this paired sign-flip design, but the published p is not the registered p. Studentize or amend the protocol *before* freezing.
- **`num_classes=None` inference + divisor discrepancy** (`estimands.py:64`; vs `train/metrics.py`): require num_classes (persist it in the sidecar), fix the false "matches sklearn's default" docstring, freeze the denominator convention in §1.
- **Provenance gaps**: inner_split_seed + realised inner-partition hash not in the sidecar; head vocabulary size not persisted (§1's identical-vocabulary assertion impossible); outer-pass tie/ambiguity certificate computed then dropped at `runner.py:232`.
- **`selection_stream` fail-closed claim**: the docstring promises a caller that forgets *fails*; the only caller quietly falls back to the outer stream. Add an explicit `allow_legacy_selection` and raise when sealing was requested but no stream exists.
- **multiplicity.py**: Romano-Wolf and the Bonferroni partial-conjunction variant are named by the docs and absent; needed only when a sweep reaches a confirmatory family — add or delete from the docs.
- **`mean_of_folds` bias test** asserts only inequality; pin the sign and a magnitude floor with a fixture that actually empties a class from a fold.

## 4. Statistical correctness verdict

The inference core is right where it exists. The multinomial-weight paired user-cluster bootstrap is exactly equivalent to resampling users with replacement for both metrics (both are ratios of user-additive sufficient statistics — the ratio-estimator trap is avoided); `_bca_interval` matches Efron 1987 (z0, delete-one-cluster jackknife acceleration, endpoint transform); the permutation's per-user bundle exchange is the correct paired randomisation with the correct (count+1)/(perm+1) p-value; Holm, BH, and the Benjamini-Heller Simes conjunction are all correctly implemented.

Miscalibrated or deviating: (a) the verdict layer — the mislabeled SUPERIOR and the missing NI/gatekeeping are the only places a *wrong-direction conclusion* can currently be printed; (b) 95%-for-90% interval substitution — conservative (a level-0.025 TOST), never anti-conservative, but a silent pre-registration deviation that costs power exactly in the 0.25-0.36 pp half-width regime; (c) the unstudentized permutation — small level drift at most in this paired design, and superiority is double-gated by the CI, but the p is not the protocol's p; (d) the missing rare-class guard — bounded (≈e^−k per replicate), paired-attenuated, but its bias direction favors equivalence and nothing reports when it fires; (e) num_classes inference — latent denominator drift, essentially unreachable at C=7 state-scale but unpinned.

## 5. What is fine — stop re-checking it

- **The dedicated-arm seal**: `build_inner` is genuinely user-disjoint, outer folds byte-identical to the legacy split; sealed `train_fold` selects on the inner stream and evaluates the outer fold once; `train_labels`, class stats, and logit-adjust priors are fit on the actual 70% training block. The 31.9452→31.2841 measurement is real and correctly interpreted.
- **The joint epoch loop's sealing** (post-`joint_selection_streams` fix): joint cells select on the inner split like STL — the leakage version of that finding is refuted and regression-tested. The joint problem is *absence* (no capture/outer eval), not bias.
- **Row alignment**: validation batches never shuffle, streams follow `fold.val` order, `_fold_predictions` asserts length — no mis-attribution path found.
- **The seed *columns* as records**: they truthfully record what the run did (per NOMENCLATURE §6 rule 3); the defect is the single knob upstream, not lying metadata.
- **`predictions.write` ordering and the BCa degenerate fallback** — both examined and harmless; readers fail closed on the sidecar and re-validate hashes.
- **`report.md` outer-number suppression** works in the sealed configuration; the residual is one cosmetic keying (`seal_outer` from `capture_predictions` instead of `fold.sealed`).
- **best_state memory** (~17 MB CPU clone, freed) — a non-issue.
- **The permutation no-op regression test** has real teeth for the permutation path.

One sentence for the morning: fix items 1-3 (joint capture, seed split, verdict enum) before any wave, items 4-8 before any number is quoted, and harden the tests before the freeze — everything else in the layer is doing what the protocol says.
