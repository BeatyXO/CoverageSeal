"""Verify the official linter bundle and seed the legacy Direct Mode cache.

Run genvm-lint check first. No SDK code or archive contents are modified.
"""
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import shutil

from genvm_linter.validate.artifacts import get_tarball_path
from gltest.direct.sdk_loader import CACHE_DIR

RUNNER = 'v0.3.0-rc7'
SHA256 = 'e218a1854214681560351051f76fe2b878545cf3409455ef372d57014a88ca67'


def checksum(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main() -> None:
    if version('genvm-linter') != '0.11.0' or version('genlayer-test') != '0.29.2':
        raise RuntimeError('Expected genvm-linter 0.11.0 and genlayer-test 0.29.2')
    if os.environ.get('GENVM_VERSION') != RUNNER:
        raise RuntimeError('Set GENVM_VERSION=' + RUNNER)
    source = get_tarball_path(RUNNER)
    if checksum(source) != SHA256:
        raise RuntimeError('Linter archive does not match official runners-all SHA-256')
    destination = CACHE_DIR / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if checksum(destination) != SHA256:
        raise RuntimeError('Direct Mode cache copy checksum mismatch')
    print(f'PASS: {RUNNER} official archive SHA-256 {SHA256}')
    print(f'Copied {source} to {destination}')


if __name__ == '__main__':
    main()
