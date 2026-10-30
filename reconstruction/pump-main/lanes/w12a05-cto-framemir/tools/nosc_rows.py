#!/usr/bin/env python3
"""nosc_rows.py <fo_dir_with_nosc/mir.txt and nosc/m.o> : per-alloca implied orig T from the -no-stack-coloring llc run"""
import sys, re, collections, importlib.util
from pathlib import Path
FO=str(__import__('pathlib').Path(__file__).resolve().parents[2]/'w4-frame-oracle/frameoracle.py')
spec=importlib.util.spec_from_file_location('fo',FO); fo=importlib.util.module_from_spec(spec); spec.loader.exec_module(fo)
d=Path(sys.argv[1]); sym=sys.argv[2] if len(sys.argv)>2 else None
text=(d/'nosc/mir.txt').read_text()
dumps=fo.split_dumps(text)
before=dumps[('Before','stack-coloring')]
names,lt=fo.names_and_marks(before)
fin=fo.frame_objects(dumps[('After','prologepilog')])
# candidate bytes: extract from nosc/m.o
import subprocess
o=d/'nosc/m.o'
t=subprocess.check_output([str(fo.SDK/'llvm-readelf'),'-sSW',str(o)],text=True)
secs={}
for l in t.splitlines():
    m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)',l)
    if m: secs[int(m.group(1))]=(m.group(2),int(m.group(3),16))
blob=o.read_bytes(); cand=None
for l in t.splitlines():
    f=l.split()
    if len(f)>=8 and f[3]=='FUNC' and 'admin_cto7execute17' in f[-1]:
        val,size,ndx=int(f[1],16),int(f[2]),int(f[6]); off=secs[ndx][1]; cand=blob[off+val:off+val+size]
sc=fo.load_score(); W={x['start']:x for x in sc.original_windows()}; orig=W[0x22a10]['raw']
class A: minv=2
rep=fo.analyze(orig,cand,fin,names,lt,{},d,A())
for r in rep['rows']:
    if r['fi']<0: continue
    print(f"fi{r['fi']:<4} T={r['T']:#7x} sz={r['size']:<4} al={r['align']} orig={'?' if r['orig'] is None else hex(r['orig']):>7} votes={r['votes']}/{r['tot']} lt={r['lt']} {r['name']}")
