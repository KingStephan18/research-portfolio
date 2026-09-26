#!/usr/bin/env python3
"""Inspect source references, shared origins and declared contradictions.

Synthetic demonstration only. Relations and origin groups are supplied by a
human/dataset author; this program does not verify entailment or factual truth.
No network, model, filesystem writes or external dependencies are used.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

KINDS = frozenset({'primary', 'secondary', 'reconstruction'})
RELATIONS = frozenset({'supports', 'contradicts', 'context'})


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    if value != value.strip():
        raise ValueError(f'{field} must not have surrounding whitespace')
    # Reject lone surrogates before any output is emitted.
    value.encode('utf-8')
    return value


def _list(value: Any, field: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f'{field} must be a list')
    return value


def review_dataset(data: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic metadata checks; never return a truth judgment.

    Raises ValueError on unsupported or ambiguous input. This teaching example
    intentionally accepts only data explicitly marked synthetic=True.
    """
    if not isinstance(data, dict):
        raise ValueError('root must be an object')
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('schema_version must be integer 1')
    if data.get('synthetic') is not True:
        raise ValueError('this demonstration only accepts explicitly synthetic data')
    sources: dict[str, dict[str, Any]] = {}
    for source in _list(data.get('sources'), 'sources'):
        if not isinstance(source, dict):
            raise ValueError('each source must be an object')
        sid = _text(source.get('id'), 'source.id')
        if sid in sources:
            raise ValueError('duplicate source id')
        _text(source.get('title'), 'source.title')
        _text(source.get('origin_group'), 'source.origin_group')
        kind = _text(source.get('kind'), 'source.kind')
        if kind not in KINDS:
            raise ValueError('unsupported source kind')
        sources[sid] = source

    reports: list[dict[str, Any]] = []
    claim_ids: set[str] = set()
    for claim in _list(data.get('claims'), 'claims'):
        if not isinstance(claim, dict):
            raise ValueError('each claim must be an object')
        cid = _text(claim.get('id'), 'claim.id')
        if cid in claim_ids:
            raise ValueError('duplicate claim id')
        claim_ids.add(cid)
        text = _text(claim.get('text'), 'claim.text')
        seen_sources: set[str] = set()
        support_origins: list[str] = []
        contradict_origins: set[str] = set()
        flags: set[str] = set()
        evidence = _list(claim.get('evidence'), 'claim.evidence')
        for item in evidence:
            if not isinstance(item, dict):
                raise ValueError('each evidence item must be an object')
            sid = _text(item.get('source_id'), 'evidence.source_id')
            relation = _text(item.get('relation'), 'evidence.relation')
            if relation not in RELATIONS:
                raise ValueError('unsupported evidence relation')
            if sid not in sources:
                raise ValueError('evidence references an unknown source')
            if sid in seen_sources:
                raise ValueError('a source may occur only once per claim; split ambiguous claims')
            seen_sources.add(sid)
            source = sources[sid]
            if source['kind'] == 'reconstruction':
                flags.add('RECONSTRUCTION')
                continue
            if relation == 'supports':
                support_origins.append(source['origin_group'])
            elif relation == 'contradicts':
                contradict_origins.add(source['origin_group'])
        support_groups = set(support_origins)
        if len(support_origins) > len(support_groups):
            flags.add('SHARED_ORIGIN')
        if support_groups and contradict_origins:
            state = 'CONFLICT'
        elif contradict_origins:
            state = 'REVIEW_REQUIRED'
        elif flags:
            state = 'REVIEW_REQUIRED'
        elif support_groups:
            state = 'TRACEABLE'
        else:
            state = 'UNSOURCED'
        reports.append({
            'id': cid,
            'text': text,
            'review_state': state,
            'supporting_origin_groups': len(support_groups),
            'contradicting_origin_groups': len(contradict_origins),
            'source_references': len(seen_sources),
            'flags': sorted(flags),
            'truth_verdict': None,
        })
    return {
        'schema_version': 1,
        'synthetic': True,
        'scope': 'Reference and declared-relation checks only; not factual verification.',
        'claim_count': len(reports),
        'claims': reports,
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys at any depth without echoing their names."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON object key')
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError('non-finite JSON number')


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('JSON number exceeds supported finite range')
    return number


def load_strict_json(text: str) -> dict[str, Any]:
    """Parse JSON without last-key-wins ambiguity or non-finite numbers."""
    data = json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant, parse_float=_finite_float)
    # Validate all decoded strings, including unused metadata and object keys.
    pending = [data]
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            value.encode('utf-8')
        elif isinstance(value, dict):
            pending.extend(value.keys())
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Synthetic JSON dataset')
    args = parser.parse_args(argv)
    try:
        # Bound the actual read, not just a potentially stale file-size check.
        with args.input.open('rb') as handle:
            raw = handle.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('input exceeds the 2 MB demonstration limit')
        data = load_strict_json(raw.decode('utf-8'))
        result = review_dataset(data)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        # Do not echo input content or absolute filesystem paths.
        if isinstance(exc, OSError):
            message = 'unable to read input file'
        elif isinstance(exc, json.JSONDecodeError):
            message = 'input is not valid JSON'
        elif isinstance(exc, (UnicodeError, RecursionError)):
            message = 'input encoding or nesting is unsupported'
        else:
            message = str(exc)
        print(f'Input rejected: {message}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
