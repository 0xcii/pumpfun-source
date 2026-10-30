#!/usr/bin/env python3
"""Event normalization must reject truncated CPI events, not zero-pad them.

bytearray slice assignment past the end appends: without a length check, a
truncated original event and a full candidate event both normalized to the
same zero-padded bytes, hiding the mismatch. The buy_v2 drivers already assert
the extent (pump_buy_v2_surfpool.py); the migrate/exact-quote/holder/v3
drivers now do the same. The drivers run at import, so each function is
loaded directly from its source tree via ast.
"""
import ast
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
DRIVERS = (
    "pump_migrate_surfpool.py",
    "pump_holder_distribution_surfpool.py",
    "pump_exact_quote_surfpool.py",
    "pump_v3_configured_fee_surfpool.py",
)


def load_normalize_event(name):
    source = (SCRIPTS / name).read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "normalize_event")
    module = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), name, "exec"), module)
    return module["normalize_event"]


class TruncatedEventNormalizationTests(unittest.TestCase):
    KEY = b"\x01" * 8

    def test_full_event_keeps_its_length_and_zeroes_the_timestamp(self):
        for name in DRIVERS:
            with self.subTest(driver=name):
                normalize = load_normalize_event(name)
                data = self.KEY + b"\x02" * 16
                out = normalize(data, {self.KEY: 16})
                self.assertEqual(len(out), 24)
                self.assertEqual(out[16:24], bytes(8))
                self.assertEqual(out[:16], data[:16])

    def test_truncated_event_is_rejected(self):
        for name in DRIVERS:
            with self.subTest(driver=name):
                normalize = load_normalize_event(name)
                data = self.KEY + b"\x02" * 12  # timestamp field absent
                with self.assertRaisesRegex(AssertionError, "truncated event"):
                    normalize(data, {self.KEY: 16})


if __name__ == "__main__":
    unittest.main()
