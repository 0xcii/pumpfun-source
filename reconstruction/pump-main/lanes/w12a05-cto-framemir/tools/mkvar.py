#!/usr/bin/env python3
"""mkvar.py <name> : crate copy var/<name> with edits from edits/<name>.py (EDITS=[(old,new),...], line count kept)"""
import sys, subprocess, runpy
from pathlib import Path
OUT=Path('/Users/shawwalters/.cache/pumpfun-reconstruction/lanes/w12a05-cto-framemir')
WT=Path('/Users/shawwalters/Documents/Codex/2026-10-24/pump-main-swarm/worktrees/w12a05-cto-framemir')
name=sys.argv[1]; base=Path(sys.argv[2]) if len(sys.argv)>2 else WT/'programs/pump'
d=OUT/'var'/name
subprocess.run(['rsync','-a','--delete','--exclude','target',str(base)+'/',str(d)+'/'],check=True)
f=d/'src/creator/admin_cto.rs'; t=f.read_text(); n0=t.count('\n')
ns=runpy.run_path(str(OUT/'edits'/(name+'.py')))
for old,new in ns['EDITS']:
    c=t.count(old)
    assert c==1, f'edit not unique ({c}): {old[:80]!r}'
    t=t.replace(old,new)
assert t.count('\n')==n0, 'line count changed'
f.write_text(t); print('ok',d)
