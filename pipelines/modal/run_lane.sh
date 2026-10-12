#!/usr/bin/env bash
# v18_2 lane runner -- ONE dataset, ONE seed, all three families, fp32.
#
# Runs identically on the A40 and on a Modal H100 container. The point of a single
# script is that the recipe cannot drift between lanes: every hyperparameter below is
# read from the same table the v18 driver used, and precision is pinned, not inherited.
#
#   usage: run_lane.sh <state> <seed> <engine> <v14_dir> <outdir>
#
# PRECISION IS NOT A TUNABLE HERE. CA (8501 region classes) and TX (6553) sit in the
# C~6.5-8.5k band where bf16 backward grad-NaNs and fp16 logits overflow; the resulting
# collapse is SILENT because the per-task best-epoch selector reports the pre-collapse
# peak (archive/lessons/CA_MTL_DIVERGENCE.md). fp32 everywhere.
#
# MTL_STRICT=1 does NOT mean the same thing on all three cells, so do not read it as a
# blanket "abort on non-finite". `guard_finite_step` lives only in mtl_cv.py, so the
# fail-loud non-finite abort applies to the JOINT cell only. On the cat and reg cells the
# same variable instead hard-fails two guards that would otherwise only warn: the torch-build
# check (train.py `_preflight_canon_guards`, fires for every task) and the stride-1 overlap
# provenance check (folds.py `_warn_if_ungated_overlap`). That is a deliberate fail-closed
# choice -- it is stricter than v18/run_wave.sh, which sets MTL_STRICT only on joint -- but it
# is a CRASH surface, not a numerical one. See MODAL_MANUAL.md section 4.
set -uo pipefail

ST=${1:?state}; SEED=${2:?seed}; ENG=${3:-check2hgi_v18}
V14=${4:-check2hgi_design_k_resln_mae_l0_1}; OUT=${5:-docs/results/closing_data/v18_2}
REPO=${REPO:-$(pwd)}

# PY resolution. The A40 box runs from a venv; a Modal container has none -- the staged
# /data/repo on the volume contains only docs/ research/ src/ scripts/ pipelines/, with no
# .venv anywhere. The old unconditional default ($REPO/.venv/bin/python) therefore pointed at
# a nonexistent path on every rented cell, and only worked because the submit wrapper happened
# to pass PY=/usr/local/bin/python. Resolve it here instead, and fail loudly if nothing works,
# so the script is correct on both lanes without the caller having to know.
if [ -z "${PY:-}" ]; then
  if [ -x "$REPO/.venv/bin/python" ]; then PY="$REPO/.venv/bin/python"
  else PY=$(command -v python3 2>/dev/null || command -v python 2>/dev/null); fi
fi
[ -n "${PY:-}" ] && [ -x "$PY" ] || {
  echo "FATAL: no usable python interpreter (PY='${PY:-}'; no $REPO/.venv/bin/python, none on PATH)" >&2
  exit 127; }

# Global exports the version of record sets at file scope (run_wave.sh lines 25-26). These are
# NOT per-cell knobs, so exporting them here does not repeat the precision leak PRECISION_CAVEAT
# warns about (that was MTL_DISABLE_AMP leaking out of a function into later cells).
# expandable_segments cuts allocator fragmentation on the long joint cells; without it a run that
# fits can still OOM late in training.
export PYTHONPATH=${PYTHONPATH:-src}
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
mkdir -p "$OUT" "$OUT/logs"

# ---- recipe tables: identical to v18/run_wave.sh, reproduced so a lane is self-contained
cat_bs(){   echo 8192; }
cat_lr(){   case $1 in alabama) echo 0.0025 ;; arizona|istanbul) echo 0.0005 ;; *) echo 0.005 ;; esac; }
mtl_catlr(){ case $1 in alabama|arizona|istanbul) echo 0.001 ;; *) echo 0.002 ;; esac; }
LA_TAU=0.5     # dedicated-cat + MTL-cat head only; NEVER the region head (region is Acc@10,
               # whose Bayes-optimal predictor is the UNADJUSTED posterior)

# `date -Is` is GNU-only; BSD/macOS date rejects it and the timestamp comes out empty. Both
# real lanes are Linux, but an agent dry-running this on a mac should still get usable logs.
now(){ date -Is 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S%z"; }
log(){ echo "[$(now)] $*" | tee -a "$OUT/logs/${ST}_s${SEED}.log"; }

# ---- self-reporting: the run logs its own health into the HARVESTED directory --------------
# One JSON line per sample in out/heartbeat.jsonl. It comes back with the results, so a
# post-mortem needs no live container and no second CPU instance.
HB_PID=""
heartbeat(){                    # heartbeat [interval_s]
  local iv="${1:-60}" hb="$HARVEST_OUT/heartbeat.jsonl"
  mkdir -p "$HARVEST_OUT"
  ( local t0=$SECONDS
    while :; do
      local g="" ; command -v nvidia-smi >/dev/null 2>&1 && \
        g=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,clocks_throttle_reasons.active \
            --format=csv,noheader,nounits | head -1 | tr -d ' ')
      local ncell rd folds
      ncell=$(ls -d /proc/[0-9]* 2>/dev/null | while read -r d; do
                tr '\0' ' ' < "$d/cmdline" 2>/dev/null | grep -qE 'train\.py|p1_region_head' && echo x; done | wc -l)
      # ANCHOR TO THIS LANE, not to the newest rundir on disk. `ls -dt | head -1` picks whatever
      # is newest by mtime, and once a state has a banked cell on the Volume that is the PREVIOUS
      # seed's completed rundir -- so the heartbeat reported `folds_done=5` six minutes into a
      # fresh california s100 while it was still on fold 1 of s7's leftovers. It is the same
      # mtime-vs-identity bug already fixed in rundir_for(), and it makes folds_done useless for
      # an ETA exactly when several seeds of one state exist. Filter by the lane's start marker.
      rd=$(find results/$ENG/$ST -maxdepth 1 -newer "$LANE_MARK" \
             \( -name 'next_*' -o -name 'mtlnet_*' \) -type d 2>/dev/null \
           | xargs -r ls -dt 2>/dev/null | head -1)
      folds=$(ls "$rd"/metrics/*standard_scores.json 2>/dev/null | wc -l)
      local line
      line=$(printf '{"t":%s,"iso":"%s","gpu":"%s","cells_running":%s,"folds_done":%s,"rundir":"%s","out_kb":%s}' \
        "$((SECONDS-t0))" "$(now)" "$g" "${ncell:-0}" "${folds:-0}" "${rd:-}" \
        "$(du -sk "$HARVEST_OUT" 2>/dev/null | cut -f1)")
      echo "$line" >> "$hb"
      # LIVE copy on the Volume + commit, so an outside reader can watch progress mid-run.
      # Without the commit the file exists only inside the container and nobody can see it.
      if [ -n "${LIVE_DIR:-}" ]; then
        mkdir -p "$LIVE_DIR"
        echo "$line" >> "$LIVE_DIR/heartbeat.jsonl"
        cp "$OUT/logs/${ST}_s${SEED}.log" "$LIVE_DIR/lane.log" 2>/dev/null
        for f in "$OUT"/logs/${ST}_s${SEED}_*.out; do
          [ -f "$f" ] && tail -c 20000 "$f" > "$LIVE_DIR/$(basename "$f")" 2>/dev/null
        done
        python -c "import modal,os;modal.Volume.from_name(os.environ['LIVE_VOLUME']).commit()" \
          >/dev/null 2>&1 || true
      fi
      sleep "$iv"
    done ) >/dev/null 2>&1 &
  HB_PID=$!
}
heartbeat_stop(){ [ -n "${HB_PID:-}" ] && kill "$HB_PID" 2>/dev/null; HB_PID=""; return 0; }

# Every cell's stdout log is a deliverable too: a failed cell is diagnosable ONLY from its log,
# and reading it later needs a whole extra job. Copy the tail into out/ on failure.
# HEAD + TAIL, never tail alone. Everything diagnostic is at the HEAD -- "TF32 enabled",
# "torch.compile enabled", the resolved config echo, the first per-fold "[log_T-inert skip]" --
# and a tqdm-heavy joint log blows past any tail window. Measured: the alabama s100 joint log hit
# the 400 KB cap and the harvested copy began mid-progress-bar with every startup line already
# gone. On a CA/TX joint that is hours of progress bars burying the only lines worth reading.
log_excerpt(){                  # log_excerpt <src> <dst>
  local src="$1" dst="$2" n
  [ -f "$src" ] || return 0
  n=$(wc -c < "$src" 2>/dev/null || echo 0)
  if [ "${n:-0}" -le 400000 ]; then cp "$src" "$dst" 2>/dev/null; return 0; fi
  { head -c 150000 "$src"
    printf '\n\n...[log_excerpt: %s bytes elided; kept head 150000 + tail 250000]...\n\n' \
           "$((n - 400000))"
    tail -c 250000 "$src"
  } > "$dst" 2>/dev/null
  return 0
}

save_log(){                     # save_log <family> <logfile>
  local fam="$1" lg="$2"
  mkdir -p "$HARVEST_OUT/logs"
  log_excerpt "$lg" "$HARVEST_OUT/logs/${ST}_s${SEED}_${fam}.log"
  return 0
}

# ---- precision + strictness, pinned per command (never `export`: a bare export leaks into
#      later cells in the same shell, which silently varied precision in the v18 run --
#      see PRECISION_CAVEAT.md)
# Base: precision + strictness. MTL_CHUNK_VAL_METRIC is NOT here any more -- it is a per-cell
# decision, because it means different things per runner and was actively harmful on one of them.
ENVCOMMON="MTL_DISABLE_AMP=1 MTL_STRICT=1"

# ---- MTL_CHUNK_VAL_METRIC, per cell -------------------------------------------------------
# The flag FORCES p1/MTL to accumulate the full val logit on CPU and score it there. It exists as
# an OOM guard: the GPU `torch.cat` of an [N_val x C] logit is ~20 GB at texas overlap scale and
# worse at california. But `_should_chunk_val_metric` ALREADY auto-enables above
# P1_S2_AUTO_BUDGET_GB (default 4 GB), so forcing it adds nothing for a large state and, for a
# SMALL one, pushes a tiny tensor onto the CPU for no reason:
#
#     arizona   N_val=40179  C=1547  -> 0.25 GB  auto-guard would NOT fire
#     florida   N_val=254883 C=4703  -> 4.79 GB  auto-guard fires anyway
#     texas     N_val=766083 C=6553  -> 20.1 GB  auto-guard fires anyway
#
# Measured cost of forcing it: arizona reg took 343 s on a rented H100 against 185 s alone on the
# A40 -- the only family that was SLOWER on faster silicon, because the CPU phase had 8 container
# cores against the A40 box's 32.
#
# EQUIVALENCE IS VERIFIED, NOT ASSUMED. The rank is `1 + #{logits strictly greater}` (an exact
# integer count, device-independent by construction), and the repo's own CPU-vs-CUDA test was
# `skipif(not cuda)` and had therefore never executed. Run on a real T4 on 2026-08-10 over six
# shapes including the arizona and florida val folds and two heavy-exact-tie cases: **worst
# deviation 2.98e-08 across top5/top10/mrr/ndcg/accuracy/f1**, against a reporting precision of
# 1e-4 -- 3350x below the bar. GPU scoring was 3.8-7.6x faster on those shapes.
#
#   reg   -> flag DROPPED; the auto-guard still protects TX/CA. Set P1_FORCE_CPU_VAL=1 to restore.
#   joint -> flag KEPT, exactly as v18/run_wave.sh sets it (mtl_eval.py has its own S2 path; that
#            is a separate question and is deliberately not bundled into this change).
#   cat   -> flag never applied: next_cv.py does not read it, so it was a no-op. Dropped as noise.
# REVERTED 2026-08-10 after measuring on the target card. Keep forcing the CPU path.
#
# The justification for dropping it was that CPU and CUDA scoring are equivalent "by
# construction" because the rank is an exact integer count. That argument is WRONG for the
# metric this cell actually reports: `top10_acc` comes from `_top_k_accuracy`
# (src/tracking/metrics.py:102-110), which uses `logits.topk(k).indices` — and the tie-break AT
# THE K-BOUNDARY is a kernel/arch detail, not the device-independent strict-`>` rank that mrr and
# ndcg use. Measured on an H100 (the card these cells run on):
#
#   continuous-valued logits (all four realistic shapes)  boundary_ties  0.0%   topk_setdiff 0
#                                                          max|Δ| ~1e-9   -> PASS
#   exact ties AT the k-boundary (synthetic worst case)    topk_setdiff 19950/20000
#                                                          top10_acc cpu 0.009850 vs gpu 0.009550
#                                                          Δ = 3.0e-04  -> 300x OVER the 1e-6 bar
#
# So the failure needs an exact fp32 tie at the top-k boundary. It does not occur on continuous
# logits, and p1 evaluates in fp32 (no fp16 quantisation manufacturing ties) — but the rate on
# REAL reg logits is unmeasured, and every banked reg cell in the study was CPU-scored. Mixing
# scoring devices inside one pooled n=20 cell to save ~40 s per small-state cell is a bad trade.
#
# The right fix is not this flag: it is to make p1 stream the val metric ON GPU the way
# mtl_eval.py already does (`_streamed_cls_metrics`, src/tracking/metrics.py), which makes scoring
# homogeneous at ALL scales instead of splitting by size. That belongs at a freeze boundary,
# applied to every state at once — not mid-study. See MODAL_MANUAL.md section 3b-fix.
#
# Set P1_GPU_VAL=1 to opt OUT of the CPU path (only with fresh evidence for your shapes).
REG_ENV="MTL_CHUNK_VAL_METRIC=1"
# Propagate the ambiguity switch when the caller set it. ENVCOMMON pins MTL_STRICT=1, which also
# arms the tie-break abort -- and both large states trip that certificate at ~1 row in 766k. Being
# able to accept that deliberately (MTL_AMBIGUITY_STRICT=0) WITHOUT disarming the canon-recipe and
# overlap-provenance guards is the difference between a considered decision and dropping every
# guard at once. The count is still recorded in the cell artifact either way.
[ -n "${MTL_AMBIGUITY_STRICT:-}" ] && REG_ENV="$REG_ENV MTL_AMBIGUITY_STRICT=$MTL_AMBIGUITY_STRICT"
[ "${P1_GPU_VAL:-0}" = "1" ] && REG_ENV=""

# ---- torch.compile cache ------------------------------------------------------------------
# The record sets TORCHINDUCTOR_CACHE_DIR only on the JOINT cell; cat and reg inherit the
# default. On the A40 that default is a persistent ~/.cache, so cat/reg still amortise their
# warm-up. In a Modal container it is an ephemeral /tmp that dies with the sandbox, so every
# rented cat/reg cell re-pays the full compile -- MODAL_MANUAL section 4's rule, unapplied.
#
# DEFAULT OFF, deliberately. Tying cat/reg to a persistent cache would change how every rented
# cell is produced, including cells another agent is producing right now against cells already
# banked with a cold cache. CLAUDE.md records that a compiled number is governed by the inductor
# session and is within-fold-sigma rather than bit-reproducible, so this is not a protocol
# change -- but it is not nothing either, and it is not a change to make on someone else's
# behalf mid-study. Opt in with INDUCTOR_SHARE_CELLS=1 when you want the amortisation and are
# willing to own the caveat; leave it unset and cat/reg behave exactly as they always have.
# (The JOINT cell is unaffected either way: the record pins its cache dir explicitly.)
inductor_env(){                 # inductor_env <family>  -> "VAR=..." or nothing
  [ "${INDUCTOR_SHARE_CELLS:-0}" = "1" ] || return 0
  [ -n "${INDUCTOR_ROOT:-}" ] || return 0
  echo "TORCHINDUCTOR_CACHE_DIR=${INDUCTOR_ROOT}/.inductor_cache_v18_${ST}_s${SEED}_$1"
}

# ---- tiny JSON readers (the scorers' outputs are the source of truth, never a re-derivation)
jnum(){                         # jnum <file> <top-level key>
  [ -f "$1" ] || return 0
  "$PY" -c 'import json,sys
d=json.load(open(sys.argv[1])); v=d.get(sys.argv[2])
print("" if v is None else v)' "$1" "$2" 2>/dev/null
}
jreg(){                         # jreg <P1 region_head json>  -> top10_acc_mean * 100
  [ -f "$1" ] || return 0
  "$PY" -c 'import json,sys
d=json.load(open(sys.argv[1]))
a=d["heads"]["next_stan_flow"]["aggregate"]
print(round(a["top10_acc_mean"]*100,4))' "$1" 2>/dev/null
}

# ---- sidecar --------------------------------------------------------------------------------
# SCHEMA PARITY WITH THE RECORD IS THE POINT. v18/score_all.py reads sidecars from
# docs/results/closing_data/v18 and pulls (state, seed, family) -> rundir out of them; the old
# 5-field sidecar this script wrote carried no values, no commit and no protocol block, so a
# rented cell could not be merged or audited the way a local one can. This mirrors
# run_wave.sh's sidecar_write field for field.
#
# NOTE ON $OUT: score_all.py hardcodes SIDE=docs/results/closing_data/v18. Sidecars written to
# the default v18_2 directory are invisible to it. Pass OUT=docs/results/closing_data/v18 when
# the cell is meant to merge into the board, or copy them across at merge time.
SHA=${COMMIT_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}

# Aviso alto quando os sidecars nao vao para onde score_all.py os procura. Nao aborta: uma lane
# exploratoria em v18_2 e legitima. Mas o seed 7 rodou assim e precisou de um passo manual
# depois, entao a escolha nunca deve ser silenciosa.
case "$OUT" in
  *closing_data/v18) : ;;                        # o board: score_all.py enxerga
  *) echo "[lane] AVISO: OUT=$OUT nao e docs/results/closing_data/v18." >&2
     echo "[lane]        score_all.py so le v18; esta celula NAO entrara nas tabelas" >&2
     echo "[lane]        sem um merge manual. Passe OUT=docs/results/closing_data/v18" >&2
     echo "[lane]        se ela e destinada ao board." >&2 ;;
esac
# --- devolver os score JSONs COM o rundir de origem -------------------------------------
# score_all.py nao usa os numeros do sidecar: ele releh cada valor de DENTRO do rundir. Uma
# celula que roda no Modal deixa o rundir no volume, entao sem isto a agregacao reporta
# "sidecar present but <score>.json unreadable" e a celula nao entra nas tabelas.
# Solucao: junto do harvest, gravar cada score JSON sob out/rundirs/<caminho-do-rundir>/,
# de modo que o destino no host seja uma copia literal, sem adivinhar caminho.
harvest_rundir_scores(){        # harvest_rundir_scores <rundir> [arquivos...]
  local rd="${1:-}"; shift || true
  [ -n "$rd" ] || return 0
  local dst="$HARVEST_OUT/rundirs/$rd"
  mkdir -p "$dst"
  local f
  for f in "$@"; do
    [ -s "$rd/$f" ] && cp "$rd/$f" "$dst/$f" 2>/dev/null
  done
  return 0
}

sidecar_write(){                # sidecar_write <family> <wall> <rundir> <cat> <reg> <pid>
  local fam="$1" wall="$2" rd="$3" cv="${4:-}" rv="${5:-}" pid="${6:-}" rec
  case $fam in
    cat)   rec="bs$(cat_bs "$ST") lr$(cat_lr "$ST") logit_adjust_tau=$LA_TAU (replaces class weighting)" ;;
    reg)   rec="max_lr 3e-3 freeze_alpha logit_adjust_tau=0 (OFF: hurts Acc@10, AL -1.84 / IST -2.75)" ;;
    joint) rec="bs8192 cat-lr $(mtl_catlr "$ST") cw0.50 logit_adjust_tau=$LA_TAU (cat head only)" ;;
  esac
  # The tie certificate travels WITH the number or it may as well not exist. p1 records
  # `ambiguous_rows` per fold in its result JSON, but until 2026-08-11 this function dropped it,
  # so a Modal-run reg cell banked a tie-optimistic value with no disclosure while the A40 driver
  # recorded it for the identical recipe. texas s100 shipped that way and had to be back-filled by
  # hand. Read it from the p1 JSON the cell just wrote; empty for families that have none.
  local p1json amb=""
  p1json=$(ls -t docs/results/P1/region_head_${ST}_*_${fam_tag:-v18_${ST}_${fam}_s${SEED}}.json 2>/dev/null | head -1)
  [ -n "$p1json" ] && amb=$("$PY" - "$p1json" <<'AMBPY'
import json, sys
try:
    h = json.load(open(sys.argv[1]))["heads"]
    pf = list(h.values())[0].get("per_fold") or []
    it = pf.values() if isinstance(pf, dict) else pf
    rows = [f.get("ambiguous_rows") for f in it if isinstance(f, dict)]
    print(json.dumps(rows) if any(r is not None for r in rows) else "")
except Exception:
    print("")
AMBPY
)
  "$PY" - "$OUT/${ST}_s${SEED}_${fam}.json" "$ST" "$SEED" "$fam" "$wall" "$rd" \
          "$cv" "$rv" "$SHA" "$rec" "$pid" "${LANE_HOST:-}" "$amb" <<'PY'
import json, sys
out, st, sd, fam, wall, rd, cv, rv, sha, rec, pid, host, amb = sys.argv[1:14]
def f(x):
    try: return float(x)
    except Exception: return None
json.dump({
    "state": st, "seed": int(sd), "family": fam,
    "wall_seconds": int(float(wall)), "rundir": rd or None,
    "cat": f(cv), "reg": f(rv),
    **({"ambiguous_rows": json.loads(amb)} if amb else {}),
    "commit_sha": sha,
    "v18_config": {"engine": "check2hgi_v18", "forward_only": True, "in_channels": 15,
                   "node_layout": ["canonical_11", "continuous_time_4"], "repr_seed": 42},
    "protocol": {"precision": "fp32 (MTL_DISABLE_AMP=1, pinned per-command)", "compile": True,
                 "tf32": True, "folds": 5, "epochs": 50,
                 "cat_metric": "macro-F1 at f1-best epoch (diag-best)",
                 "reg_metric": "top10_acc_indist * (1 - ood_fraction) * 100 at indist-best epoch"},
    "recipe": rec,
    "recipe_version": "v18-approved-2026-08-09 (FINAL_SETTINGS.md)",
    # Provenance a rented cell needs and a local one does not: which box produced it, and the
    # pid the rundir is anchored to. Hardware is NOT yet established as poolable across lanes
    # (MODAL_MANUAL section 10), so every cell must say where it ran.
    "lane_host": host or None,
    "train_pid": pid or None,
}, open(out, "w"), indent=2)
PY
}

# ---- charter section 6.6 guard (run_wave.sh lines 204-215) ----------------------------------
v17_guard(){                    # v17_guard <cat> <reg>
  "$PY" - "$ST" "${1:-}" "${2:-}" <<'PY' 2>/dev/null | while read -r l; do log "  [VERIFY] $l"; done
import sys
V17 = {"alabama": (64.54, 69.80), "arizona": (65.83, 59.56), "florida": (79.85, 77.42),
       "california": (77.05, 65.69), "texas": (77.24, 67.06), "istanbul": (63.33, 75.44)}
st = sys.argv[1]
if st in V17:
    c17, r17 = V17[st]
    try: cv = float(sys.argv[2])
    except Exception: cv = None
    try: rv = float(sys.argv[3])
    except Exception: rv = None
    if cv is not None and abs(cv - c17) < 5:
        print(f"{st}: cat {cv:.2f} is within 5 pp of v17 {c17:.2f} -- INVESTIGATE the forward-only path")
    if rv is not None and abs(rv - r17) > 2:
        print(f"{st}: reg moved {rv-r17:+.2f} pp vs v17 {r17:.2f} (>2 pp) -- INVESTIGATE")
PY
  return 0
}

# ---- HARVEST (Modal returns ONLY ./out/; both entrypoints write elsewhere) --------------
# train.py writes its rundir under results/<engine>/<state>/; p1_region_head_ablation.py
# hard-codes docs/results/P1. Neither is under ./out/, so without this a cell exits 0 and
# returns NOTHING. Verified: the alabama gate only came back because its command had an
# explicit copy. Keep out/ small -- the harvest window is bounded and a multi-GB out/ risks
# harvest_failed, which strands the only copy on a sandbox that self-terminates.
HARVEST=${HARVEST:-0}          # set HARVEST=1 on Modal; 0 on the A40 (no harvest needed)
# OUTDIR is the job workdir Modal harvests from. `run_lane.sh` is usually invoked with
# cwd=/data/repo (the Volume), so ./out there is NOT the harvested directory -- the harvested one
# is $J/out in the job workdir. Pass HARVEST_OUT=$J/out so the copy lands where it is collected.
HARVEST_OUT=${HARVEST_OUT:-out}
harvest(){                      # harvest <rundir> <family>
  [ "$HARVEST" = "1" ] || return 0
  # `local a=$1 b=$2` evaluates BOTH RHS before assigning, so under `set -u` an empty $2
  # aborts the whole script -- which is exactly how the first harvest verification died.
  # Default them explicitly instead.
  local rd="${1:-}" fam="${2:-cell}" dst
  dst="$HARVEST_OUT/${ST}_s${SEED}_${fam}"
  mkdir -p "$dst"
  # Only the SMALL score/metric JSONs. The harvest stream is bounded (~2 min): a multi-GB
  # out/ risks harvest_failed, which strands the only copy on a self-terminating sandbox.
  # Bulk artefacts stay on the Volume, which survives teardown and the run clock.
  if [ -n "$rd" ] && [ -d "$rd" ]; then
    cp "$rd"/*.json "$dst"/ 2>/dev/null
    [ -d "$rd/metrics" ] && { mkdir -p "$dst/metrics"; cp "$rd"/metrics/*standard_scores.json "$dst/metrics"/ 2>/dev/null; }
  fi
  # The reg family's deliverable lives outside the rundir entirely.
  # ANCHOR THE SEED AT BOTH ENDS. The old glob was *${ST}*s${SEED}*, and `*s1*` matches
  # `..._reg_s100.json` -- verified. At seed 1 that copied seed-100 results into a seed-1
  # harvest. `_s${SEED}.json` can only match the seed it names.
  mkdir -p "$HARVEST_OUT/P1"
  cp docs/results/P1/region_head_"${ST}"_*_s"${SEED}".json "$HARVEST_OUT/P1"/ 2>/dev/null
  du -sh "$HARVEST_OUT" 2>/dev/null | tail -1
}

# INCREMENTAL harvest. `./out/` is staged UNCONDITIONALLY at a deadline, so what survives a
# run-clock kill is whatever was already written there -- not what a final `cp` would have
# written. The CA joint that died at 3.6 h lost its workspace copy for exactly this reason
# (its per-fold results were on the Volume and recoverable, but nothing reached ./out/).
# Run this in the background of a long cell so each finished fold is banked as it lands.
HARVEST_WATCH_PID=""
harvest_watch(){                # harvest_watch <rundir-glob> <family> <interval_s> <train_pid>
  HARVEST_WATCH_PID=""
  [ "$HARVEST" = "1" ] || return 0
  local glob="$1" fam="$2" iv="${3:-300}" tpid="${4:-}"
  # NO command substitution around this call: the subshell loop never exits, so $( ) would
  # block forever waiting for EOF on the capture pipe. The pid goes to a GLOBAL instead, and
  # the subshell's stdout/stderr are closed off so it can never hold a pipe open.
  ( while :; do
      sleep "$iv"
      rd=$(rundir_for "$glob" "$tpid")
      [ -n "$rd" ] && harvest "$rd" "$fam"
    done ) >/dev/null 2>&1 &
  HARVEST_WATCH_PID=$!
  # disown so killing the watcher does not print a job-control "Terminated" notice into the
  # cell log, which is the log a post-mortem reads.
  disown $HARVEST_WATCH_PID 2>/dev/null || true
}

harvest_watch_stop(){
  [ -n "${HARVEST_WATCH_PID:-}" ] && kill "$HARVEST_WATCH_PID" 2>/dev/null
  HARVEST_WATCH_PID=""
  return 0
}

# ---- rundir resolution: ANCHORED TO THE LAUNCHED PID, never newest-mtime -----------------
# MLHistory names every rundir `<prefix>_<timestamp>_<os.getpid()>` (tracking/experiment.py:268),
# and all 22 rundir call sites in the v18 driver family resolve it as `*_${pid}`. run_wave.sh
# states the rule outright: "Rundirs are captured by the launched PID, never by newest-mtime
# globbing (two jobs run concurrently by design)."
#
# This script used to glob `ls -dt ... | head -1`. That is wrong under the packing MODAL_MANUAL
# section 12 recommends -- one job per seed, several jobs sharing one Volume at cwd=/data/repo --
# because two same-state cells then write sibling rundirs under the same prefix and the newest
# one is a race, not an identity. The heartbeat's Volume.commit() makes those writes visible
# across sandboxes, so the race is reachable rather than theoretical: the scorer would score
# another seed's rundir and the sidecar would attest to it.
#
# `env VAR=1 python ...` execs in place, so $! is the python PID -- the same assumption
# run_wave.sh makes.
rundir_for(){                   # rundir_for <prefix> <pid>
  local pre="$1" pid="${2:-}" rd=""
  if [ -n "$pid" ]; then
    # PID ALONE IS NOT AN IDENTITY when the volume is shared. Containers each start their PID
    # space from scratch, so two concurrent cells of the SAME state routinely give the trainer
    # the same low pid (76 was observed on four containers at once). If a sibling's rundir with
    # that pid is already on the volume when this container starts, `ls ... _<pid>` matches it
    # and this cell attests a number computed from someone else's run.
    #
    # That is not hypothetical: on 2026-08-10 texas s100 scored texas s7's rundir this way, and
    # -- because a Modal volume gives a container the snapshot it had at start -- saw it with
    # only 1 of 5 folds, banking `n_folds=1, 36.4189` (fold 1 of s7) as if it were the s100 cell.
    # It also overwrote s7's own score file. Correct value after re-scoring: 36.3445 over 5 folds.
    #
    # $LANE_MARK is touched at lane start, so anything older cannot belong to this cell. Same
    # anchor the heartbeat already uses (see folds_done above) -- it just never got applied here.
    rd=$(find results/$ENG/$ST -maxdepth 1 -name "${pre}*_${pid}" -newer "$LANE_MARK" \
           -type d 2>/dev/null | head -1)
    [ -n "$rd" ] && { echo "$rd"; return 0; }
    # A pid match that FAILS the freshness test is the collision above. Never silently accept it.
    local stale
    stale=$(ls -d results/$ENG/$ST/${pre}*_"${pid}" 2>/dev/null | head -1)
    [ -n "$stale" ] && log "  WARN pid $pid matches '$stale' but it predates this lane -- ignoring (sibling cell on the shared volume)"
  fi
  # Fallback only. Say so loudly: an unanchored pick is unsafe the moment anything else
  # shares this volume, and a silent fallback is how a wrong number would get attested.
  rd=$(ls -dt results/$ENG/$ST/${pre}* 2>/dev/null | head -1)
  [ -n "$rd" ] && log "  WARN rundir not found for pid='$pid'; falling back to newest '$rd' (UNSAFE if another job shares this volume)"
  echo "$rd"
}

cell_cat(){
  local side="$OUT/${ST}_s${SEED}_cat.json"
  [ -f "$side" ] && { log "SKIP $ST s$SEED cat"; return 0; }
  local bs lr t0; bs=$(cat_bs "$ST"); lr=$(cat_lr "$ST"); t0=$SECONDS
  log "START $ST s$SEED cat (bs=$bs lr=$lr tau=$LA_TAU fp32)"
  env $ENVCOMMON MTL_NO_TRAIN_DIAGNOSTICS=1 $(inductor_env "cat") \
    "$PY" scripts/train.py --task next --state "$ST" --engine "$ENG" \
      --seed "$SEED" --epochs 50 --folds 5 --batch-size "$bs" --max-lr "$lr" \
      --logit-adjust-tau "$LA_TAU" --model next_gru --embedding-dim 64 \
      --task-a-input-type checkin \
      --compile --tf32 --no-checkpoints > "$OUT/logs/${ST}_s${SEED}_cat.out" 2>&1 &
  local pid=$!
  wait $pid; local rc=$?
  local rd; rd=$(rundir_for "next_" "$pid")
  if [ $rc -ne 0 ] || [ -z "$rd" ] || [ ! -d "$rd" ]; then
    save_log cat "$OUT/logs/${ST}_s${SEED}_cat.out"
    log "  FAIL  $ST s$SEED cat rc=$rc rd='$rd' -- NO sidecar written (cell will be retried)"
    return 1
  fi
  # score IN the container: the scorer writes stl_cat_ceiling_score.json INTO the rundir,
  # which is what score_all.py reads back. Scoring here means the harvested rundir is
  # already complete and the merge needs no second pass.
  "$PY" scripts/closing_data/score_stl_cat_ceiling.py "$rd" \
      --tag "v18_${ST}_cat_s${SEED}" >> "$OUT/logs/${ST}_s${SEED}_cat.out" 2>&1
  local cv; cv=$(jnum "$rd/stl_cat_ceiling_score.json" cat_macro_f1_mean)
  harvest "$rd" cat
  harvest_rundir_scores "$rd" stl_cat_ceiling_score.json
  if [ -z "$cv" ]; then
    save_log cat "$OUT/logs/${ST}_s${SEED}_cat.out"
    log "  FAIL  $ST s$SEED cat: trained but produced no score -- NO sidecar written"
    return 1
  fi
  sidecar_write cat "$((SECONDS-t0))" "$rd" "$cv" "" "$pid"
  log "DONE  $ST s$SEED cat = $cv ($((SECONDS-t0))s) rundir=$rd"
}

cell_reg(){
  local side="$OUT/${ST}_s${SEED}_reg.json"
  [ -f "$side" ] && { log "SKIP $ST s$SEED reg"; return 0; }
  local t0=$SECONDS tag="v18_${ST}_reg_s${SEED}"
  log "START $ST s$SEED reg (fp32, NO logit adjustment)"
  # `-u` matches the record (run_wave.sh line 146). It is not cosmetic on a rented box: a
  # buffered log loses its most recent output when the run clock kills the container, which
  # is exactly the log you need for the post-mortem.
  env $ENVCOMMON $REG_ENV $(inductor_env "reg") \
    "$PY" -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
      --input-type region --region-emb-source "$V14" \
      --override-hparams freeze_alpha=True alpha_init=0.0 \
      --engine-override "$ENG" --folds 5 --epochs 50 --seed "$SEED" --target region \
      --max-lr 0.003 --compile --tf32 --tag "$tag" \
      > "$OUT/logs/${ST}_s${SEED}_reg.out" 2>&1
  local rc=$?
  # The reg deliverable is docs/results/P1/region_head_<state>_region_5f_50ep_<tag>.json --
  # NOT in a rundir. A rented reg cell that loses this file fails SILENTLY at merge time.
  # Construct the EXACT name the ablation writes (run_wave.sh line 154 does the same) instead
  # of globbing: `ls -t *reg_s1*.json | head -1` returns the seed-100 file whenever one is
  # newer, which would attest seed-100 numbers under a seed-1 sidecar. Verified, not theorised.
  local rf="docs/results/P1/region_head_${ST}_region_5f_50ep_${tag}.json"
  [ -f "$rf" ] || rf=""
  harvest "" reg
  local rv=""; [ -n "$rf" ] && rv=$(jreg "$rf")
  if [ $rc -ne 0 ] || [ -z "$rf" ] || [ -z "$rv" ]; then
    save_log reg "$OUT/logs/${ST}_s${SEED}_reg.out"
    log "  FAIL  $ST s$SEED reg rc=$rc p1='$rf' val='$rv' -- NO sidecar written (cell will be retried)"
    return 1
  fi
  sidecar_write reg "$((SECONDS-t0))" "$rf" "" "$rv" ""
  log "DONE  $ST s$SEED reg = $rv ($((SECONDS-t0))s) p1file=$rf"
}

cell_joint(){
  local side="$OUT/${ST}_s${SEED}_joint.json"
  [ -f "$side" ] && { log "SKIP $ST s$SEED joint"; return 0; }
  local clr t0; clr=$(mtl_catlr "$ST"); t0=$SECONDS
  log "START $ST s$SEED joint (bs8192 cat-lr $clr cw0.50 tau=$LA_TAU fp32)"
  # MTL_ONECYCLE_PER_HEAD_LR=1 is LOAD-BEARING: without it --cat-lr/--reg-lr are inert
  # and the run silently reverts to the previous version's schedule.
  # TORCHINDUCTOR_CACHE_DIR is keyed per state+seed exactly as the record does it. On a rented
  # container the default cache lives in an ephemeral /tmp, so every cell would pay the full
  # torch.compile warm-up again; pointing it at a persistent path is what makes --compile pay
  # for itself across cells rather than once per container.
  # bank each fold as it lands: this cell is hours long and a run-clock kill keeps only what
  # is already under the harvested out/. The watcher starts AFTER the launch so it can be
  # given the training pid and resolve the rundir the same anchored way the cell does.
  env $ENVCOMMON MTL_CHUNK_VAL_METRIC=1 MTL_ONECYCLE_PER_HEAD_LR=1 MTL_COMPILE_DYNAMIC=1 \
      TORCHINDUCTOR_CACHE_DIR="${INDUCTOR_ROOT:-$HOME}/.inductor_cache_v18_${ST}_s${SEED}" \
    "$PY" scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$ENG" --state "$ST" --seed "$SEED" --epochs 50 --folds 5 \
      --batch-size 8192 --mtl-loss static_weight --category-weight 0.50 \
      --no-reg-class-weights --no-cat-class-weights --logit-adjust-tau "$LA_TAU" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple \
      --compile --tf32 --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints \
      > "$OUT/logs/${ST}_s${SEED}_joint.out" 2>&1 &
  local pid=$!
  harvest_watch "mtlnet_" joint 300 "$pid"
  wait $pid; local rc=$?
  harvest_watch_stop                         # stop the incremental watcher
  local rd; rd=$(rundir_for "mtlnet_" "$pid")
  if [ $rc -ne 0 ] || [ -z "$rd" ] || [ ! -d "$rd" ]; then
    save_log joint "$OUT/logs/${ST}_s${SEED}_joint.out"
    log "  FAIL  $ST s$SEED joint rc=$rc rd='$rd' -- NO sidecar written (cell will be retried)"
    return 1
  fi
  # Score IN the container, exactly as run_wave.sh lines 195-197 does. Without this the joint
  # rundir comes home unscored: a40_matched_score.json is what score_all.py and
  # run_modal_cell.values_from() both read, so an unscored joint cell reports no numbers at
  # all and needs a second pass over a rundir that only exists on the Volume.
  #   db_* diag-best (Table-3 convention)  |  jb_* joint-best (the single served checkpoint)
  "$PY" scripts/closing_data/a40_score_matched.py "$rd" --seed "$SEED" \
      --tag "v18_${ST}_joint_s${SEED}" >> "$OUT/logs/${ST}_s${SEED}_joint.out" 2>&1
  "$PY" scripts/closing_data/score_joint_best.py "$rd" --seed "$SEED" \
      --tag "v18_${ST}_joint_s${SEED}" >> "$OUT/logs/${ST}_s${SEED}_joint.out" 2>&1 || true
  local cv rv
  cv=$(jnum "$rd/a40_matched_score.json" cat_macro_f1_mean)
  rv=$(jnum "$rd/a40_matched_score.json" reg_full_top10_mean)
  harvest "$rd" joint
  harvest_rundir_scores "$rd" a40_matched_score.json joint_best_score.json
  if [ -z "$cv" ]; then
    save_log joint "$OUT/logs/${ST}_s${SEED}_joint.out"
    log "  FAIL  $ST s$SEED joint: trained but produced no score -- NO sidecar written"
    return 1
  fi
  sidecar_write joint "$((SECONDS-t0))" "$rd" "$cv" "$rv" "$pid"
  log "DONE  $ST s$SEED joint cat=$cv reg=$rv ($((SECONDS-t0))s) rundir=$rd"
  # Charter section 6.6 sanity, the same guard the record runs. A v18 category number landing
  # near its v17 value means the forward-only path is broken, not that v18 did well.
  v17_guard "$cv" "$rv"
}

# ---- cell selection -------------------------------------------------------------------------
# CELLS lets a caller run a SUBSET (e.g. "cat,reg" when the joint cell is already banked, or
# when only the two cheap families are wanted). Previously the driver's --cells flag gated only
# the preflight while this script ran all three regardless, so asking for two cells silently
# bought three -- on a joint cell that is hours of GPU nobody asked for.
CELLS=${CELLS:-cat,reg,joint}
want(){ case ",${CELLS}," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }

# Marker the heartbeat anchors its rundir search to (see heartbeat()).
LANE_MARK="$OUT/.lane_start_${ST}_s${SEED}"
: > "$LANE_MARK"
[ "$HARVEST" = "1" ] && heartbeat 60
log "===== v18_2 LANE $ST seed=$SEED engine=$ENG cells=$CELLS (fp32 pinned) ====="
if [ "${PARALLEL:-0}" = "1" ]; then
  # All three cells share ONE card. Only safe when their combined VRAM fits: on a saturated
  # GPU concurrency buys nothing (measured SM 96-100% on the A40, concurrent cells ~2x slower
  # each), so this is a LATENCY choice for a small state on a large card, not a throughput one.
  log "  PARALLEL=1: selected cells share this GPU"
  PIDS=""
  want cat   && { cell_cat   & PIDS="$PIDS $!"; }
  want reg   && { cell_reg   & PIDS="$PIDS $!"; }
  want joint && { cell_joint & PIDS="$PIDS $!"; }
  rc=0
  for p in $PIDS; do wait "$p" || rc=1; done
  [ $rc -ne 0 ] && log "  one or more cells FAILED (see per-cell logs)"
else
  want cat   && cell_cat
  want reg   && cell_reg
  want joint && cell_joint
fi
heartbeat_stop
# mkdir FIRST. $HARVEST_OUT/logs is created by save_log(), which only runs when a cell FAILS,
# so on a clean run the directory did not exist and this cp silently did nothing -- the lane
# log, promised as a deliverable in README "Instrumentation", was harvested only from runs
# that had already gone wrong.
if [ "$HARVEST" = "1" ]; then
  mkdir -p "$HARVEST_OUT/logs"
  cp "$OUT/logs/${ST}_s${SEED}.log" "$HARVEST_OUT/logs/" 2>/dev/null
  # the sidecars are the merge's index; they live on the Volume otherwise and never come home
  cp "$OUT/${ST}_s${SEED}"_*.json "$HARVEST_OUT/" 2>/dev/null
fi
log "===== LANE $ST seed=$SEED COMPLETE ====="
