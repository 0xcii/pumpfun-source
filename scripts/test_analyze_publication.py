"""Atomic publication checks for analyze.py's paired evidence reports."""
import tempfile
import unittest
from pathlib import Path

import analyze


class AnalyzePublicationTests(unittest.TestCase):
    def test_missing_second_parent_does_not_replace_first_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / 'binary-analysis.json'
            second = root / 'missing/interface-inventory.json'
            first.write_text('prior\n', encoding='utf-8')

            with self.assertRaises(FileNotFoundError):
                analyze.publish_reports([(first, 'replacement\n'), (second, 'new\n')])

            self.assertEqual(first.read_text(encoding='utf-8'), 'prior\n')
            self.assertFalse(second.exists())


if __name__ == '__main__':
    unittest.main()
