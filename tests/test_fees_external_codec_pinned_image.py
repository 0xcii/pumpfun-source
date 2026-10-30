"""`scripts/fees_external_codec_differential.py` must execute one candidate image per run.

Sibling of merged #2774 (fees sharing create differential), open
#2782 (fees sharing update differential) and #2765 (fees admin_cto
differential) and merged #2722, which pinned their candidate images.
Merged #2774 already pins the load inside `sharing.run()` itself, so
the remaining gap in this script is at its own boundary: `main()`
still passes the live candidate/baseline paths in, and reads the
report's `candidate_sha256` (and `baseline_sha256`) from those live
paths only at the end — so replacing the candidate file mid-run
leaves the receipt attributing the run to bytes that were never
executed. Pinning at this boundary makes the receipt match the
snapshots actually executed.

The script module itself is not imported here (it needs solders and
the LiteSVM fixture); only the pinning wiring is checked by AST, so
the test fails on base (no `pin_program` use, live paths passed to
`sharing.run` and to the report hash) and passes with the fix. The
runtime swap is not runnable here (solders is absent).
"""

import ast
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "scripts" / "fees_external_codec_differential.py"


def load_tree():
    return ast.parse(SCRIPT.read_text(encoding="utf-8"))


def is_live_path(node, attr):
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "a"
        and node.attr == attr
    )


class FeesExternalCodecPinnedImageTests(unittest.TestCase):
    def test_candidate_and_baseline_images_are_pinned(self):
        tree = load_tree()
        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "pump_amm_reusable_harness"
            and any(alias.name == "pin_program" for alias in node.names)
            for node in ast.walk(tree)
        )
        self.assertTrue(imported, "pin_program is not imported")

        pinned_args = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "pin_program"
                and node.args
                and isinstance(node.args[0], ast.Attribute)
            ):
                pinned_args.add(node.args[0].attr)
        self.assertIn("candidate", pinned_args, "candidate path is not pinned")
        self.assertIn("baseline", pinned_args, "baseline path is not pinned")

        # sharing.run() must never receive a live candidate/baseline path.
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and len(node.args) >= 2
            ):
                self.assertFalse(
                    is_live_path(node.args[1], "candidate"),
                    "sharing.run receives the live candidate path",
                )
                self.assertFalse(
                    is_live_path(node.args[1], "baseline"),
                    "sharing.run receives the live baseline path",
                )

        # The report hashes must not be read from the live paths either.
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "sha"
                and node.args
            ):
                self.assertFalse(
                    is_live_path(node.args[0], "candidate"),
                    "report hash is read from the live candidate path",
                )
                self.assertFalse(
                    is_live_path(node.args[0], "baseline"),
                    "report hash is read from the live baseline path",
                )


if __name__ == "__main__":
    unittest.main()
