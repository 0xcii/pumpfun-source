"""`scripts/fees_donation_crank_probe.py` must report the candidate image it executed.

Sibling of open #2805 (fees social-claim differential), #2798 (fees
donation-create differential) and #2791 (fees external-codec
differential) and merged #2774 (fees sharing-create differential),
which pinned their candidate images: this script's `CrankFixture`
loads the candidate once, at construction, via
`add_program_from_file`, but `main()` reads the report's
`candidate_sha256` from the live candidate path only at the end — so
replacing the candidate file mid-run leaves the receipt attributing
the run to bytes that were never executed.

The script module itself is not imported here (it needs solders and
the LiteSVM fixture); only the pinning wiring is checked by AST, so
the test fails on base (no `pin_program` use, live path hashed at
the end) and passes with the fix. The runtime swap is not runnable
here (solders is absent).
"""

import ast
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "scripts" / "fees_donation_crank_probe.py"


def load_tree():
    return ast.parse(SCRIPT.read_text(encoding="utf-8"))


def is_pinned_candidate_call(node):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "pin_program"
        and node.args
        and isinstance(node.args[0], ast.Attribute)
        and isinstance(node.args[0].value, ast.Name)
        and node.args[0].value.id == "a"
        and node.args[0].attr == "candidate"
    )


class FeesDonationCrankPinnedImageTests(unittest.TestCase):
    def test_candidate_image_is_pinned(self):
        tree = load_tree()
        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "pump_amm_reusable_harness"
            and any(alias.name == "pin_program" for alias in node.names)
            for node in ast.walk(tree)
        )
        self.assertTrue(imported, "pin_program is not imported")

        pinned = any(is_pinned_candidate_call(node) for node in ast.walk(tree))
        self.assertTrue(pinned, "candidate path is not pinned")

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "CrankFixture"
                and node.args
                and isinstance(node.args[0], ast.Attribute)
                and isinstance(node.args[0].value, ast.Name)
                and node.args[0].value.id == "a"
                and node.args[0].attr == "candidate"
            ):
                self.fail("candidate CrankFixture is built from the live path")
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "read_bytes"
                and isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "a"
                and node.func.value.attr == "candidate"
            ):
                self.fail("report hash is read from the live candidate path")


if __name__ == "__main__":
    unittest.main()
