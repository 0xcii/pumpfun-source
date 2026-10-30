#!/usr/bin/env python3
"""framesim.py <fo_dir> [ops...]: frame what-if with the ratio it would give.
Reads <fo_dir>/mir.txt (llc dumps) and <fo_dir>/fn.bin (our function bytes), re-lays-out the frame after
applying ops, remaps every r10 access (object-relative) and prints the masked-exact ratio vs the original.
ops:  mv:FI:BEFORE_FI   move object FI just before BEFORE_FI
      sz:FI:SIZE[:ALIGN] resize
      ins:BEFORE_FI:SIZE[:ALIGN]  insert a new object
      del:FI            delete object FI (its accesses then map into object INTO if given del:FI:INTO)
"""
import sys, re, difflib, importlib.util
from pathlib import Path
FO=str(__import__('pathlib').Path(__file__).resolve().parents[2]/'w4-frame-oracle/frameoracle.py')
spec=importlib.util.spec_from_file_location('fo',FO); fo=importlib.util.module_from_spec(spec); spec.loader.exec_module(fo)
d=Path(sys.argv[1]); ops=sys.argv[2:]
dumps=fo.split_dumps((d/'mir.txt').read_text())
fin=fo.frame_objects(dumps[('After','prologepilog')])
cand=(d/'fn.bin').read_bytes()
sc=fo.load_score(); W={x['start']:x for x in sc.original_windows()}; orig=W[0x22a10]['raw']
live={fi:x for fi,x in fin.items() if fi>=0 and not x['dead']}
seq=[[fi,live[fi]['size'],live[fi]['align']] for fi in sorted(live)]
oldT={fi:-live[fi]['loc'] for fi in live}
into={}
for op in ops:
    p=op.split(':')
    if p[0]=='mv':
        a,b=int(p[1]),int(p[2]); it=next(x for x in seq if x[0]==a); seq.remove(it)
        j=next(k for k,x in enumerate(seq) if x[0]==b); seq.insert(j,it)
    elif p[0]=='sz':
        it=next(x for x in seq if x[0]==int(p[1])); it[1]=int(p[2]); 
        if len(p)>3: it[2]=int(p[3])
    elif p[0]=='ins':
        j=next(k for k,x in enumerate(seq) if x[0]==int(p[1])); seq.insert(j,[f'n{len(seq)}',int(p[2]),int(p[3]) if len(p)>3 else 8])
    elif p[0]=='del':
        a=int(p[1]); seq=[x for x in seq if x[0]!=a]
        if len(p)>2: into[a]=int(p[2])
T=0; newT={}
for fi,s,a in seq:
    T=T+s; T=(T+a-1)//a*a; newT[fi]=T
spans=sorted((oldT[fi],live[fi]['size'],fi) for fi in live)
def obj(c):
    for t,s,fi in spans:
        if t-s<c<=t: return fi,t
    return None
def remap(c):
    o=obj(c)
    if not o: return c
    fi,t=o
    if fi in into:
        tgt=into[fi]; return c-t+newT[tgt]
    if fi not in newT: return c
    return c+(newT[fi]-t)
b=bytearray(cand)
for x in fo.decode(cand):
    i=x['i']; op=x['op']; cls=op&7; dst=x['dst']; src=x['src']
    base=src if cls==1 else dst
    if cls in (1,2,3) and base==10 and x['off']<0:
        no=-remap(-x['off']); b[i+2:i+4]=int(no).to_bytes(2,'little',signed=True)
    # mov rX,r10 ; add rX,-imm
    if op==0x07 and x['imm']<0 and i>=8:
        p=fo.decode(cand[i-8:i])[0]
        if p['op']==0xbf and p['src']==10 and p['dst']==dst:
            ni=-remap(-x['imm']); b[i+4:i+8]=int(ni).to_bytes(4,'little',signed=True)
def mtok(raw): return [fo.norm_calls(raw[x['i']:x['i']+x['k']]) for x in fo.decode(raw)]
r0=difflib.SequenceMatcher(None,mtok(orig),mtok(cand),autojunk=False).ratio()
r1=difflib.SequenceMatcher(None,mtok(orig),mtok(bytes(b)),autojunk=False).ratio()
print(f'base {r0:.5f} -> what-if {r1:.5f}  ({" ".join(ops)})  frame end {T:#x} (was {max(oldT.values()):#x})')
