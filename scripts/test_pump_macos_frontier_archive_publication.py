#!/usr/bin/env python3
"""Reject retained archive aliases before downloading macOS toolchain inputs."""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pump_macos_frontier_qualification as target  # noqa: E402


class MacosFrontierArchivePublicationTests(unittest.TestCase):
    def test_symlinked_archive_is_rejected_before_its_target_is_modified(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            work = root / "work"
            work.mkdir()
            external = root / "external-toolchain.tar"
            external.write_bytes(b"external retained bytes\n")
            archive = work / "fixture.tar.bz2"
            archive.symlink_to(external)
            spec = root / "inputs.json"
            spec.write_text(json.dumps({
                "archives": {
                    "fixture": {
                        "url": "https://example.invalid/tool.tar",
                        "sha256": "0" * 64,
                    },
                },
            }), encoding="utf-8")

            with mock.patch.object(target, "OUT", work), \
                    mock.patch.object(target, "EVIDENCE", work / "evidence"), \
                    mock.patch.object(target, "SPEC", spec), \
                    mock.patch.object(target.platform, "system", return_value="Darwin"), \
                    mock.patch.object(target.platform, "machine", return_value="arm64"), \
                    mock.patch.object(target.subprocess, "check_output",
                                      return_value="test-revision\n"), \
                    mock.patch.object(target.urllib.request, "urlopen",
                                      return_value=io.BytesIO(b"synthetic download")):
                with self.assertRaisesRegex(FileExistsError, "retained archive"):
                    target.main()

            self.assertEqual(external.read_bytes(), b"external retained bytes\n")
            self.assertTrue(archive.is_symlink())


if __name__ == "__main__":
    unittest.main()
