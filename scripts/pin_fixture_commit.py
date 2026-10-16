#!/usr/bin/env python3
"""Replace only a template SHA in fixture manifest/reviewer demo after actual first push."""
from pathlib import Path
from Crypto.Hash import keccak
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = 'FIXTURE_COMMIT_PLACEHOLDER'

def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[0-9a-f]{40}', sys.argv[1]):
        raise SystemExit('usage: python scripts/pin_fixture_commit.py <40-character lowercase commit SHA>')
    sha = sys.argv[1]
    path = ROOT / 'fixtures/demo_manifest.json'
    data = json.loads(path.read_text())
    if data['fixture_commit'] != PLACEHOLDER:
        raise SystemExit('fixture manifest already pinned; do not silently replace historical fixture commit')
    data['fixture_commit'] = sha
    url = f'https://raw.githubusercontent.com/BeatyXO/CoverageSeal/{sha}/fixtures/'
    data['source_prefix'] = url
    for filename in ['ownership.txt', 'finances.txt', 'incidents_clear.txt', 'incidents_conflicting.txt']:
        contents = (ROOT / 'fixtures' / filename).read_bytes()
        h = keccak.new(digest_bits=256)
        h.update(contents)
        data['artifacts'][filename] = {'url': url + filename, 'keccak256': h.hexdigest()}
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    demo = ROOT / 'docs/REVIEWER_DEMO.md'
    text = demo.read_text()
    if PLACEHOLDER not in text:
        raise SystemExit('reviewer demo already pinned')
    demo.write_text(text.replace(PLACEHOLDER, sha))
    print('Pinned source namespace and reviewer demo to', sha)
    print('Commit and push this change; do not alter fixture contents without a new fixture commit.')

if __name__ == '__main__':
    main()
