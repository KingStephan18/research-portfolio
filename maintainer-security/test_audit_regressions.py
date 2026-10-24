"""Regression tests for read-only input handling; no external workflows run."""
from __future__ import annotations
import importlib.util
import io
from contextlib import nullcontext
from types import SimpleNamespace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('workflow_audit', Path(__file__).with_name('workflow_review.py'))
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class InputBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root / '.github' / 'workflows'
        self.folder.mkdir(parents=True)
        self.file = self.folder / 'ci.yml'
        self.file.write_text('permissions: {}\n', encoding='utf-8')

    def assess_without_exception(self):
        try:
            return mod.audit_root(self.root)
        except OSError:
            self.fail('filesystem failures must produce NOT_ASSESSED, not a traceback')

    def test_directory_permission_failure_is_sanitized(self):
        with patch('os.scandir', side_effect=PermissionError('PRIVATE_PATH_SENTINEL')):
            result, status = self.assess_without_exception()
        self.assertEqual((result['outcome'], status), ('NOT_ASSESSED', 2))
        self.assertNotIn('PRIVATE_PATH_SENTINEL', str(result))

    def test_workflow_metadata_failure_is_sanitized(self):
        original = Path.stat
        def denied(path, *args, **kwargs):
            if path == self.file:
                raise PermissionError('PRIVATE_PATH_SENTINEL')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'stat', denied):
            result, status = self.assess_without_exception()
        self.assertEqual((result['outcome'], status), ('NOT_ASSESSED', 2))
        self.assertNotIn('PRIVATE_PATH_SENTINEL', str(result))

    def test_actual_read_is_bounded_even_if_file_grew(self):
        reads = []
        class GrowingStream(io.BytesIO):
            def read(self, size=-1):
                reads.append(size)
                return super().read(size)
        stream = GrowingStream(b'x' * (mod.MAX_FILE_BYTES + 20))
        with patch.object(Path, 'open', return_value=stream):
            result, status = mod.audit_root(self.root)
        self.assertEqual((result['error'], status), ('FILE_TOO_LARGE', 2))
        self.assertEqual(reads, [mod.MAX_FILE_BYTES + 1])

    def test_enumeration_stops_at_workflow_limit(self):
        def entries():
            for index in range(mod.MAX_FILES + 1):
                yield SimpleNamespace(name=f'{index}.yml', path=str(self.folder / f'{index}.yml'))
            self.fail('enumeration continued after the workflow limit')
        with patch('os.scandir', return_value=nullcontext(entries())):
            result, status = mod.audit_root(self.root)
        self.assertEqual((result['error'], status), ('TOO_MANY_FILES', 2))

    def test_nonworkflow_enumeration_is_bounded(self):
        def entries():
            for index in range(1001):
                yield SimpleNamespace(name=f'{index}.txt', path=str(self.folder / f'{index}.txt'))
            self.fail('directory enumeration exceeded the total-entry bound')
        with patch('os.scandir', return_value=nullcontext(entries())):
            result, status = mod.audit_root(self.root)
        self.assertEqual((result['error'], status), ('TOO_MANY_ENTRIES', 2))

if __name__ == '__main__':
    unittest.main()
