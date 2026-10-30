"""One byte snapshot per program path for the whole run.

A differential that loads its candidate path again for every case, then hashes
the path when it writes the report, can execute two images under one receipt if
the file changes during the run. pin_program copies the bytes once; every load
and every report hash then reads the private copy.
"""
import atexit
import os
from pathlib import Path
import shutil
import tempfile

_pinned = {}
def pin_program(path):
    """Return a private copy of one byte snapshot of path, the same for the whole run."""
    # Key the path as given: resolving symlinks would re-pin a retargeted link.
    key = os.path.abspath(path)
    if key not in _pinned:
        directory = tempfile.mkdtemp(prefix='pump-amm-pinned-')
        atexit.register(shutil.rmtree, directory, True)
        snapshot = Path(directory) / 'program.so'
        snapshot.write_bytes(Path(key).read_bytes())
        _pinned[key] = snapshot
    return _pinned[key]
