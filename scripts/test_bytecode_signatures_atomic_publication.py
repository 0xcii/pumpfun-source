"""Bytecode-signature packets are staged before their final publication."""
import contextlib
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import bytecode_signatures as tool


def generate(output):
    with mock.patch.object(sys, 'argv', [
            'bytecode_signatures.py', '--output', str(output)]), \
            contextlib.redirect_stdout(io.StringIO()):
        tool.main()


def packet_hashes(output):
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in output.iterdir()
    }


class BytecodeSignaturesAtomicPublicationTests(unittest.TestCase):
    def test_late_write_failure_leaves_no_partial_new_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'packet'
            real_write_text = Path.write_text

            def fail_readme(path, *args, **kwargs):
                if path.name == 'README.md':
                    raise OSError('injected README write failure')
                return real_write_text(path, *args, **kwargs)

            with mock.patch.object(Path, 'write_text', fail_readme):
                with self.assertRaisesRegex(OSError, 'injected README write failure'):
                    generate(output)

            self.assertFalse(output.exists(), 'failed analysis published a partial packet')
            self.assertEqual(list(output.parent.glob('.packet.staging-*')), [])

    def test_failed_regeneration_preserves_prior_complete_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'packet'
            generate(output)
            before = packet_hashes(output)
            real_write_text = Path.write_text

            def fail_top_ngrams(path, *args, **kwargs):
                if path.name == 'top-ngrams.json':
                    raise OSError('injected regeneration write failure')
                return real_write_text(path, *args, **kwargs)

            with mock.patch.object(Path, 'write_text', fail_top_ngrams):
                with self.assertRaisesRegex(OSError, 'injected regeneration write failure'):
                    generate(output)

            self.assertEqual(packet_hashes(output), before)
            self.assertEqual(list(output.parent.glob('.packet.staging-*')), [])


if __name__ == '__main__':
    unittest.main()
