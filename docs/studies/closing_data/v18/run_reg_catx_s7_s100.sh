#!/usr/bin/env bash
# v18 — the 4 dedicated-REGION cells that block texas and california from n=20.
#
#   {california, texas} x {seed 7, seed 100} x reg
#
# The rented lane bought the JOINT cells at seeds 7/100 for these two states but not the dedicated
# cat/reg arms; the author asked for the reg half now. Without these, texas/california stand at n=10
# while the other four states are at n=20 -- and they are the two states carrying the study's only
# robust effect (region +1.93 / +1.96, 25-30x the fold sd).
#
# ── SCORING PATH, and a CORRECTION ───────────────────────────────────────────────────────────────
# The banked siblings (ca/tx seeds 0,1) were scored on the LEGACY path: full [N,C] logit matrix on
# the CPU, hits from topk. Since 2026-08-10 the default is STREAMED + rank-derived hits + GPU.
# The first attempt here set MTL_STRICT=1 and california seed 7 ABORTED on the ambiguity certificate
# (1 row ambiguous at the 5/6 boundary; top10, the metric this cell reports, was 0/585092).
#
# ⚠ CORRECTION (2026-08-10, after an independent review refuted the first reading). I originally
# attributed a +0.004478 arizona difference to "compile-session nondeterminism" and generalised it
# into a ~0.05 pp reproducibility floor. BOTH halves of that were wrong:
#   * the +0.004478 is caused by commit aab23985 ("skip the inert α·log_T prior gather when frozen
#     α == 0"), which defaults ON via MTL_SKIP_INERT_PRIOR=1 and fires on exactly the
#     `freeze_alpha=True alpha_init=0.0` this driver passes. The A/B is in inert_prior_ab/:
#     skip OFF reproduces the 08-06 banked arizona cell BIT-FOR-BIT on all five folds.
#   * the ~0.05 pp "joint drift" compared a bs2048 sweep arm against a bs8192 wave cell — a batch
#     size effect, not drift.
# Measured reality: compiled cells on this box ARE bit-reproducible across sessions (8/8 exact
# same-recipe pairs). The real limiter is SEED variance (0.02-0.12 pp), not the compile session.
#
# CONSEQUENCE FOR THESE FOUR CELLS: MTL_SKIP_INERT_PRIOR is pinned to 0. The s0/s1 siblings these
# will be pooled with were banked before aab23985 existed, i.e. with the gather always performed.
# Leaving the new default ON would inject a known ~0.005 pp inhomogeneity into a single state's
# n=20 pool for no benefit. It is small against a +1.93/+1.96 effect, but it is free to remove.
#
# The STREAMED scoring path is kept (certificate warn-only): it is measured at 1e-6 against legacy,
# and the legacy path allocates ~20 GB of HOST RAM -- which is what SIGSEGV'd texas s1 reg at 06:31
# on this shared box. `ambiguous_rows` is recorded in every sidecar so the tie is disclosed.
#
# ── CONCURRENCY: deliberately 1-wide ─────────────────────────────────────────────────────────────
# Compiled fold fan-out is NOT bit-identical (~1e-4 drift from inductor autotuning under contention;
# only EAGER fan-out was verified byte-identical, and the banked cells are compiled). The banked
# ca/tx reg cells ran 1-wide and compiled, so these do too. ~6 h total instead of ~3 h; homogeneity
# with the cells these will be pooled with is worth more than the wall clock.
#
# Recipe is otherwise byte-identical to run_wave.sh cell_reg, including tau=0 (logit adjustment is
# OFF for region: it significantly HURTS Acc@10, AL -1.841 p=0.0002 / IST -2.749 p<0.0001).
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18
V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
SIDE=docs/results/closing_data/v18
LOGS=$BASE/logs/reg_catx
DRV=$BASE/logs/reg_catx_DRIVER.log
mkdir -p "$LOGS"
SHA=$(git rev-parse HEAD)
log(){ echo "[$(date '+%F %T')] REGCATX: $*" | tee -a "$DRV"; }

cell_reg(){
  local st=$1
  local sd=$2
  local side="$SIDE/${st}_s${sd}_reg.json"
  if [ -f "$side" ]; then log "  SKIP $st s$sd reg (sidecar exists)"; return 0; fi
  local lg="$LOGS/${st}_s${sd}_reg.log"
  local tag="v18_${st}_reg_s${sd}"
  local t0=$SECONDS
  log "  START $st s$sd reg  (streamed+rank+GPU, certificate warn-only — see MEASURED note above)"
  # MTL_STRICT is deliberately NOT set here. It aborts on an ambiguous row at ANY k, and california
  # seed 7 hit exactly that: 1 row ambiguous at the 5/6 boundary while top10 -- the metric this cell
  # reports -- was 0/585092. Aborting a 1.4 h cell over a tie in a k we never report is the wrong
  # trade, and the parity experiment (run_reg_scoring_parity.sh) measured what the tie is actually
  # worth. `ambiguous_rows` is captured into the sidecar below, so the tie is recorded, not hidden.
  env MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 MTL_SKIP_INERT_PRIOR=0 \
    python -u scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$ENG" --folds 5 --epochs 50 --seed "$sd" --target region \
    --max-lr 0.003 --compile --tf32 --tag "$tag" > "$lg" 2>&1 &
  local pid=$!
  wait $pid; local rc=$?
  local rj="docs/results/P1/region_head_${st}_region_5f_50ep_${tag}.json"
  if [ $rc -ne 0 ] || [ ! -f "$rj" ]; then
    log "  FAIL  $st s$sd reg rc=$rc (see $lg)"
    grep -iE "ambiguous|certificate|tie" "$lg" | tail -3 | sed 's/^/      /' | tee -a "$DRV"
    return 1
  fi
  local v; v=$(python -c "import json;d=json.load(open('$rj'));print(round(d['heads']['next_stan_flow']['aggregate']['top10_acc_mean']*100,4))" 2>/dev/null)
  [ -z "$v" ] && { log "  FAIL  $st s$sd reg: no score"; return 1; }
  python - "$SIDE/${st}_s${sd}_reg.json" "$st" "$sd" "$((SECONDS-t0))" "$rj" "$v" "$SHA" <<'PY'
import json, sys
out, st, sd, wall, rd, rv, sha = sys.argv[1:8]
_h = json.load(open(rd))["heads"]["next_stan_flow"]
AMB = [f.get("ambiguous_rows") for f in _h.get("per_fold", []) if isinstance(f, dict)]
json.dump({
    "state": st, "seed": int(sd), "family": "reg",
    "wall_seconds": int(wall), "rundir": rd, "cat": None, "reg": float(rv),
    "commit_sha": sha,
    "v18_config": {"engine": "check2hgi_v18", "forward_only": True, "in_channels": 15,
                   "node_layout": ["canonical_11", "continuous_time_4"], "repr_seed": 42},
    "protocol": {"precision": "fp32 (MTL_DISABLE_AMP=1, pinned per-command)", "compile": True,
                 "tf32": True, "folds": 5, "epochs": 50,
                 "reg_metric": "top10_acc_indist * (1 - ood_fraction) * 100 at indist-best epoch",
                 "scoring": "streamed + rank-derived hits on GPU (2026-08-10 default). Banked "
                            "siblings at seeds 0/1 used the legacy CPU full-logit topk path. "
                            "Measured equivalence (run_reg_scoring_parity.sh, AZ+IST seed 0): the "
                            "scoring path contributes 1e-6 Acc@10. MTL_SKIP_INERT_PRIOR=0 is pinned "
                            "so this cell matches its pre-aab23985 s0/s1 siblings exactly. "
                            "See ambiguous_rows for the tie certificate on this cell."},
    "ambiguous_rows": AMB,
    "recipe": "max_lr 3e-3 freeze_alpha logit_adjust_tau=0 (OFF: hurts Acc@10, AL -1.84 / IST -2.75); MTL_SKIP_INERT_PRIOR=0",
    "recipe_version": "v18-approved-2026-08-09 (FINAL_SETTINGS.md)",
}, open(out, "w"), indent=2)
PY
  # surface the certificate so a reader never has to trust the default silently
  python - "$rj" <<'PY' | tee -a "$DRV"
import json, sys
d = json.load(open(sys.argv[1]))
h = d["heads"]["next_stan_flow"]
amb = [f.get("ambiguous_rows") for f in h.get("per_fold", []) if isinstance(f, dict)]
so  = {f.get("scored_on") for f in h.get("per_fold", []) if isinstance(f, dict)} or {"?"}
print(f"      certificate: ambiguous_rows={amb or 'n/a'}  scored_on={so}")
PY
  log "  DONE  $st s$sd reg = $v  ($((SECONDS-t0))s)"
}

log "===== ca/tx x seeds {7,100} dedicated region — 4 cells, 1-wide, ~6 h — commit ${SHA:0:8} ====="
for sd in 7 100; do
  cell_reg california "$sd" || true
  cell_reg texas      "$sd" || true
done
log "===== COMPLETE ====="
python "$BASE/make_results.py" 2>&1 | tail -2 | tee -a "$DRV"
