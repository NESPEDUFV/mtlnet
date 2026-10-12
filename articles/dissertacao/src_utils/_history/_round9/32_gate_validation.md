# 32_gate_validation.md — the seven `R9-` probes, validated by sabotage

Round 9, 2026-07-30, build commit `d4078c75`. A probe that has never fired carries no
information (GUARDRAILS §7, §4b V15). Each leg below breaks exactly one property in a **live** line,
runs the gate, and reads the exit code. The mutation script asserts the target string is present
before substituting, so a no-op substitution cannot be mistaken for a passing gate (V15b).

## The legs

| probe | property broken | rc | rows flagged |
|---|---|--:|--:|
| `R9-schema`  | `### AUT-01` renamed, i.e. the per-item schema no longer covers all 43 blocks | 1 | 1 |
| `R9-commit`  | the build-commit field (43 occurrences) renamed to "Measured at tree" | 1 | 1 |
| `R9-verbal`  | "transcribed by the author" changed to "written by Germano" | 1 | 1 |
| `R9-stale`   | the stale count changed from 9 to 10 (the figure I first got wrong) | 1 | 1 |
| `R9-blocked` | FAB-28's verdict changed from INADMISSIBLE to "fine to cite" | 1 | 1 |
| `R9-pend6`   | the §6 heading renumbered | 1 | 1 |
| `R9-pend28`  | 2.8 flipped back to "que eu NAO executei" | 1 | 1 |

Every leg turned the gate red, each flagging exactly its own row and nothing else, which is what makes
the seven independent rather than one probe with seven names. Restored afterwards and confirmed
byte-identical with `diff -q`; the clean run is rc=0 with 20 of 20 probes holding.

Command:

    cd articles/dissertacao/src_utils
    python3 check_audit_claims.py            # rc=0, 20 of 20
    # per leg: mutate one string, re-run, read rc, restore

## The two traps this validation had to avoid

**A sabotage that never reaches the instrument.** `live_text()` strips everything after an unescaped
`%`. On markdown that is a no-op, but I did not want to assume it: `self_test()` now asserts that
`### FAB-01` and `### GER-01` survive `live_text()` on the real tracker, so an R9 probe reading mangled
text fails loudly instead of reading like a probe that never fires.

**A probe resolved against the wrong root.** The trackers live in `src_utils/`, and every pre-existing
probe resolves against `src/`. Before this round a probe naming `CONSIDERATIONS.md` would have looked
for `src/CONSIDERATIONS.md`, missed, and printed `SKIP ... not found` — which returns rc=2, so it would
not have passed silently. `probe_root()` routes `.md` paths to `src_utils/`, and `self_test()` asserts
both directions of that routing.

## The scope change, stated in the same commit

The gate's docstring previously said it covered two things. It now covers three, and the third reads
files outside `src/`. Both facts are in the docstring, because a docstring claiming one scope over code
covering more is a defect this repository has already hit once.

## What these probes do NOT defend

They pin the **shape and the honesty** of the split: that all 43 blocks exist, that every one records
its build commit, that Germano's verbal comments are never attributed to him as written words, that the
stale count is the corrected one, that FAB-28 stays blocked, and that §6 exists while 2.8 no longer
asks for a decision. They do **not** verify any per-item verdict — a verdict is an argument, not a
string, and the author is the one who settles it. Nor do they cover the 21 "you apply" edits, because
**none of those edits has been made yet**: this round produced the split, not the fixes. When an edit
lands, its own probe lands with it (V15), and the item block already names the probe reserved for it.
