#!/usr/bin/env bash
# CRITICAL-tier watchdog (author-approved 2026-10-03 for the FL G1 training arms). usage: g1_run_crit.sh <tag> <cmd...>
# Kills ONLY its own child tree (by PID) at: kernel memory pressure CRITICAL (kern.memorystatus_vm_pressure_level=4),
# free memory < 10%, swap total > 14 GB, or any disk < 3 GB free. Samples every 1 s into trace.log (kept if it dies).
C="/Volumes/Vitor's SSD/ingred_g1fl"; R=/Users/vitor/Desktop/mestrado/ingred; cd "$C" || exit 9
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" OUTPUT_DIR="${OUTPUT_DIR:-$C/output}" DATA_ROOT="$C/data" RESULTS_ROOT="${RESULTS_ROOT:-$C/results}"
export MTL_RAM_HEADROOM_GB=4 MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 PYTHONDONTWRITEBYTECODE=1
TAG=$1; shift; L="$C/g1_logs/$TAG"; mkdir -p "$L"; touch "$L/MARKER"
echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD) tier=CRITICAL swap_used_MB_at_start=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}') swap_total_MB_at_start=$(sysctl -n vm.swapusage | awk '{gsub("M","",$3); print int($3)}') disk_int_GB_at_start=$(df -g / | awk 'NR==2{print $4}') disk_ssd_GB_at_start=$(df -g "/Volumes/Vitor's SSD" | awk 'NR==2{print $4}') pressure_at_start=$(sysctl -n kern.memorystatus_vm_pressure_level)" > "$L/RUN.txt"; echo "cmd: $*" >> "$L/RUN.txt"
T0=$(date +%s)
/usr/bin/time -l "$@" > "$L/out.log" 2>&1 & CP=$!
( echo "time pressure_lvl free_pct swap_total_MB swap_used_MB wired_GB child_rss_GB disk_int_GB disk_ssd_GB" > "$L/trace.log"
  while kill -0 $CP 2>/dev/null; do
    pl=$(sysctl -n kern.memorystatus_vm_pressure_level); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}')
    st=$(sysctl -n vm.swapusage | awk '{gsub("M","",$3); print int($3)}'); su=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
    wi=$(vm_stat | awk '/wired down/{gsub("\\.","",$4); printf "%.1f",$4*16384/1e9}')
    cr=$(ps -o rss= -p $(pgrep -P $CP | head -1) 2>/dev/null | awk '{printf "%.1f",$1/1048576}')
    di=$(df -g / | awk 'NR==2{print $4}'); ds=$(df -g "/Volumes/Vitor's SSD" 2>/dev/null | awk 'NR==2{print $4}'); ds=${ds:-0}
    echo "$(date +%T) $pl $fr $st $su $wi ${cr:-0} $di $ds" >> "$L/trace.log"
    if [ "$pl" -ge 4 ] || [ "$fr" -lt 10 ] || [ "$st" -gt 14336 ] || [ "$di" -lt 3 ] || [ "$ds" -lt 3 ]; then
      echo "ABORT $(date +%T) pressure=$pl free=$fr swap_total=$st disk_int=$di disk_ssd=$ds" >> "$L/RUN.txt"; touch "$L/ABORTED"
      pkill -TERM -P $CP; kill -TERM $CP 2>/dev/null; break; fi
    sleep 1; done ) & WD=$!
wait $CP; RC=$?; kill $WD 2>/dev/null; wait $WD 2>/dev/null
echo "rc=$RC wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/out.log" | awk '{print $1}')" >> "$L/RUN.txt"
echo "trace peaks: $(awk 'NR>1{if($2>p)p=$2; if(m==""||$3<m)m=$3; if($4>s)s=$4; if($6>w)w=$6; if($7>r)r=$7} END{print "max_pressure="p" min_free="m"% max_swap_total="s"MB max_wired="w"GB max_child_rss="r"GB"}' "$L/trace.log")" >> "$L/RUN.txt"
LEAK=$( { find $R/output/ $R/data/ $R/results/ $R/docs/results/ -newer "$L/MARKER" ! -name .DS_Store 2>/dev/null; find "/Volumes/Vitor's SSD/ingred_g1/output/" -path "*florida*" -newer "$L/MARKER" 2>/dev/null; } | head -5)
[ -z "$LEAK" ] && echo "repo-write-guard OK" >> "$L/RUN.txt" || { echo "repo-write-guard FAIL:" >> "$L/RUN.txt"; echo "$LEAK" >> "$L/RUN.txt"; }
echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
