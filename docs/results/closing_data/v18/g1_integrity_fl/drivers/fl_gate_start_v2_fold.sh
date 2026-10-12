#!/usr/bin/env bash
# Start gate v2 (D2b 17571c16, MTL_DATASET_CPU=1 cat arms; run after a fresh boot) for G1 FL fold 0 (knowladge 2026-10-03): internal disk >= 15 GB, pressure normal/warn (<4), no other MPS job. Fails closed.
di=$(df -g / | awk 'NR==2{print $4}'); pl=$(sysctl -n kern.memorystatus_vm_pressure_level)
mps=$(pgrep -fl "scripts/(train|p1_region_head_ablatio|baselines/b3_hmt_gr|baselines/build_ctle_substrat|integrity_v2/build_study_rep)[n.er]" | grep -v fl_gate_start)
sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); st=$(sysctl -n vm.swapusage | awk '{gsub("M","",$3); print int($3)}')
echo "GATE $(date '+%F %T') disk_int_GB=$di pressure=$pl swap_used_MB=$sw swap_total_MB=$st other_jobs=[${mps}]"
if [ "$di" -ge 15 ] && [ "$pl" -lt 4 ] && [ -z "$mps" ]; then echo "GATE PASS -> FL fold $1 starts"; bash "/Volumes/Vitor's SSD/ingred_g1fl/g1_logs/g1_fl_fold_ordered_v2.sh" "${1:?fold}"; echo "FL fold $1 driver ended rc=$? $(date '+%F %T')"
else echo "GATE FAIL -> FL NOT started tonight (defer to fresh boot)"; fi
