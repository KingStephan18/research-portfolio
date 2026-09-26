"""Tests for a deterministic reference checker; no model/API calls."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def module():
    path = HERE / 'ledger.py'
    if not path.exists():
        raise AssertionError('ledger.py implementation is not present')
    spec = importlib.util.spec_from_file_location('ledger', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def fixture():
    return {
      'schema_version': 1,
      'synthetic': True,
      'sources': [
        {'id':'S1','title':'Event log','origin_group':'O1','kind':'primary'},
        {'id':'S2','title':'Copied report','origin_group':'O1','kind':'secondary'},
        {'id':'S3','title':'Independent log','origin_group':'O2','kind':'primary'},
        {'id':'S4','title':'Illustrative reconstruction','origin_group':'O3','kind':'reconstruction'},
      ],
      'claims': [{'id':'C1','text':'A sample claim','evidence':[{'source_id':'S1','relation':'supports'}]}]
    }

class LedgerTests(unittest.TestCase):
    def review(self, data=None):
        return module().review_dataset(data or fixture())
    def test_traceable_is_not_a_truth_verdict(self):
        r=self.review()['claims'][0]
        self.assertEqual(r['review_state'],'TRACEABLE')
        self.assertIsNone(r['truth_verdict'])
    def test_counts_shared_origin_once(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S2','relation':'supports'})
        r=self.review(d)['claims'][0]
        self.assertEqual(r['supporting_origin_groups'],1)
        self.assertIn('SHARED_ORIGIN',r['flags'])
    def test_counts_independent_origins(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S3','relation':'supports'})
        self.assertEqual(self.review(d)['claims'][0]['supporting_origin_groups'],2)
    def test_conflict_is_not_automatically_resolved(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S3','relation':'contradicts'})
        self.assertEqual(self.review(d)['claims'][0]['review_state'],'CONFLICT')
    def test_contradiction_only_requires_review(self):
        d=fixture(); d['claims'][0]['evidence'][0]['relation']='contradicts'
        self.assertEqual(self.review(d)['claims'][0]['review_state'],'REVIEW_REQUIRED')
    def test_unsourced_claim(self):
        d=fixture(); d['claims'][0]['evidence']=[]
        self.assertEqual(self.review(d)['claims'][0]['review_state'],'UNSOURCED')
    def test_context_does_not_count_as_support(self):
        d=fixture(); d['claims'][0]['evidence'][0]['relation']='context'
        r=self.review(d)['claims'][0]
        self.assertEqual(r['review_state'],'UNSOURCED')
        self.assertEqual(r['supporting_origin_groups'],0)
    def test_reconstruction_does_not_count_as_documentary_support(self):
        d=fixture(); d['claims'][0]['evidence']=[{'source_id':'S4','relation':'supports'}]
        r=self.review(d)['claims'][0]
        self.assertEqual(r['review_state'],'REVIEW_REQUIRED')
        self.assertEqual(r['supporting_origin_groups'],0)
        self.assertIn('RECONSTRUCTION',r['flags'])
    def test_reconstruction_does_not_create_documentary_conflict(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S4','relation':'contradicts'})
        r=self.review(d)['claims'][0]
        # A reconstruction is not a documentary conflict, but requires review.
        self.assertEqual(r['review_state'],'REVIEW_REQUIRED')
        self.assertIn('RECONSTRUCTION',r['flags'])
    def test_input_is_not_mutated(self):
        d=fixture(); before=copy.deepcopy(d); self.review(d); self.assertEqual(d,before)
    def test_deterministic(self):
        self.assertEqual(self.review(),self.review())
    def test_unknown_source_rejected(self):
        d=fixture(); d['claims'][0]['evidence'][0]['source_id']='NOPE'
        with self.assertRaises(ValueError): self.review(d)
    def test_duplicate_source_rejected(self):
        d=fixture(); d['sources'].append(copy.deepcopy(d['sources'][0]))
        with self.assertRaises(ValueError): self.review(d)
    def test_duplicate_claim_rejected(self):
        d=fixture(); d['claims'].append(copy.deepcopy(d['claims'][0]))
        with self.assertRaises(ValueError): self.review(d)
    def test_duplicate_evidence_rejected(self):
        d=fixture(); d['claims'][0]['evidence']*=2
        with self.assertRaises(ValueError): self.review(d)
    def test_same_source_opposing_relations_rejected(self):
        d=fixture(); d['claims'][0]['evidence'].append({'source_id':'S1','relation':'contradicts'})
        with self.assertRaises(ValueError): self.review(d)
    def test_bad_relation_rejected(self):
        d=fixture(); d['claims'][0]['evidence'][0]['relation']='proves'
        with self.assertRaises(ValueError): self.review(d)
    def test_bad_source_kind_rejected(self):
        d=fixture(); d['sources'][0]['kind']='ground_truth'
        with self.assertRaises(ValueError): self.review(d)
    def test_empty_origin_rejected(self):
        d=fixture(); d['sources'][0]['origin_group']=' '
        with self.assertRaises(ValueError): self.review(d)
    def test_nonstring_claim_rejected(self):
        d=fixture(); d['claims'][0]['text']=123
        with self.assertRaises(ValueError): self.review(d)
    def test_nonlist_evidence_rejected(self):
        d=fixture(); d['claims'][0]['evidence']='S1'
        with self.assertRaises(ValueError): self.review(d)
    def test_missing_schema_rejected(self):
        d=fixture(); d.pop('schema_version')
        with self.assertRaises(ValueError): self.review(d)
    def test_boolean_schema_rejected(self):
        d=fixture(); d['schema_version']=True
        with self.assertRaises(ValueError): self.review(d)
    def test_non_synthetic_input_rejected_for_demo(self):
        d=fixture(); d['synthetic']=False
        with self.assertRaises(ValueError): self.review(d)
    def test_invalid_root_rejected(self):
        with self.assertRaises(ValueError): module().review_dataset([])
    def test_cli_valid_json(self):
        module()
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'input.json'; p.write_text(json.dumps(fixture()))
            r=subprocess.run([sys.executable,str(HERE/'ledger.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(r.stdout)['claim_count'],1)
    def test_cli_malformed_json_returns_safe_error(self):
        module()
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json'; p.write_text('{')
            r=subprocess.run([sys.executable,str(HERE/'ledger.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2)
            self.assertNotIn('Traceback',r.stderr)
    def test_cli_missing_file_returns_safe_error(self):
        module()
        r=subprocess.run([sys.executable,str(HERE/'ledger.py'),'not-present.json'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertNotIn('Traceback',r.stderr)

if __name__ == '__main__': unittest.main()
