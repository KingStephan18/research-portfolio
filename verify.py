#!/usr/bin/env python3
"""Run local samples, reproduce fixtures, and verify complete artifact integrity."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = 'SHA256SUMS.txt'
IGNORED_DIRS = frozenset({'.git', '__pycache__', '.venv'})

def ignored_file(name: str) -> bool:
    return (name in {'.env', '.DS_Store', 'Thumbs.db'} or name.startswith('.env.')
            or name.endswith(('.pyc', '.pyo', '.pyd')))



def run(command: list[str]) -> subprocess.CompletedProcess:
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    return subprocess.run([sys.executable, *command], cwd=ROOT,
                          capture_output=True, text=True, encoding='utf-8',
                          timeout=60, env=env)


def check_manifest(root: Path) -> tuple[int, list[str]]:
    """Check syntax, canonical paths, uniqueness, complete coverage and hashes.

    Git internals, local environments and bytecode caches are excluded. This checks the local
    snapshot against its own manifest, not publisher identity or trustworthiness.
    """
    errors: list[str] = []
    manifest = root / MANIFEST_NAME
    try:
        if manifest.is_symlink() or not manifest.is_file():
            return 0, ['missing or invalid manifest']
        with manifest.open('rb') as handle:
            raw = handle.read(1_000_001)
        if len(raw) > 1_000_000:
            return 0, ['manifest exceeds size limit']
        lines = raw.decode('utf-8').splitlines()
    except (OSError, UnicodeError):
        return 0, ['unreadable manifest']
    entries: dict[str, str] = {}
    if not lines:
        return 0, ['empty manifest']
    for line in lines:
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            errors.append('malformed manifest entry')
            continue
        digest, name = match.groups()
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or path.as_posix() != name
                or '\\' in name or ':' in name or name == MANIFEST_NAME
                or any(part in IGNORED_DIRS for part in path.parts)
                or ignored_file(path.name)
                or any(ord(char) < 32 for char in name)):
            errors.append('unsafe or noncanonical manifest entry')
            continue
        if name in entries:
            errors.append('duplicate manifest entry')
            continue
        entries[name] = digest
    if not entries:
        errors.append('manifest has no valid entries')

    actual: set[str] = set()
    def on_walk_error(_error: OSError) -> None:
        errors.append('unable to enumerate artifact inventory')
    try:
        for folder, directories, filenames in os.walk(root, followlinks=False, onerror=on_walk_error):
            kept = []
            for name in directories:
                if name in IGNORED_DIRS:
                    continue
                if (Path(folder) / name).is_symlink():
                    errors.append('symlink directory in artifact inventory')
                else:
                    kept.append(name)
            directories[:] = kept
            for name in filenames:
                if ignored_file(name):
                    continue
                path = Path(folder) / name
                relative = path.relative_to(root).as_posix()
                if relative == MANIFEST_NAME:
                    continue
                actual.add(relative)
                if path.is_symlink() or not path.is_file():
                    errors.append('non-regular artifact in inventory')
                    continue
                if relative in entries:
                    digest = hashlib.sha256()
                    with path.open('rb') as handle:
                        for chunk in iter(lambda: handle.read(1_048_576), b''):
                            digest.update(chunk)
                    if digest.hexdigest() != entries[relative]:
                        errors.append('hash mismatch: ' + relative)
    except OSError:
        errors.append('unable to read artifact inventory')
    if set(entries) - actual:
        errors.append('manifest references missing artifacts')
    if actual - set(entries):
        errors.append('artifact inventory contains unlisted files')
    return len(entries), errors


def main() -> int:
    failures: list[str] = []
    for folder in ['evidence-ledger', 'permission-boundary', 'maintainer-security', 'audit-tests']:
        try:
            result = run(['-m', 'unittest', 'discover', '-s', folder, '-v'])
        except (OSError, UnicodeError, subprocess.SubprocessError):
            print(folder + ': FAIL (test process unavailable or timed out)')
            failures.append(folder)
            continue
        print(folder + ': ' + ('PASS' if result.returncode == 0 else 'FAIL'))
        print(result.stderr.strip())
        if result.returncode:
            failures.append(folder)
    for command, dest in [(['evidence-ledger/ledger.py', 'evidence-ledger/claims.json'], 'evidence-ledger/results.json'),
                          (['permission-boundary/run_lab.py'], 'permission-boundary/results.json')]:
        try:
            result = run(command)
            match = result.returncode == 0 and result.stdout.encode('utf-8') == (ROOT / dest).read_bytes()
        except (OSError, UnicodeError, subprocess.SubprocessError):
            match = False
        print('Reproduce ' + dest + ': ' + ('PASS' if match else 'FAIL'))
        if not match:
            failures.append(dest)
    count, integrity_errors = check_manifest(ROOT)
    failures.extend(integrity_errors)
    print(f'Manifest entries checked: {count}')
    print('OVERALL: ' + ('FAIL' if failures else 'PASS'))
    for failure in failures:
        print(' - ' + failure)
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
