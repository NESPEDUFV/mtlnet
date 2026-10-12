#!/usr/bin/env bash
# Best-effort PLUMBING git syncer for TX results. In this degraded env, porcelain `git status`/
# `git commit` hang on the working-tree scan (a git proc stuck in D-state I/O), but plumbing
# (write-tree/commit-tree/update-ref) + push work fine — they never scan the working tree.
# Every ~3min: stage result files (git add of specific paths only stats those), and if the index
# differs from HEAD, build a commit via plumbing and push. Timeout-bounded so it can never hang.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
REF=refs/heads/study/board-h100
FILES=(
  docs/studies/closing_data/TX_CELL.md
  docs/studies/closing_data/EP100_ABLATION_AND_TX_RAM.md
  docs/results/closing_data/h100/texas_s0_mtl
  docs/results/closing_data/h100/texas_s0_stl_cat_ceiling.json
  scripts/closing_data/tx_resume_nogit.sh
  scripts/closing_data/tx_cat_ceiling_deferred.sh
  scripts/closing_data/git_sync_loop.sh
  .gitignore
)
for i in $(seq 1 40); do
  timeout 30 git add "${FILES[@]}" 2>/dev/null || true
  if timeout 30 git diff --cached --quiet HEAD 2>/dev/null; then
    : # nothing new staged
  else
    tree=$(timeout 30 git write-tree 2>/dev/null || true)
    if [ -n "$tree" ]; then
      commit=$(printf 'board-h100: TX resume/ceiling results — autonomous plumbing sync (%s)\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_017bpM3kYznPgop7ySjMPkGF' "$i" | timeout 30 git commit-tree "$tree" -p HEAD 2>/dev/null || true)
      if [ -n "$commit" ]; then
        timeout 15 git update-ref "$REF" "$commit" 2>/dev/null && echo "[gsync $i] committed $commit ($(date -u +%H:%M:%S)Z)"
      fi
    fi
  fi
  if timeout 80 git push origin "$BRANCH" >/tmp/gsync_push.txt 2>&1; then
    grep -q 'Everything up-to-date' /tmp/gsync_push.txt || echo "[gsync $i] PUSHED ($(date -u +%H:%M:%S)Z)"
  fi
  sleep 200
done
echo "[gsync] exiting after ~2h ($(date -u +%H:%M:%S)Z)"
