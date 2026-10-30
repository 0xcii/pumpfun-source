#!/usr/bin/env python3
"""pfboard.py <unstripped.so>...: rank admin_cto candidates by perfect-frame ratio (code closeness with
the frame factored out) next to the plain ratio and size. JSON lines on stdout."""
import json, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))

def one(p):
    import ctoracle, framebound
    try:
        ctok, n = ctoracle.so_tokens(p)
        r0, r1, _ = framebound.bound(ctok)
        return {'so': p, 'bytes': n, 'ratio': r0, 'pf': r1}
    except Exception as e:  # noqa
        return {'so': p, 'error': repr(e)[:120]}

if __name__ == '__main__':
    with ProcessPoolExecutor(4) as ex:
        for r in ex.map(one, sys.argv[1:]):
            print(json.dumps(r), flush=True)
