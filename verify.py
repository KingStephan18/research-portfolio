#!/usr/bin/env python3
"""Run local sample tests and compare generated output with committed fixtures."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent

def run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable,*command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)

def main() -> int:
    failures=[]
    for folder in ['evidence-ledger','permission-boundary']:
        r=run(['-m','unittest','discover','-s',folder,'-v'])
        print(f'{folder}: '+('PASS' if r.returncode==0 else 'FAIL'))
        print(r.stderr.strip())
        if r.returncode: failures.append(folder)
    for command,dest in [(['evidence-ledger/ledger.py','evidence-ledger/claims.json'],'evidence-ledger/results.json'),
                         (['permission-boundary/run_lab.py'],'permission-boundary/results.json')]:
        r=run(command)
        match=r.returncode==0 and r.stdout.encode('utf-8')==(ROOT/dest).read_bytes()
        print(f'Reproduce {dest}: '+('PASS' if match else 'FAIL'))
        if not match: failures.append(dest)
    manifest=ROOT/'SHA256SUMS.txt'
    if manifest.exists():
        count=0
        for line in manifest.read_text().splitlines():
            digest,name=line.split('  ',1); relative=Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                failures.append('unsafe manifest entry'); continue
            target=ROOT/relative
            if target.is_symlink() or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
                failures.append('hash: '+name)
            count+=1
        print(f'Manifest entries checked: {count}')
    else:
        failures.append('missing SHA256SUMS.txt')
    print('OVERALL: '+('FAIL' if failures else 'PASS'))
    for failure in failures: print(' - '+failure)
    return int(bool(failures))

if __name__=='__main__': raise SystemExit(main())
