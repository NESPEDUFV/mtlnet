# v18_2 scripts

| file | purpose |
|---|---|
| `run_lane.sh` | Runs ONE dataset x ONE seed x the selected families, fp32 pinned. Identical on A40 and rented hardware so the recipe cannot drift between lanes. Idempotent: a cell with an existing sidecar is skipped, so a killed lane resumes. |
| `preflight.py` | Authoritative per-cell input list. Run before every launch; never hand-write the list. |
| **`modal_lane.py`** | **Claude Code / plain-shell entry point to Modal.** Sandbox-based: live stdout, preflight, harvest onto the Volume, local archive with metadata, verified teardown, cost printed before submit. |
| `run_modal_cell.py` | Claude Science entry point — requires the `host.compute` API, which Claude Code does not have. |
| `watch_modal.py` | Second, independent view of a running lane, read from the committed heartbeat on the Volume. |
| `run_wave_a40.sh` | Seed-major driver for the small states on the local A40. |
| `monitor.sh` | Local-A40 monitor: duplicate drivers, write progress, GPU throttle, disk/RAM. |
| `replication_gate.md` | The cross-hardware check that must pass before rented numbers are pooled with local ones. ⚠ its comparand `data/alabama_s0_cat.json` was deleted 2026-08-10; the gate needs a fresh reference value. |

## Choosing cells

`run_lane.sh` honours `CELLS` (default `cat,reg,joint`); `modal_lane.py --cells cat,reg` passes it
through. Before 2026-08-10 the driver flag gated only the preflight while the script ran all
three families anyway — asking for two cells silently bought three, which on a joint cell is
hours of GPU nobody requested.

## Precision is fixed, not tunable

`run_lane.sh` pins `MTL_DISABLE_AMP=1` (fp32) and `MTL_STRICT=1` on every command, using
`env VAR=1 cmd` rather than `export` — a bare `export` inside a shell function leaks into
later cells in the same shell, which is exactly how precision silently varied in the v18
run (`PRECISION_CAVEAT.md`).

bf16/fp16 are **not** available as a speed option for california or texas: at 8462 and
6530 region classes they sit in the band where the trainer's own guard
(`_AUTO_FP32_REG_CLASS_THRESHOLD = 2000`) forces fp32, and where a collapse is silent
rather than loud.

## `MTL_STRICT=1` means different things on different cells

Do not read it as a blanket "abort on non-finite". `guard_finite_step` lives only in
`mtl_cv.py`, so the fail-loud non-finite abort covers the **joint** cell only. On cat and reg
the same variable hard-fails two guards that would otherwise warn — the torch-build check
(`train.py::_preflight_canon_guards`) and the stride-1 overlap provenance check
(`folds.py::_warn_if_ungated_overlap`). Fail-closed by choice, and stricter than
`v18/run_wave.sh`, but it is a **crash** surface, not a numerical one.

## Two invariants worth re-checking after any edit

1. **Flag equivalence with `v18/run_wave.sh`.** REG and JOINT are identical; CAT differs only by
   `--task-a-input-type checkin`, which is the argparse default and therefore inert. A flag diff
   is necessary and *not* sufficient — see `MODAL_MANUAL.md` §4 for the four things to diff.
2. **Rundirs are anchored to the launched PID**, never to newest-mtime. `MLHistory` names every
   rundir `<prefix>_<timestamp>_<pid>` (`tracking/experiment.py:268`), and all 22 rundir call
   sites in the v18 driver family resolve it that way. Under one-job-per-seed packing, several
   containers share one Volume and "newest" is a race that scores another seed's rundir.
