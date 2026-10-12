#!/usr/bin/env bash
# FL G1 chain: after fold k's driver ends rc=0, free fold k's scored TO engine parquet, then gate+run fold k+1. Stops at first failure/gate fail.
G=/Users/vitor/g5_scratch/logs; C="/Volumes/Vitor's SSD/ingred_g1fl"
for N in 2 3 4; do P=$((N-1))
  until grep -q "FL fold $P driver ended" $G/fl_gate_v2.log 2>/dev/null; do sleep 30; done
  grep -q "FL fold $P driver ended rc=0" $G/fl_gate_v2.log || { echo "CHAIN STOP: fold $P driver did not end rc=0 $(date '+%F %T')"; exit 1; }
  grep -q "^rc=0" "$C/g1_logs/florida_f${P}_reg_to/RUN.txt" || { echo "CHAIN STOP: fold $P reg_to not rc=0"; exit 1; }
  E=/Users/vitor/g1_fl_scratch/output/check2hgi_v18_to_f$P/florida/input
  if [ -f "$E/next.parquet" ] && [ -f "$C/results/integ18_repr/florida/TO_F$P/win_matched.npz" ]; then rm -f "${E:?}/next.parquet"; echo "next.parquet deleted $(date '+%F %T') after FL f$P fully scored; rebuild from results/integ18_repr/florida/TO_F$P/win_matched.npz" > "$E/DELETED.txt"; echo "freed f$P TO engine $(date '+%F %T')"; fi
  bash $G/fl_gate_start_v2_fold.sh $N >> $G/fl_gate_v2.log 2>&1
  grep -q "GATE PASS -> FL fold $N starts" $G/fl_gate_v2.log || { echo "CHAIN STOP: gate failed for fold $N $(date '+%F %T')"; exit 1; }
done; echo "CHAIN DONE $(date '+%F %T')"
