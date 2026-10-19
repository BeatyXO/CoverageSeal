#!/usr/bin/env python3
"""Offline structural preflight; --final additionally checks pinned fixtures and proof file."""
from pathlib import Path
import argparse
import ast
import json
import hashlib
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
    c = (ROOT / 'contracts/coverage_seal.py').read_text(encoding='utf-8')
    gate = (ROOT / 'contracts/coverage_gate.py').read_text(encoding='utf-8')
    cfg = (ROOT / 'gltest.config.yaml').read_text(encoding='utf-8')
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
        data = json.loads(manifest.read_text(encoding='utf-8'))
        sha = data.get('fixture_commit', '')
        if not re.fullmatch(r'[0-9a-f]{40}', sha):
            faults.append('fixture commit not pinned to 40-hex SHA')
        if 'FIXTURE_COMMIT_PLACEHOLDER' in (ROOT / 'docs/REVIEWER_DEMO.md').read_text(encoding='utf-8'):
            faults.append('reviewer demo not pinned')
        proof = ROOT / 'proof/verified-studionet.json'
        if not proof.exists():
            faults.append('no verified-studionet.json (record real proof; do not fabricate)')
        else:
            data = json.loads(proof.read_text(encoding='utf-8'))
            if data.get('chain_id') != 61999 or not data.get('coverage_seal_address') or not data.get('coverage_gate_address'):
                faults.append('proof lacks chain ID or deploy addresses')
            for name in ('coverage_seal', 'coverage_gate'):
                source = data.get('source_verification', {}).get(name, {})
                text = (ROOT / 'contracts' / (name + '.py')).read_text(encoding='utf-8')
                canonical = text.replace('\r\n', '\n').replace('\r', '\n').rstrip('\n') + '\n'
                digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
                if (source.get('matches') is not True or source.get('local_sha256') != digest or
                        source.get('deployed_sha256') != digest or
                        source.get('address') != data.get(name + '_address')):
                    faults.append('proof source mismatch: ' + name)
            journal_path = ROOT / 'proof/closeout-journal.json'
            if not journal_path.is_file():
                faults.append('missing receipt-backed closeout journal')
            else:
                journal = json.loads(journal_path.read_text(encoding='utf-8'))
                if journal.get('chain_id') != 61999 or not journal.get('completed_at_utc'):
                    faults.append('closeout journal incomplete')
                required_transactions = {
                    'deploy_coverage_seal', 'deploy_coverage_gate', 'finalize_complete',
                    'finalize_missing', 'finalize_conflict', 'consumer_execute',
                    'consumer_wrong', 'consumer_replay', 'consumer_incomplete',
                }
                if not required_transactions.issubset(journal.get('transactions', {})):
                    faults.append('closeout journal lacks required lifecycle transactions')
                for label, entry in journal.get('transactions', {}).items():
                    receipt = entry.get('receipt', {})
                    if (receipt.get('status') != 'FINALIZED' or receipt.get('consensus') != 'MAJORITY_AGREE' or
                            receipt.get('execution') != entry.get('expected')):
                        faults.append('unverified transaction: ' + label)
    for fail in faults:
        print('FAIL:', fail)
    if faults:
        return 1
    print('PASS: structural preflight' + (' (final profile)' if args.final else ''))
    return 0

if __name__ == '__main__':
    sys.exit(main())
