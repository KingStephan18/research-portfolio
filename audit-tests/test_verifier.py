"""Verifier regressions use synthetic folders and stub only subprocess suites."""
from __future__ import annotations
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('portfolio_verifier', Path(__file__).resolve().parents[1] / 'verify.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ['evidence-ledger', 'permission-boundary']:
            (self.root / folder).mkdir()
            (self.root / folder / 'results.json').write_text('{}', encoding='utf-8')
        (self.root / 'sample.txt').write_text('public fixture', encoding='utf-8')
        self.manifest = self.root / 'SHA256SUMS.txt'
        self.lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(self.root).as_posix()
                      for p in sorted(self.root.rglob('*')) if p.is_file()]
        self.manifest.write_text('\n'.join(self.lines) + '\n', encoding='utf-8')

    def invoke(self, error=None):
        stream = io.StringIO()
        success = subprocess.CompletedProcess([], 0, stdout='{}', stderr='synthetic suite stub')
        with patch.object(mod, 'ROOT', self.root), patch.object(mod, 'run', return_value=success, side_effect=error), redirect_stdout(stream):
            try:
                status = mod.main()
            except (ValueError, OSError, subprocess.SubprocessError):
                self.fail('verifier must fail cleanly, not raise')
        return status, stream.getvalue()

    def test_valid_complete_manifest_passes(self):
        self.assertEqual(self.invoke()[0], 0)

    def test_empty_manifest_does_not_pass(self):
        self.manifest.write_text('', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

    def test_duplicate_entry_does_not_pass(self):
        self.manifest.write_text('\n'.join(self.lines + [self.lines[0]]) + '\n', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

    def test_unlisted_artifact_does_not_pass(self):
        (self.root / 'unlisted.py').write_text('# new public code\n', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

    def test_malformed_manifest_fails_cleanly(self):
        self.manifest.write_text('not-a-manifest-line\n', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

    def test_mismatched_hash_fails(self):
        (self.root / 'sample.txt').write_text('changed', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

    def test_missing_manifest_fails(self):
        self.manifest.unlink()
        self.assertEqual(self.invoke()[0], 1)

    def test_manifest_symlink_is_rejected(self):
        copy = self.root / 'other-manifest.txt'
        copy.write_bytes(self.manifest.read_bytes())
        self.manifest.unlink()
        try:
            self.manifest.symlink_to(copy)
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        self.assertEqual(self.invoke()[0], 1)

    def test_timeout_fails_without_private_error_text(self):
        status, text = self.invoke(subprocess.TimeoutExpired('PRIVATE_COMMAND_SENTINEL', 60))
        self.assertEqual(status, 1)
        self.assertNotIn('PRIVATE_COMMAND_SENTINEL', text)

    def test_local_environment_and_venv_are_not_artifacts(self):
        (self.root / '.env').write_text('PRIVATE_FIXTURE_ONLY', encoding='utf-8')
        (self.root / '.venv').mkdir()
        (self.root / '.venv' / 'local.py').write_text('# local environment', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 0)

    def test_manifest_cannot_include_local_environment(self):
        local = self.root / '.env'
        local.write_text('PRIVATE_FIXTURE_ONLY', encoding='utf-8')
        self.manifest.write_text('\n'.join(self.lines + [hashlib.sha256(local.read_bytes()).hexdigest() + '  .env']) + '\n', encoding='utf-8')
        self.assertEqual(self.invoke()[0], 1)

if __name__ == '__main__':
    unittest.main()
