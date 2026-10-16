#!/usr/bin/env python3
"""Print GenVM-compatible Keccak-256 digests for immutable fixture bytes."""
from pathlib import Path
from Crypto.Hash import keccak
ROOT = Path(__file__).resolve().parents[1]
for file in sorted((ROOT / 'fixtures').glob('*.txt')):
    h = keccak.new(digest_bits=256)
    h.update(file.read_bytes())
    print(f'{file.name}: {h.hexdigest()}')
