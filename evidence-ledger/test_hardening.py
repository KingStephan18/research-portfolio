"""Regression cases added during the portfolio's second audit."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_ledger import fixture, module

HERE = Path(__file__).resolve().parent

class HardeningTests(unittest.TestCase):
    def run_cli(self, text: str | bytes):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json'
            p.write_bytes(text if isinstance(text, bytes) else text.encode('utf-8'))
            return subprocess.run([sys.executable,str(HERE/'ledger.py'),str(p)],capture_output=True,text=True,timeout=5)

    def assert_rejected(self, result):
        self.assertEqual(result.returncode,2,result.stdout)
        self.assertEqual(result.stdout,'')
        self.assertNotIn('Traceback',result.stderr)
        self.assertNotIn('DO_NOT_ECHO',result.stderr)

    def test_surrogate_in_ignored_metadata_is_rejected(self):
        with self.assertRaises(UnicodeError):
            module().load_strict_json('{"unused": "\\ud800"}')

    def test_surrogate_in_nested_array_is_rejected(self):
        with self.assertRaises(UnicodeError):
            module().load_strict_json('{"unused": [["\\udfff"]]}')

    def test_surrogate_in_json_key_is_rejected(self):
        with self.assertRaises(UnicodeError):
            module().load_strict_json('{"\\ud800": "unused"}')

    def test_shared_origin_requires_review(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S2','relation':'supports'})
        r=module().review_dataset(d)['claims'][0]
        self.assertEqual(r['review_state'],'REVIEW_REQUIRED')
        self.assertEqual(r['supporting_origin_groups'],1)

    def test_reconstruction_with_documentary_support_requires_review(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S4','relation':'context'})
        self.assertEqual(module().review_dataset(d)['claims'][0]['review_state'],'REVIEW_REQUIRED')

    def test_conflict_keeps_priority_over_warning(self):
        d=fixture(); d['claims'][0]['evidence'] += [{'source_id':'S2','relation':'supports'},{'source_id':'S3','relation':'contradicts'}]
        self.assertEqual(module().review_dataset(d)['claims'][0]['review_state'],'CONFLICT')

    def test_duplicate_root_key_rejected(self):
        payload=json.dumps(fixture()).replace('"synthetic": true','"synthetic": false, "synthetic": true')
        self.assert_rejected(self.run_cli(payload))

    def test_duplicate_nested_key_rejected_without_echo(self):
        payload=json.dumps(fixture()).replace('"title": "Event log"','"title": "DO_NOT_ECHO", "title": "Event log"')
        self.assert_rejected(self.run_cli(payload))

    def test_nonstandard_nan_rejected(self):
        d=fixture(); d['unused']=float('nan')
        self.assert_rejected(self.run_cli(json.dumps(d)))

    def test_nonstandard_infinity_rejected(self):
        d=fixture(); d['unused']=float('inf')
        self.assert_rejected(self.run_cli(json.dumps(d)))

    def test_overflowing_numeric_literal_rejected(self):
        payload=json.dumps(fixture())[:-1]+', "unused": 1e10000}'
        self.assert_rejected(self.run_cli(payload))

    def test_unpaired_surrogate_is_safe_error(self):
        d=fixture(); d['claims'][0]['text']='DO_NOT_ECHO\ud800'
        self.assert_rejected(self.run_cli(json.dumps(d)))

    def test_invalid_utf8_is_safe_error(self):
        self.assert_rejected(self.run_cli(b'\xff\xfeDO_NOT_ECHO'))

    def test_oversized_input_is_safe_error(self):
        self.assert_rejected(self.run_cli(b' ' * 2_000_001))

    def test_empty_object_not_silently_substituted(self):
        with self.assertRaises(ValueError): module().review_dataset({})

    def test_unicode_scalar_claim_preserved(self):
        d=fixture(); d['claims'][0]['text']='Żółć — 日本語'
        r=self.run_cli(json.dumps(d))
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['claims'][0]['text'],d['claims'][0]['text'])

    def test_no_data_or_filesystem_path_in_missing_file_error(self):
        r=subprocess.run([sys.executable,str(HERE/'ledger.py'),'/missing/DO_NOT_ECHO.json'],capture_output=True,text=True)
        self.assert_rejected(r)

if __name__=='__main__': unittest.main()
