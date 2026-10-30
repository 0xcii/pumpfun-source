#!/usr/bin/env python3
"""Lane-local capture (experiment copies only): build a crate copy with the identity recipe and
--emit=link,llvm-ir,mir, then copy pump_recovered.{ll,mir} into <out>.  Extra args are passed as
-C llvm-args=<v>.  Never used for proposals.

usage: capmir.py <crate_copy> <work> <out> [llvm-arg ...]
"""
import sys, subprocess, json, shutil
from pathlib import Path
H = Path(__file__).resolve().parents[4] / 'harness'
sys.path.insert(0, str(H)); import fastbuild
src, work, out = map(Path, sys.argv[1:4]); llvm = sys.argv[4:]
real = fastbuild.run_compiler
def hook(cmd, *a, **k):
    if isinstance(cmd, list) and len(cmd) > 1 and str(cmd[0]).endswith('/cargo') and cmd[1] == 'build':
        cmd = cmd[:]; cmd[1] = 'rustc'
        cmd += ['--lib', '--', '--emit=link,llvm-ir,mir'] + [x for v in llvm for x in ('-C', 'llvm-args=' + v)]
    return real(cmd, *a, **k)
fastbuild.run_compiler = hook
try:
    r = fastbuild.build(src, work, out, recipe='identity')
finally:
    fastbuild.run_compiler = real
if r.get('ok'):
    d = work / 'target-identity/sbpf-solana-solana/release/deps'
    for ext in ('ll', 'mir'):
        p = d / f'pump_recovered.{ext}'
        if p.exists():
            shutil.copy2(p, out / f'pump_recovered.{ext}')
print(json.dumps(r, indent=1))
