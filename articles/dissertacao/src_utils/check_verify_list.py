#!/usr/bin/env python3
"""check_verify_list.py -- run every command documented in VERIFY_LIST.md and PENDENCIAS.md,
and compare what it returns against what the document says it should return.

WHY THIS EXISTS. On 2026-07-28 three separate commands written into the author-facing verification
documents did not answer the question they were annotated with:

  * a count of \path{} entries annotated "# 13" returned 15, because it did not strip the appendix's
    own provenance comments, which mention \path{} while explaining the count;
  * a "four of six" sweep promised 3 prose hits and returned 4, one an indented comment;
  * a "three of our six" sweep promised ZERO prose hits and returned 5, every one an audit comment.

Each was individually plausible. What made them survive is that nothing ran them. A verification
document nobody executes is a claim, not a check -- the same failure this repository has now recorded
for its build reporter, four checker globs, and a page-count syncer.

WHAT IT CHECKS. For each fenced bash block carrying a machine-checkable EXPECT annotation (see below),
the block is run from its declared working directory and its output compared against the expectation.
Blocks without an EXPECT annotation are still RUN, and reported as executed-not-asserted, so the count
of what was actually verified is never overstated.

RECURSION. This gate is invoked from check.sh, and two documented blocks invoke check.sh (or
`make check`) themselves -- which is correct for the author, since checking that the gate suite passes
is one of the things the list tells him to do. Running them from inside the harness re-enters check.sh,
which re-enters the harness, and the run does not terminate. I built exactly that cycle on 2026-07-28
and it hung `make check` for ten minutes before I noticed.

So the harness SKIPS any block that invokes `check.sh` or `make check`, and reports them as skipped
with the reason rather than silently -- an unreported skip counted as a pass is the defect this file
was written to answer. Those two blocks are exercised every time check.sh itself runs, which is the
only place they can be exercised without recursion.

THE ANNOTATION. Add a comment line inside the bash block:

    # EXPECT: lines=3
    # EXPECT: contains=RC=0
    # EXPECT: equals=13

Supported: lines=N (exactly N non-empty output lines), contains=STR, equals=STR (whole stripped
output). Multiple EXPECT lines all have to hold. A block with no annotation is executed only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DISS = Path(__file__).resolve().parent.parent
ROOT = DISS.parent.parent
DOCS = [DISS / "src_utils" / "_history" / "_round6" / "VERIFY_LIST.md",
        DISS / "src_utils" / "PENDENCIAS.md"]

EXPECT = re.compile(r'#\s*EXPECT:\s*(lines|contains|equals)=(.*)$')


def blocks(doc: Path):
    text = doc.read_text(encoding="utf-8")
    for m in re.finditer(r'```bash\n(.*?)```', text, re.S):
        code = "\n".join(re.sub(r'^> ?', '', l) for l in m.group(1).split("\n"))
        yield code


def expectations(code: str) -> list[tuple[str, str]]:
    return [(m.group(1), m.group(2).strip()) for m in
            (EXPECT.search(l) for l in code.split("\n")) if m]


def cwd_for(code: str) -> Path:
    """A block that cd's into articles/dissertacao needs the repo root; everything else runs
    from articles/dissertacao, which is what the document's own header declares."""
    first = next((l for l in code.split("\n") if l.strip()), "")
    if first.strip().startswith("cd articles/"):
        return ROOT
    return DISS


# Verbs that CHANGE something. A documented block carrying any of these is refused, not run.
# Deliberately broad and anchored at a word boundary: `git reset --hard`, `git push`, `git commit`,
# `git add`, `git mv`, `rm -rf`, `mv`, `> file` truncation, and pip/conda installs. False positives
# here cost a printed REFUSED line; a false negative costs the author's branch.
#
# ROUND 8, 2026-07-30: this pattern was itself a name-list and SIX shapes walked past it. Measured
# with the case table at the foot of this file (`--selftest`, 36 rows -- an earlier draft of this
# comment said 29 and cited a table that did not yet exist; it does now, and the count is read from
# SELFTEST_CASES rather than retyped), the pre-round version let all of these through as
# kind="run", i.e. EXECUTED on every `make check`:
#     git -C <path> push origin main          option before the subcommand; `git\s+push` cannot match
#     git --git-dir=... commit -am wip        same
#     printf 'x' > notes.txt                  the redirect test was anchored at `> /`, so any
#     echo appended >> PENDENCIAS.md          RELATIVE target, and every append, was invisible
#     tee src_utils/out.txt                   writes without a redirect operator at all
#     curl -X POST ... -d @payload.json       leaves the machine; `ssh` was listed, `curl` was not
#     sed -i '' 's/a/b/' PENDENCIAS.md        in-place edit
#     python3 src_utils/sync_page_counts.py --write     this tree's own repair flags
# The rule generalized: match the TOOL plus "any options" rather than the exact word pair, treat
# every redirect that is not /dev/null as a write, and name the write-capable tools as a class.
MUTATING = re.compile(
    # git with any number of options between the binary and a mutating subcommand
    r"\bgit\b(?:\s+-{1,2}[^\s]+(?:\s+[^\s-][^\s]*)?)*\s+"
    r"(?:reset|push|commit|add|mv|rm|checkout|switch|restore|branch|clean|tag|stash|apply|"
    r"cherry-pick|rebase|merge|fetch|pull|remote|submodule|worktree|gc|prune|filter-branch)\b"
    r"|\brm\s+-|\brmdir\b|\bmv\s+\S+\s+\S+|\bcp\s+\S+\s+\S+|\bln\s+-s"
    r"|\b(?:tee|truncate|shred|install|chmod|chown|touch|mkdir|unlink)\b"
    r"|\bsed\s+(?:-\S+\s+)*-\S*i|\bperl\s+(?:-\S+\s+)*-\S*i"
    r"|\bdd\s+if=|\bpip3?\s+install\b|\bconda\s+(?:install|remove|create)\b"
    r"|\bnpm\s+(?:install|i)\b|\bbrew\s+(?:install|upgrade)\b"
    # anything that leaves this machine
    r"|\b(?:curl|wget|ssh|scp|rsync|sftp)\b"
    # this tree's own repair flags: --write / --fix / --in-place / -i
    r"|--(?:write|fix|in-place|apply)\b"
    # every redirection whose target is not /dev/null, absolute or relative, truncating or appending
    r"|>>?\s*(?!/dev/null|&\s*[12])\S"
    # a heredoc that writes a file
    r"|<<-?\s*['\"]?\w+['\"]?[^\n]*\n(?:.|\n)*?\n\s*\w+\s*$"
)

# WHICH COMMANDS COUNT AS "a build" -- and this list was INCOMPLETE, which is the whole defect.
# The build guard below has existed since round 7 and its comment correctly says running a build
# here "took make check from 4 seconds to 297". But it tested for `make defense`, `make final`,
# `make ppgc` and `pdflatex` by substring, and two blocks added to PENDENCIAS.md afterwards open
# with `make fast3 && bash src_utils/build.sh src both` -- neither of which matched. So the guard
# reported nothing, the harness built all three targets and then rebuilt two more, on EVERY
# `make check`.
#
# Measured 2026-07-30: 264.1 s of a 265.5 s suite, 99.5 percent, against 0.927 s for the same gate
# in round 7. The lesson is not "add fast3": it is that a substring list of the CURRENT target names
# is guaranteed to go stale the next time a target is added, which is exactly what happened. Hence
# one pattern, covering the Makefile's build targets as a class plus the two scripts and pdflatex.
#
# The cost was not only the clock. A gate that rebuilds the PDFs is a gate that COLLIDES with any
# other build, which is the source of every intermittent rc=1 chased this round: the suite
# rewriting build/*.pdf underneath its own page-count and numbering checks.
#
# Refused rather than skipped-in-silence, and reported with this reason, because the block itself
# is CORRECT for the author -- he should run that recipe. It just must not run here.
#
# ROUND 8: the target ALTERNATION was widened last round but the `make` invocation itself was still
# assumed to be bare, so `make -C src defense` and `make --directory=src defense` fell through to
# kind="run" and were executed in full. Same defect one level up: a guard that matches the argument
# and not the way the tool is called. `make` now tolerates any options before the target, and the
# target list is a negative test (anything that is NOT one of the handful of known cheap targets
# counts as a build) so the next target added is guarded on the day it is added rather than the day
# someone measures the suite.
CHEAP_MAKE_TARGETS = ("check", "check-scripts", "clean", "help", "wordcount", "status")
BUILDING = re.compile(
    r"\bmake\b(?:\s+-{1,2}[^\s]+(?:\s+[^\s-][^\s]*)?)*\s+(?!(?:" + "|".join(CHEAP_MAKE_TARGETS) + r")\b)[a-z][\w.-]*"
    r"|\bbuild\.sh\b|\bpdflatex\b|\blatexmk\b|\bxelatex\b|\blualatex\b|\bbibtex\b|\bbiber\b"
    r"|\bmkformat\.py\b(?![^\n]*--(?:status|selftest))"
)

# RECURSION. Also a name-list until round 8: it was the two substrings "check.sh" and "make check",
# so `make -C src check`, `make --directory=src check` and `cd src && make -f Makefile check` all
# classified as "run" and would have re-entered the suite that called them. Verified NOT by running
# one (that is the hang this guard exists to prevent) but with `make -C src -n check`, whose dry run
# prints `../src_utils/check.sh`: the command does reach this gate's own caller.
RECURSING = re.compile(
    r"\bcheck\.sh\b|\bcheck_scripts\.sh\b"
    r"|\bmake\b(?:\s+-{1,2}[^\s]+(?:\s+[^\s-][^\s]*)?)*\s+check(?:-scripts)?\b"
)


def classify(code: str) -> tuple[str, list[str]]:
    """Decide what kind of block this is. Returns (kind, body lines).

    Factored out of main() when this gate was parallelized, so the two passes (plan, then
    report) cannot disagree about a block's kind -- one classifier, called twice.

    ORDER MATTERS AND IS LOAD-BEARING. The recursion test runs FIRST: blocks 3 and 17 of
    VERIFY_LIST are single-line `cd ... && make check` commands, so the bare-cd test below
    would swallow them as "notes" and skip them silently, which is how the first version of
    this guard reported 0 skipped while still recursing. An unreported skip counted as a pass
    is the failure mode this whole file exists to answer.
    """
    body = [l for l in code.split("\n") if l.strip() and not l.strip().startswith("#")]
    # MUTATING COMMANDS ARE REFUSED, AND THIS TEST RUNS BEFORE EVERY OTHER ONE.
    # Found 2026-07-29: PENDENCIAS §2.1 documents the recovery procedure for a destructive local
    # commit, so its bash block legitimately contains `git reset --hard 3c57197c`, `git commit` and
    # `git push origin mobiwac`. This harness EXECUTES documented blocks. It was running that one on
    # every `make check`. It did no damage only because the target worktree's .git/ happens to be
    # unwritable in this sandbox -- an accident of the environment, not a safeguard. On the author's
    # machine `make check` would have reset a branch and pushed it.
    # A verification harness must never mutate. Blocks carrying a mutating verb are reported as
    # REFUSED, loudly, and never run: a documented recovery procedure is for a human to execute
    # deliberately, and a gate that runs it is a footgun wearing a checker's clothes.
    if MUTATING.search(code):
        return "refused", body
    if RECURSING.search(code):
        return "recursion", body            # see RECURSION in the module docstring
    if BUILDING.search(code):
        return "build", body
    # THE BARE WORKING-DIRECTORY NOTE. The `&&` test alone was too narrow: `cd src; grep -c foo x`
    # is one line with no `&&`, so it classified as a note and was skipped SILENTLY -- the exact
    # unreported-skip-counted-as-a-pass failure named in the docstring. Any separator disqualifies.
    if (len(body) == 1 and body[0].strip().startswith("cd ")
            and not re.search(r"&&|\|\||;|\||`|\$\(", body[0])):
        return "note", body
    return "run", body


def probe_cmd(body: list[str]) -> str:
    first = body[0] if body else ""
    return re.sub(r'&&\s*\(?cd src.*$', '', first).strip().rstrip("&").strip()


def main() -> int:
    # PARALLEL EXECUTION, and why it is worth it HERE and nowhere else in the suite.
    # Round 7 timed every gate: all of them are under 0.3 s except this one, which was 0.93 s
    # of the 2.0 s suite. Profiled, that is 15 documented shell blocks whose subprocesses sum
    # to 0.85 s, with the slowest single block at 0.30 s -- so the work is I/O-bound subprocess
    # waiting, not Python, and a thread pool is the right shape. The gates that are already
    # 0.03 s are NOT parallelized: forking to save 30 ms costs more than it saves, and the
    # per-gate timing table in check.sh is there so the next gate that grows past a second is
    # visible rather than suspected.
    #
    # THREADS, NOT PROCESSES: every one of these blocks is a subprocess.run() that releases the
    # GIL while it waits. And the RESULTS ARE PRINTED IN DOCUMENT ORDER, not completion order,
    # so this gate's output stays byte-comparable with its serial form -- a gate whose output
    # reorders run to run cannot be diffed, and diffing its output is how the author checks it.
    from concurrent.futures import ThreadPoolExecutor

    plan: list[tuple[Path, str, str, list[str]]] = []
    for doc in DOCS:
        if not doc.exists():
            continue
        for code in blocks(doc):
            kind, body = classify(code)
            plan.append((doc, code, kind, body))

    def execute(item):
        doc, code, kind, body = item
        if kind == "run":
            return subprocess.run(["bash", "-c", code], capture_output=True, cwd=cwd_for(code))
        if kind == "build":
            probe = probe_cmd(body)
            if not probe:
                return None
            return subprocess.run(["bash", "-c", probe + " && echo REACHED"],
                                  capture_output=True, cwd=cwd_for(code))
        return None

    n_conc = sum(1 for _, _, k, _ in plan if k in ("run", "build"))
    with ThreadPoolExecutor(max_workers=min(8, max(1, n_conc))) as pool:
        results = list(pool.map(execute, plan))

    ran = asserted = failed = 0
    skipped: list[tuple[str, str]] = []
    refused: list[tuple[str, str]] = []
    build_blocks: list[tuple[str, str, bool]] = []
    for (doc, code, kind, body), proc in zip(plan, results):
        if kind == "refused":
            # Reported by name, never counted as verified. See MUTATING above for why.
            refused.append((doc.name, body[0][:58] if body else "(empty)"))
            continue
        if kind == "recursion":
            skipped.append((doc.name, body[0][:58] if body else "(empty)"))
            continue
        if kind == "build":
            # A three-target build takes minutes and check.sh is a lint gate that people run
            # constantly. Running it here took make check from 4 seconds to 297. The build is
            # already verified by build.sh, which is the tool for it; what matters HERE is that
            # the documented command is well formed and its paths resolve, so that is what is
            # checked. Reported, not silent.
            first = body[0] if body else ""
            ok = True if proc is None else (b"REACHED" in proc.stdout)
            build_blocks.append((doc.name, first[:58], ok))
            continue
        if kind == "note":
            continue
        exps = expectations(code)
        out = proc.stdout.decode("utf-8", "replace").strip()
        lines = [l for l in out.split("\n") if l.strip()]
        ran += 1
        head = body[0][:58] if body else "(empty)"
        if not exps:
            print(f"  ran      {doc.name}: {head}  (no EXPECT annotation)")
            continue
        asserted += 1
        problems = []
        if proc.returncode != 0:
            problems.append(f"exit {proc.returncode}")
        # `etype`, not `kind`: `kind` is the BLOCK's classification in this scope, and reusing
        # the name here shadowed it. Harmless today only because the outer loop reassigns it,
        # which is exactly the kind of accident that stops being harmless after one edit.
        for etype, want in exps:
            if etype == "lines" and len(lines) != int(want):
                problems.append(f"lines={len(lines)}, expected {want}")
            elif etype == "contains" and want not in out:
                problems.append(f"output does not contain {want!r}")
            elif etype == "equals" and out != want:
                problems.append(f"output {out[:40]!r} != {want!r}")
        if problems:
            failed += 1
            print(f"  FAIL     {doc.name}: {head}")
            for p in problems:
                print(f"           {p}")
        else:
            print(f"  verified {doc.name}: {head}")
    print(f"\n{ran} documented command(s) executed; {asserted} carried a machine-checkable "
          f"expectation; {failed} failed.")
    for name, head in refused:
        print(f"  REFUSED  {name}: {head}")
    if refused:
        print(f"    {len(refused)} block(s) carry a MUTATING command (git reset/push/commit, rm, "
              f"install) and were NOT executed. That is deliberate: this harness verifies, it does "
              f"not mutate. A documented recovery procedure is for a human to run on purpose. "
              f"They are not counted as verified.")
    for name, head in skipped:
        print(f"{len(skipped)} skipped to avoid recursion (they invoke this gate's own caller): "
              f"{name}: {head}" if skipped.index((name, head)) == 0 else
              f"    also: {name}: {head}")
    if skipped:
        print("    Those run every time check.sh runs, which is the only place they can run "
              "without re-entering this harness.")
    for name, head, ok in build_blocks:
        print(f"  {'cd-ok   ' if ok else 'CD-FAIL '} {name}: {head}  "
              f"(build block: cwd checked, build NOT run here -- use build.sh)")
    if any(not ok for _, _, ok in build_blocks):
        print("    A build block whose own cd does not resolve cannot work for the author.")
        return 1
    if ran - asserted:
        print(f"{ran - asserted} were executed but NOT asserted against their prose expectation "
              f"(prose too discursive to encode, or the check is a human judgment). "
              f"Do not describe those as verified.")
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# THE FIXTURE TABLE THIS FILE'S OWN COMMENT PROMISED.
#
# ROUND 8, 2026-07-30. The comment at the top of MUTATING said the six escaped shapes were
# "measured with a 29-case fixture table (`--selftest` below)". There was no `--selftest` below,
# and no table. `main()` reads no argv at all, so `check_verify_list.py --selftest` parsed nothing,
# ran the ordinary gate, printed the ordinary report and exited 0 -- indistinguishable from a
# passing self-test to anyone who checked the exit code. That is this round's own failure mode
# reproduced inside the tool built to catch it: a durable record asserting a measurement that was
# never taken. selftest_all.py independently lists check_verify_list among the four checkers with
# NOTHING, which is the reading to trust.
#
# Every MUTATING row below is one of the six shapes that walked past the pre-round pattern, or a
# guard against a regression that would let it walk again. Every BUILDING and RECURSING row is a
# call-shape (`-C`, `--directory=`, `-f`) that classified as "run" before round 8. The NEGATIVE
# rows matter as much: a guard that refuses everything is not a guard, and three of them
# (`> /dev/null`, `2>&1`, `git log`/`git show`/`git diff` reads) are shapes this file's own
# documented blocks depend on -- if a widening breaks those, the harness stops verifying anything.
SELFTEST_CASES = [
    # (expected kind, source, why this row exists)
    ("refused", "git -C /tmp/x push origin main", "option before subcommand"),
    ("refused", "git --git-dir=/tmp/x/.git commit -am wip", "long option before subcommand"),
    ("refused", "git push", "the bare shape that always matched"),
    ("refused", "git add -A && git commit -m x", "chained mutation"),
    ("refused", "printf 'x' > notes.txt", "RELATIVE redirect target"),
    ("refused", "echo appended >> PENDENCIAS.md", "append, not truncate"),
    ("refused", "tee src_utils/out.txt", "writes with no redirect operator"),
    ("refused", "curl -X POST https://example.invalid -d @payload.json", "leaves the machine"),
    ("refused", "sed -i '' 's/a/b/' PENDENCIAS.md", "in-place edit, BSD two-arg form"),
    ("refused", "sed --in-place 's/a/b/' PENDENCIAS.md", "in-place edit, long option"),
    ("refused", "python3 src_utils/sync_page_counts.py --write", "this tree's own repair flag"),
    ("refused", "rm -rf build/", "delete"),
    ("refused", "ssh nespedgpu 'df -h /home'", "remote, even when read-only there"),
    ("refused", "pip install pypdfium2", "installs"),
    ("refused", "mv a.tex b.tex", "rename"),
    ("refused", "python3 -c \"a = 1 > 0\"", "KNOWN FALSE POSITIVE, deliberate: a comparison is "
                                            "indistinguishable from a redirect without parsing "
                                            "shell, and the guard must not learn to tell them "
                                            "apart. Item 20 of VERIFY_LIST documents the "
                                            "measurement it displaced into prose."),
    ("build", "make defense", "bare build target"),
    ("build", "make -C src defense", "-C before the target"),
    ("build", "make --directory=src ppgc", "--directory= before the target"),
    ("build", "make fast3 && bash src_utils/build.sh src both", "the two that cost 264 s"),
    ("build", "bash src_utils/build.sh src both", "the script alone"),
    ("build", "pdflatex main.tex", "the engine directly"),
    ("build", "make academico", "a target added after the guard was written"),
    ("recursion", "cd src && bash ../src_utils/check.sh", "the caller, by path"),
    ("recursion", "make check", "the caller, by target"),
    ("recursion", "make -C src check", "-C before check"),
    ("recursion", "make --directory=src check", "--directory= before check"),
    ("recursion", "cd src && make -f Makefile check", "-f before check"),
    # NEGATIVE ROWS -- these must NOT be refused, or the harness verifies nothing.
    ("run", "grep -c 'Overfull' src/build/main.log > /dev/null", "/dev/null is not a write"),
    ("run", "python3 src_utils/check_audit_claims.py 2>&1", "2>&1 is not a write"),
    ("run", "git log --oneline -5", "git READS must still run"),
    ("run", "git show HEAD:src/content.tex", "git show is a read"),
    ("run", "git diff --stat", "git diff is a read"),
    ("run", "sed -n '42p' model.py", "sed WITHOUT -i is a read"),
    ("run", "make status", "a cheap non-build target"),
    ("run", "python3 -c \"print(open('GLOSSARY.md').read().count('fclass'))\"", "the ordinary case"),
]


def selftest() -> int:
    """Run the fixture table through classify() and report per-row. rc=0 iff every row matches."""
    width = max(len(k) for k, _, _ in SELFTEST_CASES)
    bad = 0
    for expected, src, why in SELFTEST_CASES:
        got = classify(src)[0]
        ok = got == expected
        bad += not ok
        if not ok:
            print(f"  FAIL  expected {expected:<{width}}  got {got:<{width}}  {src}\n"
                  f"        (row exists because: {why})")
    counts = {}
    for expected, _, _ in SELFTEST_CASES:
        counts[expected] = counts.get(expected, 0) + 1
    breakdown = " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"check_verify_list selftest: {len(SELFTEST_CASES) - bad}/{len(SELFTEST_CASES)} rows "
          f"classify as documented ({breakdown})")
    if bad:
        print(f"  {bad} row(s) FAILED. A guard that does not classify its own documented "
              f"escape shapes is not protecting anything.")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    unknown = [a for a in sys.argv[1:] if a.startswith("-")]
    if unknown:
        # Round 8: an unrecognized flag used to be swallowed in silence, which is how
        # `--selftest` "passed" for a whole round while doing nothing.
        print(f"unknown option(s): {' '.join(unknown)}  (this gate takes --selftest or no argument)")
        sys.exit(2)
    sys.exit(main())
