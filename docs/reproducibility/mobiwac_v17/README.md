# MobiWac v17 reproducibility bundle

This directory is the immutable source of record cited by Dissertation Appendix A.
It freezes the v17 statistical protocol, reported joint-best results, console output,
and every small input formerly held only in an active `docs/studies/` directory.

## Durable code

- Fold construction: `src/data/folds.py`
- Region-transition implementation: `src/data/region_transitions.py`
- Region-transition CLI: `pipelines/reproducibility/build_region_transitions.pipe.py`
- Joint-best scorer: `src/tracking/score_joint_best.py`
- Statistical and label-history analyses: `research/reproducibility/mobiwac_v17/`

The former files under `scripts/` and `docs/studies/` remain compatibility copies,
but this bundle and the paths above are the dissertation-facing sources of record.

## Reproduction

Run from the repository root:

```bash
.venv/bin/python research/reproducibility/mobiwac_v17/m1_stats_n20.py
.venv/bin/python research/reproducibility/mobiwac_v17/m2_prereg_perfold.py
```

Their standard output must match `outputs/m1_full_output.txt` and
`outputs/m2_prereg_output.txt` byte for byte. The scripts read the frozen inputs in
`data/` and canonical artifacts under `docs/results/`; they do not depend on
`docs/studies/`.

`MANIFEST.sha256` records the frozen files and durable code cited by the appendix.
When an intentional correction is needed, update the file, regenerate its output and
manifest in the same change, and record the reason here.

## Snapshot origin

The bundle was promoted on 2026-08-06 from the paths previously cited by Appendix A.
Machine-specific absolute rundir paths were normalized to repository-relative paths for
the public release; no metric or experimental result was changed.
The `m1_full_output.txt` snapshot was regenerated during promotion because its old
copy retained two superseded lines that described region superiority as
pre-registered. The executable already carried the corrected post-hoc label. No
numeric result changed. `m2_prereg_output.txt` already matched its executable exactly.
