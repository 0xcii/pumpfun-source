#!/bin/bash
# trial.sh <name> <workN> : build var/<name> with IR+MIR capture, then metrics + frame oracle
set -u
OUT=/Users/shawwalters/.cache/pumpfun-reconstruction/lanes/w12a05-cto-framemir
WT=/Users/shawwalters/Documents/Codex/2026-10-24/pump-main-swarm/worktrees/w12a05-cto-framemir
H=$WT/reconstruction/harness; FO=$WT/reconstruction/pump-main/lanes/w4-frame-oracle/frameoracle.py
n=$1; w=$2; T=$OUT/t/$n; mkdir -p $T
PUMP_BUILD_SLOTS=10 python3 $WT/reconstruction/pump-main/lanes/w12a05-cto-framemir/tools/capmir.py $OUT/var/$n $OUT/$w $T > $T/cap.log 2>&1 || { echo "$n BUILD FAIL"; tail -30 $T/cap.log | grep -E "^error|-->" | head; exit 1; }
python3 $H/target_metric.py $T/unstripped.so 0x22a10 --sym 'admin_cto::execute$' --slots 4000 2>/dev/null | head -1 > $T/cto.json
python3 -c "import json;d=json.load(open('$T/cto.json'));print('$n', d['cand_bytes'], d['ratio'], d['slots_diff'], d.get('calls_candidate'))"
python3 $FO --ir $T/pump_recovered.ll --sym '_ZN14pump_recovered9admin_cto7execute17h[0-9a-f]+E' --win 0x22a10 --name $n --out $OUT/fo --no-partition > $OUT/fo/$n.txt 2>&1
head -3 $OUT/fo/$n.txt | cut -c1-200
