#!/usr/bin/env bash
# v18_2 run monitor — "is it alive, is it writing where I think, and will it finish?"
#
# Answers the four questions that cost hours when nobody asks them:
#   1. is a driver/trainer actually running, and is anything DUPLICATING it?
#   2. is it writing to the path the merge will read, and is that path GROWING?
#   3. is the GPU doing work, or thermally/power throttled into a crawl?
#   4. is the box about to run out of disk or RAM mid-run?
#
#   usage: monitor.sh [repo_root]         one-shot, human-readable
#          WATCH=60 monitor.sh            repeat every 60 s
set -uo pipefail
REPO=${1:-/home/vitor.oliveira/PoiMtlNet}
OUT=${OUT:-docs/results/closing_data/v18_2}
V18=${V18:-docs/results/closing_data/v18}
cd "$REPO" || { echo "no repo at $REPO"; exit 2; }

hr(){ printf '%s\n' "------------------------------------------------------------"; }

# ---- portability shims: the Modal image has no procps and no /home ----------------------
have(){ command -v "$1" >/dev/null 2>&1; }
# pgrep -f replacement over /proc; prints matching pids
pids_matching(){                # pids_matching <extended-regex over cmdline>
  local re="$1" p cmd
  if have pgrep; then pgrep -f "$re" 2>/dev/null; return 0; fi
  for p in /proc/[0-9]*; do
    [ -r "$p/cmdline" ] || continue
    cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null)
    case "$cmd" in *[!\ ]*) : ;; *) continue ;; esac
    echo "$cmd" | grep -qE "$re" && basename "$p"
  done
  return 0
}
cmdline_of(){ tr '\0' ' ' < /proc/"$1"/cmdline 2>/dev/null; }
etime_of(){ local j; j=$(awk '{print $22}' /proc/"$1"/stat 2>/dev/null);
            local hz; hz=$(getconf CLK_TCK 2>/dev/null || echo 100)
            local up; up=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo 0)
            [ -n "$j" ] && echo $(( up - j/hz )) || echo 0; }
# the filesystem that actually matters here: where results are being written
DATA_FS=${DATA_FS:-$PWD}

procs(){
  echo "== PROCESSES =="
  local drv=""
  for p in $(pids_matching 'run_wave|run_lane|run_regen'); do
    local cl; cl=$(cmdline_of "$p"); case "$cl" in *"sh -c"*) continue ;; esac
    drv="$drv$p $cl
"
  done
  if [ -z "$drv" ]; then echo "  drivers : NONE"; else printf '%s' "$drv" | sed 's/^/  driver  : /'; fi
  local n=0
  for p in $(pids_matching 'train\.py|p1_region_head_ablation\.py'); do
    n=$((n+1))
    local et st sd tk
    et=$(ps -o etimes= -p "$p" 2>/dev/null | tr -d ' '); [ -z "$et" ] && et=$(etime_of "$p")
    st=$(tr '\0' '\n' < /proc/$p/cmdline 2>/dev/null | grep -A1 '^--state$' | tail -1)
    sd=$(tr '\0' '\n' < /proc/$p/cmdline 2>/dev/null | grep -A1 '^--seed$'  | tail -1)
    tk=$(tr '\0' '\n' < /proc/$p/cmdline 2>/dev/null | grep -A1 '^--task$'  | tail -1)
    printf '  trainer : pid=%-7s %-9s seed=%-4s task=%-5s elapsed=%sh%02dm\n' \
           "$p" "${st:-?}" "${sd:-?}" "${tk:-reg}" "$((et/3600))" "$(((et%3600)/60))"
  done
  [ "$n" = 0 ] && echo "  trainer : NONE"
  # DUPLICATION: two trainers on the same state+seed means two drivers are racing. This
  # happened once and would have halved throughput while duplicating cells.
  local dup
  dup=$(for p in $(pids_matching 'train\.py'); do
          tr '\0' '\n' < /proc/$p/cmdline 2>/dev/null | grep -A1 -E '^--(state|seed)$' | grep -v '^--' | paste -sd/
        done | sort | uniq -d)
  [ -n "$dup" ] && echo "  !! DUPLICATE cells running: $dup"
  return 0
}

writing(){
  echo "== IS IT WRITING (and where) =="
  # The merge reads sidecars + rundir score JSONs. A trainer that is alive but writing nothing
  # for 20+ min is the failure mode that silently eats a night.
  local newest
  newest=$(find results -name '*standard_scores.json' -newermt '-30 minutes' 2>/dev/null | wc -l)
  echo "  score files written in last 30 min : $newest"
  local rd
  rd=$(ls -dt results/check2hgi_v18/*/{next,mtlnet}_* 2>/dev/null | head -1)
  if [ -n "$rd" ]; then
    echo "  newest rundir : $rd"
    echo "                  age=$(( ($(date +%s) - $(stat -c %Y "$rd")) / 60 ))min  size=$(du -sh "$rd" 2>/dev/null | cut -f1)"
    echo "                  folds done: $(ls "$rd"/metrics/*standard_scores.json 2>/dev/null | wc -l)/5"
  fi
  echo "  sidecars v18   : $(ls $V18/*.json 2>/dev/null | wc -l)"
  echo "  sidecars v18_2 : $(ls $OUT/*.json 2>/dev/null | wc -l)"
  # P1 is OUTSIDE the rundir: a reg cell that loses it fails silently at merge time.
  echo "  P1 region files: $(ls docs/results/P1/*.json 2>/dev/null | wc -l)"
}

gpu(){
  echo "== GPU =="
  command -v nvidia-smi >/dev/null || { echo "  no nvidia-smi"; return 0; }
  nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw,power.limit,clocks_throttle_reasons.active \
             --format=csv,noheader,nounits | while IFS=, read -r u um mu mt t pd pl thr; do
    printf '  util=%s%%  mem_io=%s%%  mem=%s/%s MiB  temp=%s C  power=%sW/%sW\n' \
           "$(echo $u|xargs)" "$(echo $um|xargs)" "$(echo $mu|xargs)" "$(echo $mt|xargs)" \
           "$(echo $t|xargs)" "$(echo $pd|xargs)" "$(echo $pl|xargs)"
    # Decode the throttle bitmask. These cost real throughput and are invisible in `util`,
    # which happily reads 100% while the clocks are capped.
    local h; h=$(echo "$thr" | xargs)
    local v=$((h))
    local msg=""
    (( v & 0x1  )) && msg="$msg GPU_IDLE"
    (( v & 0x4  )) && msg="$msg SW_POWER_CAP"
    (( v & 0x8  )) && msg="$msg HW_SLOWDOWN"
    (( v & 0x20 )) && msg="$msg SW_THERMAL"
    (( v & 0x40 )) && msg="$msg HW_THERMAL"
    (( v & 0x80 )) && msg="$msg HW_POWER_BRAKE"
    if [ -n "$msg" ]; then echo "  THROTTLED:$msg  (clocks capped -- util% will still read high)"; fi
    local ti; ti=$(echo "$t" | xargs)
    [ "${ti:-0}" -ge 85 ] 2>/dev/null && echo "  !! ${ti}C is hot: sustained >85C throttles and slows every cell"
  done
  nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | sed 's/^/  app: /'
}

resources(){
  echo "== HOST RESOURCES =="
  df -BG "$DATA_FS" 2>/dev/null | tail -1 | awk -v m="$DATA_FS" '{printf "  disk %-10s: %s used of %s (%s) -- %s free\n",m,$3,$2,$5,$4}'
  local freeg; freeg=$(df -BG "$DATA_FS" 2>/dev/null | tail -1 | awk '{gsub("G","",$4);print $4+0}')
  [ "${freeg:-999}" -lt 25 ] 2>/dev/null && echo "  !! under 25G free: an engine build or rundir can fill this mid-run"
  if have free; then free -g | awk '/^Mem:/{printf "  RAM        : %sG used of %sG, %sG available\n",$3,$2,$7}'
  else awk '/MemTotal/{t=$2}/MemAvailable/{a=$2}END{printf "  RAM        : %.0fG used of %.0fG, %.0fG available\n",(t-a)/1048576,t/1048576,a/1048576}' /proc/meminfo
  fi
  awk '{printf "  loadavg    : %s %s %s (cores=%d)\n",$1,$2,$3,'"$(nproc)"'}' /proc/loadavg
}

once(){ date -Is; hr; procs; hr; writing; hr; gpu; hr; resources; hr; }

if [ -n "${WATCH:-}" ]; then while :; do once; sleep "$WATCH"; done; else once; fi
