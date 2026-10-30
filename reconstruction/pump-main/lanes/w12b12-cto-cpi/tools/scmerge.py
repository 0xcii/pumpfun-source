#!/usr/bin/env python3
"""scmerge.py: StackColoring merge trace for one function, named by alloca (about 5 s, no build slot).

  scmerge.py --ll module.ll --sym 'admin_cto7execute' [--edit edit.py] [--slot NAME ...] [--out DIR]

Extracts the function with the debug build's llvm-extract (so llc runs on a 0.3 MB module, not the
42 MB crate module), optionally applies edit(fn_module_text)->text, runs the debug llc with the
fastbuild flags plus -debug-only=stack-coloring and prints:
  - every StackColoring group: representative slot (frame index, size, IR name) and its members;
  - for each --slot NAME: the group it ended in, and whether it is a representative.
The extracted module compiles to the same bytes as the full module (checked on admin_cto at main
20a1ae9: SDK llc 27,400 B, identical disassembly to the debug llc).
Use it to test which IR shape lets one alloca merge into another (for example the wallet emit_cpi!
signer slice %_117.i74 into a 24 B target piece), before looking for the source form.
"""
import argparse, os, re, runpy, subprocess, sys, tempfile
from collections import defaultdict
DBG = os.path.expanduser('~/.cache/pumpfun-reconstruction/llvm-dbg/build/bin')
FLAGS = ['-O3', '-relocation-model=pic', '-mattr=+store-imm,+jmp-ext']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ll', required=True); ap.add_argument('--sym', required=True)
    ap.add_argument('--edit'); ap.add_argument('--slot', action='append', default=[])
    ap.add_argument('--out', default=tempfile.mkdtemp(prefix='scmerge-'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m = re.search(r'define [^\n]*@(\S*' + a.sym + r'\S*)\(', open(a.ll).read())
    if not m: sys.exit('no function matching ' + a.sym)
    sym = m.group(1)
    ext = os.path.join(a.out, 'fn.ll')
    subprocess.run([DBG + '/llvm-extract', '-S', '-func=' + sym, a.ll, '-o', ext], check=True)
    if a.edit:
        t = open(ext).read(); t2 = runpy.run_path(a.edit)['edit'](t)
        if t2 == t: sys.exit('edit changed nothing')
        open(ext, 'w').write(t2)
    r = subprocess.run([DBG + '/llc'] + FLAGS + [ext, '-filetype=obj', '-o', os.path.join(a.out, 'fn.o'),
                        '-debug-only=stack-coloring'], capture_output=True, text=True)
    log = r.stderr; open(os.path.join(a.out, 'sc.log'), 'w').write(log)
    if r.returncode: sys.exit(log[-2000:])
    name = {}
    for x in re.finditer(r'slot #(\d+) with allocation: (\S+)', log): name[int(x.group(1))] = x.group(2)
    size = {int(x.group(1)): int(x.group(2)) for x in re.finditer(r'^Slot #(\d+) - (\d+) bytes\.', log, re.M)}
    rep, members = {}, defaultdict(list)
    for x in re.finditer(r'Merging #(\d+) and slots #(\d+) together', log):
        i, j = int(x.group(1)), int(x.group(2)); rep[j] = i; members[i].append(j)
    groups = sorted(members, key=lambda i: (-size.get(i, 0), i))
    for i in groups:
        print(f'#{i:<4d} {size.get(i,0):5d} B {name.get(i,"?"):24s} <- ' +
              ' '.join(f'{name.get(j,"?")}#{j}/{size.get(j,0)}' for j in members[i]))
    for s in a.slot:
        ids = [k for k, v in name.items() if v == s]
        for k in ids:
            print(f'slot {s} #{k} ({size.get(k,0)} B): ' + (f'merged into #{rep[k]} {name.get(rep[k],"?")}' if k in rep
                  else ('representative of ' + str(len(members.get(k, []))) + ' members' if k in members else 'alone')))
    print('trace:', os.path.join(a.out, 'sc.log'))

if __name__ == '__main__':
    main()
