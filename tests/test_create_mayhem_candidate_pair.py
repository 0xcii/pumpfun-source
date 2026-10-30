"""The Mayhem-create CLI must reject partial candidates and pin both programs."""

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pump_create_mayhem_differential.py"


def parse():
    return ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))


def function(tree, name):
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def contains_call(node, name):
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == name
        for child in ast.walk(node)
    )


class CreateMayhemCandidateTests(unittest.TestCase):
    def test_run_pins_both_program_images_before_loading(self):
        tree = parse()
        self.assertTrue(
            any(
                isinstance(node, ast.ImportFrom)
                and node.module == "pump_amm_reusable_harness"
                and any(alias.name == "pin_program" for alias in node.names)
                for node in tree.body
            )
        )
        run = function(tree, "run")
        pin_lines = [
            node.lineno
            for node in ast.walk(run)
            if isinstance(node, ast.Assign) and contains_call(node.value, "pin_program")
        ]
        load_lines = [
            node.lineno
            for node in ast.walk(run)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_program_from_file"
        ]
        self.assertGreaterEqual(len(pin_lines), 2)
        self.assertTrue(load_lines)
        self.assertLess(max(pin_lines), min(load_lines))

    def test_partial_candidate_pair_is_rejected_before_cases(self):
        tree = parse()
        main = function(tree, "main")
        partial_checks = []
        candidate_pins = []
        for node in ast.walk(main):
            if isinstance(node, ast.If):
                names = {
                    child.attr
                    for child in ast.walk(node.test)
                    if isinstance(child, ast.Attribute)
                    and isinstance(child.value, ast.Name)
                    and child.value.id == "a"
                }
                if {"candidate_pump", "candidate_mayhem"} <= names:
                    errors = [
                        child
                        for child in ast.walk(node)
                        if isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                        and child.func.attr == "error"
                    ]
                    if errors:
                        partial_checks.append(node.lineno)
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "a"
                    and target.attr in {"candidate_pump", "candidate_mayhem"}
                    for target in node.targets
                )
                and contains_call(node.value, "pin_program")
            ):
                candidate_pins.append(node.lineno)
        case_loops = [
            node.lineno
            for node in ast.walk(main)
            if isinstance(node, ast.For)
            and contains_call(node.iter, "cases")
        ]
        self.assertTrue(partial_checks)
        self.assertGreaterEqual(len(candidate_pins), 2)
        self.assertTrue(case_loops)
        self.assertLess(max(partial_checks), min(case_loops))
        self.assertLess(max(candidate_pins), min(case_loops))


if __name__ == "__main__":
    unittest.main()
