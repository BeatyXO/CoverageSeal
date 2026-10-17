# Stable StudioNet deployment and lifecycle proof

**Network:** stable `studionet`, chain ID **61999**, RPC `https://studio.genlayer.com/api`.

## Corrected deployments

| Contract | Address | Finalized deployment transaction |
| --- | --- | --- |
| CoverageSeal | [`0xEcC5472b8288792B0F70aEceB48Ce6fF5dd75669`](https://explorer-studio.genlayer.com/address/0xEcC5472b8288792B0F70aEceB48Ce6fF5dd75669) | [`0xc80330b8fc12bbfe63524d5ee1c42e515a03fef0059af3b0d449f72e917bd906`](https://explorer-studio.genlayer.com/tx/0xc80330b8fc12bbfe63524d5ee1c42e515a03fef0059af3b0d449f72e917bd906) |
| CoverageGate | [`0xa5e61fB8F2Ef138b291bD42d77Be1692A3fA1EcD`](https://explorer-studio.genlayer.com/address/0xa5e61fB8F2Ef138b291bD42d77Be1692A3fA1EcD) | [`0x78cc5e874347f33297a324abe2b7fe13a5a64f00e0ffcabaf3b51d9734a81d3d`](https://explorer-studio.genlayer.com/tx/0x78cc5e874347f33297a324abe2b7fe13a5a64f00e0ffcabaf3b51d9734a81d3d) |

Both deploy receipts are `FINALIZED`, `MAJORITY_AGREE`, with successful execution. CoverageGate was constructed with the corrected CoverageSeal address above. The earlier deployment pair is superseded; the proof JSON records the corrected pair as canonical.

## Complete two-dimension lifecycle

Schema `1` requires `OWNERS` and `FINANCES` under `REQUIRE_FULL`. Package `1` contains the pinned `ownership.txt` and `finances.txt` fixtures from commit `1ddcce53a43099fa25ec651a1bc06646f4a4771d`. All four requirement/artifact edges returned `FULL` (`3`), and both positive artifact pairs returned `NO_CONFLICT` (`1`). Package finalization returned snapshot `1de0db8d9289efb975ffca6e21f2e7cff2d7e49b347c17f947b122179f0eff7b` and status `COMPLETE` (`2`). Both requirement summaries are `COVERED` (`3`), with zero conflicts or unresolved edges.

Certificate pins:

- Definition/schema hash: `fd02d81e0d77de329d8dee8ba7d8520f03f0fe378e9ef3086a7e73c9ff07b180`
- Manifest/package hash: `2bbe1b8a4bac34ae2a4975dcc0cb8d1d17d0103846ee54fb16de73e12993a04d`
- Final snapshot hash: `1de0db8d9289efb975ffca6e21f2e7cff2d7e49b347c17f947b122179f0eff7b`

`is_complete` returns true for this exact package ID and triple hash pin, false for a substituted package hash, the exact pins of the incomplete package, and unknown package ID `99`.

## Required evidence missing

Package `2` contains only the pinned `ownership_only.txt` fixture. Its ownership requirement is `COVERED` (`3`); its finance requirement is `MISSING` (`1`), with no unresolved assessment. Finalization succeeded and set package status `INCOMPLETE` (`3`), with snapshot `54df873b451e8e045deb6efff97d1c491657d97265eab80db2d4b4382123c4ae`. The CoverageGate rejected its exact pins.

## Conflicting evidence

Package `3` contains the pinned `incidents_clear.txt` and `incidents_conflicting.txt` documents. Both were assessed `FULL` (`3`) for requirement `INCIDENTS`; the pair returned `CONTRADICTS` (`2`) with a grounded excerpt from each report. Finalization succeeded with requirement status `CONFLICTED` (`4`), one conflict, no unresolved assessment, and package status `INCOMPLETE` (`3`). Its exact pins return false from `is_complete`. Schema/package/snapshot hashes and all finalized transaction receipts are in the proof JSON.

## Consumer gate

CoverageGate accepted the one-time action `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` against the complete certificate and persisted the executor, package ID, all three pins, and payload hash. Read-back confirms `was_executed=true`. Finalized rollback receipts prove:

- Wrong package hash: `coverage certificate missing or mismatched`.
- Reused action hash: `action replay`.
- Incomplete package certificate: `coverage certificate missing or mismatched`.

All transaction IDs, receipts, edge results, and deployment metadata are in [`proof/verified-studionet.json`](proof/verified-studionet.json). Every transaction described there was checked with GenLayerJS `2.0.0-rc.1` and is `FINALIZED`; successful operations have leader execution `SUCCESS`, and expected gate rejections have leader execution `ERROR` with the rollback reason shown.

## Fixtures and local checks

The five immutable raw URLs are pinned to the pushed fixture commit above. A fresh fetch of each URL matched its manifest Keccak-256 digest.

```bash
python scripts/preflight.py --final
python -m compileall -q contracts scripts tests
python -m pytest tests/unit -q
python -m pytest tests/direct -q
GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/coverage_seal.py
GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/coverage_gate.py
```

The recorded local results are 4 unit tests and 19 Direct Mode tests passing; both contracts pass `genvm-lint check` against the pinned v0.3.0-rc7 runner. The linter reports a newer runner is available. The StudioNet endpoint does not expose `gen_getTransactionLifecycle`, so finality was confirmed from receipt-backed transaction status.
