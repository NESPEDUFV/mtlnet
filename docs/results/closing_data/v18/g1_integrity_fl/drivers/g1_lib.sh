# shared helpers for resumable G1 drivers (sourced). Requires: C, G set; cwd = clone.
done_ok(){ [ -f "$C/g1_logs/$1/RUN.txt" ] && grep -q "^rc=0" "$C/g1_logs/$1/RUN.txt" && grep -q "guard OK" "$C/g1_logs/$1/RUN.txt" && ! [ -e "$C/g1_logs/$1/ABORTED" ]; }
# step <tag> <partial_results_dir_or_-> <cmd...> : skip if done; else move aside any aborted attempt (logs + partial results), run, fail-stop
step(){ local tag=$1 res=$2; shift 2
  if done_ok "$tag"; then echo "SKIP (done) $tag"; return 0; fi
  local ts; ts=$(date +%Y%m%d_%H%M%S)
  [ -d "$C/g1_logs/$tag" ] && mv "$C/g1_logs/$tag" "$C/g1_logs/${tag}_aborted_$ts" && echo "moved aside aborted attempt: ${tag}_aborted_$ts"
  [ "$res" != "-" ] && [ -e "$res" ] && mv "$res" "${res}_aborted_$ts" && echo "moved aside partial results: ${res}_aborted_$ts"
  G1_HEAVY="${G1_HEAVY:-0}" "$G" "$tag" "$@"
  done_ok "$tag" || { echo "STEP FAIL $tag"; exit 1; }; }
