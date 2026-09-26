#!/usr/bin/env python3
"""Run the fixed synthetic decision scenarios; no external actions are taken."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from guard import authorize, action_only_baseline

HERE=Path(__file__).resolve().parent

def run() -> dict:
    packet=json.loads((HERE/'scenarios.json').read_text(encoding='utf-8'))
    if packet.get('synthetic') is not True or packet.get('schema_version')!=1:
        raise ValueError('unsupported lab packet')
    scenarios=packet['scenarios']; rows=[]; ids=set()
    for s in scenarios:
        if s['id'] in ids or type(s['expected_allow']) is not bool:
            raise ValueError('invalid scenario identity or expectation')
        ids.add(s['id'])
        decision=authorize(s['request'],**s['context'])
        naive=action_only_baseline(s['request'],**s['context'])
        rows.append({'id':s['id'],'case':s['case'],'expected_allow':s['expected_allow'],
                     'expected_reason':s['expected_reason'],'guard':decision,
                     'action_only_baseline_allow':naive})
    def score(values):
        return {'false_allows':sum(v and not r['expected_allow'] for v,r in zip(values,rows)),
                'false_denies':sum(not v and r['expected_allow'] for v,r in zip(values,rows))}
    return {'schema_version':1,'synthetic':True,'model_evaluated':False,
            'scope':'Deterministic policy decisions on an authored fixture matrix; no execution or external-system test.',
            'scenario_count':len(rows),'guard':score([r['guard']['allowed'] for r in rows]),
            'guard_reason_mismatches':sum(r['guard']['reason']!=r['expected_reason'] for r in rows),
            'action_only_baseline':score([r['action_only_baseline_allow'] for r in rows]),
            'input_sha256':hashlib.sha256((HERE/'scenarios.json').read_bytes()).hexdigest(),
            'guard_sha256':hashlib.sha256((HERE/'guard.py').read_bytes()).hexdigest(),'scenarios':rows}

if __name__=='__main__':
    result=run()
    print(json.dumps(result,indent=2,sort_keys=True))
    raise SystemExit(0 if not any(result['guard'].values()) and not result['guard_reason_mismatches'] else 1)
