#!/bin/bash
# check_scripts.sh -- every script gate in src_utils/, one line each, with its own timing.
#
#   usage: src_utils/check_scripts.sh            (or: make check-scripts)
#
# WHY THIS EXISTS, AND WHAT IT IS NOT. Several checkers in this directory were reachable only
# by their script path, so running one gate while fixing what it found meant knowing the
# src_utils/ layout. This gives each a name and runs them all in one pass.
#
# IT IS NOT A REPLACEMENT FOR `make check`. That remains THE gate: it runs the inline shell
# sweeps too (em-dashes, contractions, banned words, repo codenames, the undefined-cite check
# against the compiled log) and it is what a CI-style caller invokes. This script runs only the
# STANDALONE Python gates, which is why it needs no build and finishes in about a second.
#
# TWO DELIBERATE DIFFERENCES from `make check`, both of which make this useful in a fix loop:
#   1. It does NOT stop at the first failure. One run tells you everything that is broken.
#   2. It prints a status and a duration per gate, so a slow gate is visible rather than felt.
#
# The two KNOWN false positives that make `make check` exit 1 today (the technical term
# "Pareto" in published CBIC text, and apx_b_errata.tex's deliberate "this article") live in
# check.sh's inline sweeps, NOT here, so this script exiting 0 is the normal state.
# See science/AGENT_HANDOFF.md §3.5.
set -u
UTILS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # resolve before any cd (§2.5)
SRCROOT="$(cd "$UTILS/../src" && pwd)"
cd "$SRCROOT"

_now() { perl -MTime::HiRes -e 'printf "%.3f", Time::HiRes::time()'; }
T0="$(_now)"
FAIL=0; RAN=0; SKIPPED=0; FAILED=""

# run <name> <needs_build:yes|no> <command...>
run() {
  local name="$1"; shift
  local needs="$1"; shift
  if [ "$needs" = "yes" ] && [ ! -f build/main.log ]; then
    printf '  %-22s %-6s %8s  %s\n' "$name" "SKIP" "-" "needs build/main.log (run make defense)"
    SKIPPED=$((SKIPPED + 1)); return 0
  fi
  local t0 out rc dt
  t0="$(_now)"
  out="$("$@" 2>&1)"; rc=$?
  dt="$(perl -e "printf '%.3f', $(_now) - $t0")"
  RAN=$((RAN + 1))
  if [ $rc -eq 0 ]; then
    printf '  %-22s %-6s %7ss\n' "$name" "OK" "$dt"
  else
    printf '  %-22s %-6s %7ss  rc=%d\n' "$name" "FAIL" "$dt" "$rc"
    echo "$out" | tail -6 | sed 's/^/      /'
    FAIL=1; FAILED="$FAILED $name"
  fi
}

echo "== standalone script gates (make check is still THE gate; this is the fast subset) =="
printf '  %-22s %-6s %8s\n' "gate" "status" "seconds"
run sweep-guard        no  python3 "$UTILS/sweep_guard.py"
run trapped-fixtures   no  python3 "$UTILS/test_trapped_prose.py"
run trapped-prose      no  python3 "$UTILS/check_trapped_prose.py"
run torn-sentences     no  python3 "$UTILS/check_torn_sentences.py"
run doubled-macro      no  python3 "$UTILS/check_doubled_macro.py"
run tex-root           no  python3 "$UTILS/check_tex_root.py"
run negative-parallel  no  python3 "$UTILS/check_negative_parallelism.py"
run meta-claims        no  python3 "$UTILS/check_meta_claims.py"
run wordcount-claims   no  python3 "$UTILS/check_wordcount_claims.py"
run verify-list        no  python3 "$UTILS/check_verify_list.py"
run format-selftest    no  python3 "$UTILS/mkformat.py" --selftest
run equiv-selftest     no  python3 "$UTILS/verify_format.py" --selftest
run page-counts        yes python3 "$UTILS/sync_page_counts.py"

TOTAL="$(perl -e "printf '%.3f', $(_now) - $T0")"
echo "  ---"
echo "  $RAN gates ran, $SKIPPED skipped, total ${TOTAL}s"
[ -n "$FAILED" ] && echo "  FAILED:$FAILED"
exit $FAIL
