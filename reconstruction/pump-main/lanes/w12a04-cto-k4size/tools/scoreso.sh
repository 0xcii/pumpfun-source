#!/bin/bash
# scoreso.sh <dir with unstripped.so>: measure.sh's scoring half on an existing build (no rebuild)
set -u
OUT=$1; C=$HOME/.cache/pumpfun-reconstruction; BASE=${2:-$C/w11/current-baseline/score.json}
H=/Users/shawwalters/Documents/Codex/2026-10-24/pump-main-swarm/worktrees/w11-baseline/reconstruction/harness
python3 "$H/score.py" "$OUT/unstripped.so" --baseline "$BASE" --json "$OUT/score.json" --quiet > /dev/null 2>&1
python3 "$H/target_metric.py" "$OUT/unstripped.so" 0x5b3b0 --sym 'multi_hop_curve::swap_hop$' --slots 4000 2>/dev/null | head -1 > "$OUT/hop.json"
python3 "$H/target_metric.py" "$OUT/unstripped.so" 0x22a10 --sym 'admin_cto::execute$' --slots 4000 2>/dev/null | head -1 > "$OUT/cto.json"
python3 - "$OUT" "$BASE" <<'PY'
import json, sys
out, base = sys.argv[1], sys.argv[2]
s = json.load(open(f"{out}/score.json"))
b = json.load(open(base))["windows"]
w = s["windows"]
hx = lambda k: hex(int(k))
loss = [hx(k) for k in b if b[k]["normalized"] and not w.get(k, {}).get("normalized")]
rloss = [hx(k) for k in b if b[k]["raw"] and not w.get(k, {}).get("raw")]
gain = [hx(k) for k in w if w[k]["normalized"] and not b.get(k, {}).get("normalized")]
rgain = [hx(k) for k in w if w[k]["raw"] and not b.get(k, {}).get("raw")]
def tm(p):
    try:
        d = json.loads(open(p).read() or "{}")
    except Exception:
        return {}
    return {k: d.get(k) for k in ("ratio", "slots_diff", "cand_bytes", "window_bytes", "normalized_equal", "raw_equal", "calls_candidate")}
print(json.dumps({"ok": True, "sha": s["summary"].get("candidate_sha256", "")[:16],
                  "normalized": sum(1 for x in w.values() if x["normalized"]),
                  "raw": sum(1 for x in w.values() if x["raw"]),
                  "losses": loss, "raw_losses": rloss[:20], "n_raw_losses": len(rloss), "gains": gain, "raw_gains": rgain,
                  "swap_hop": tm(f"{out}/hop.json"), "admin_cto": tm(f"{out}/cto.json"), "out": out}))
PY
