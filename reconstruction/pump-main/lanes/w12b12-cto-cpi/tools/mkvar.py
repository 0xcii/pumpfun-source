#!/usr/bin/env python3
"""mkvar.py <name>[+<name>...] : crate copy of $WT/programs/pump with variant edits on admin_cto.rs -> $OUT/var/<combo>"""
import sys, os, subprocess, json
WT='/Users/shawwalters/Documents/Codex/2026-10-24/pump-main-swarm/worktrees/w12b12-cto-cpi'
OUT='/Users/shawwalters/.cache/pumpfun-reconstruction/lanes/w12b12-cto-cpi'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cpi_variants import V
combo=sys.argv[1]
base=sys.argv[2] if len(sys.argv)>2 else WT+'/programs/pump'
dst=f'{OUT}/var/{combo}'
subprocess.run(['rsync','-a','--delete','--exclude','target',base+'/',dst+'/'],check=True)
p=dst+'/src/creator/admin_cto.rs'
t=open(p).read(); n0=t.count('\n')
for name in combo.split('+'):
    name=name[3:] if name.startswith('m2_') else name
    for old,new in V[name]:
        c=t.count(old)
        if c!=1: sys.exit(f'{name}: old occurs {c} times: {old[:80]!r}')
        t=t.replace(old,new)
assert t.count('\n')==n0, 'line count changed'
open(p,'w').write(t)
print(dst)
