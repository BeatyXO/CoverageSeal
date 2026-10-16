#!/usr/bin/env python3
"""Offline structural preflight; --final additionally checks pinned fixtures and proof file."""
from pathlib import Path
import argparse
import ast
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'SUBMISSION.md', 'DEPLOYMENT.md', 'docs/ARCHITECTURE.md',
    'docs/INVARIANTS.md', 'docs/THREAT_MODEL.md', 'docs/REVIEWER_DEMO.md',
    'contracts/coverage_seal.py', 'contracts/coverage_gate.py',
    'tests/direct/test_coverage_seal.py', 'requirements-test.txt',
    'gltest.config.yaml', 'fixtures/ownership.txt', 'fixtures/demo_manifest.json',
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--final', action='store_true')
    args = p.parse_args()
    faults = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            faults.append('missing: ' + name)
    for path in list((ROOT / 'contracts').glob('*.py')) + list((ROOT / 'scripts').glob('*.py')) + list((ROOT / 'tests').rglob('*.py')):
        try:
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        except SyntaxError as e:
            faults.append(f'bad Python {path}: {e}')
    c = (ROOT / 'contracts/coverage_seal.py').read_text()
    gate = (ROOT / 'contracts/coverage_gate.py').read_text()
    cfg = (ROOT / 'gltest.config.yaml').read_text()
    for field in ['run_nondet_unsafe', 'Keccak256(content)', 'finalize_package', 'get_requirement_status', 'is_complete']:
        if field not in c:
            faults.append('contract missing primitive ' + field)
    if '.view().is_complete(' not in gate:
        faults.append('no typed gate read')
    if 'https://studio.genlayer.com/api' not in cfg:
        faults.append('stable StudioNet URL missing')
    if 'studio-dev' in cfg or '61997' in cfg:
        faults.append('studio-dev referenced in network config')
    if list(ROOT.rglob('package.json')) or list(ROOT.rglob('index.html')):
        faults.append('frontend asset present')
    if args.final:
        manifest = ROOT / 'fixtures/demo_manifest.json'
        data = json.loads(manifest.read_text())
        sha = data.get('fixture_commit', '')
        if not re.fullmatch(r'[0-9a-f]{40}', sha):
            faults.append('fixture commit not pinned to 40-hex SHA')
        if 'FIXTURE_COMMIT_PLACEHOLDER' in (ROOT / 'docs/REVIEWER_DEMO.md').read_text():
            faults.append('reviewer demo not pinned')
        proof = ROOT / 'proof/verified-studionet.json'
        if not proof.exists():
            faults.append('no verified-studionet.json (record real proof; do not fabricate)')
        else:
            data = json.loads(proof.read_text())
            if data.get('chain_id') != 61999 or not data.get('coverage_seal_address') or not data.get('coverage_gate_address'):
                faults.append('proof lacks chain ID or deploy addresses')
    for fail in faults:
        print('FAIL:', fail)
    if faults:
        return 1
    print('PASS: structural preflight' + (' (final profile)' if args.final else ''))
    return 0

if __name__ == '__main__':
    sys.exit(main())
