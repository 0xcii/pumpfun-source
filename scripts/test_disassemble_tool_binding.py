#!/usr/bin/env python3
"""Analyst disassembly runs the exact tool and input bytes its manifest hashes.

The fake objdump replaces itself with a different tool the first time it
disassembles. A run that hashes the tool once but executes it by path
afterwards publishes later outputs produced by the replacement under the
original tool's hash; a run bound to one snapshot produces every output
with the hashed tool.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "disassemble.py"
SWAPPING_OBJDUMP = """#!{python}
import pathlib, sys
if sys.argv[1] == "--version":
    print("fake objdump 1.0")
else:
    pathlib.Path(sys.argv[0]).write_text(REPLACEMENT)
    print("disassembly by v1")
"""
REPLACEMENT = """#!{python}
import sys
if sys.argv[1] == "--version":
    print("fake objdump 2.0")
else:
    print("DISASSEMBLY BY V2")
"""


class DisassembleToolBindingTests(unittest.TestCase):
    def test_outputs_come_from_the_hashed_tool(self):
        with tempfile.TemporaryDirectory() as temporary:
            objdump = Path(temporary) / "objdump"
            objdump.write_text(SWAPPING_OBJDUMP.format(python=sys.executable)
                               .replace("REPLACEMENT", repr(REPLACEMENT.format(python=sys.executable))))
            os.chmod(objdump, 0o755)
            tool_sha256 = hashlib.sha256(objdump.read_bytes()).hexdigest()
            output = Path(temporary) / "asm"
            completed = subprocess.run([sys.executable, "-B", str(SCRIPT), "--objdump", str(objdump),
                                        "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["tool_sha256"], tool_sha256)
            self.assertEqual(manifest["version"], "fake objdump 1.0\n")
            self.assertEqual(sorted(manifest["outputs"]), ["mayhem", "pump", "pump_amm", "pump_fees"])
            for name in manifest["outputs"]:
                self.assertEqual((output / f"{name}.asm").read_text(), "disassembly by v1\n")


if __name__ == "__main__":
    unittest.main()
