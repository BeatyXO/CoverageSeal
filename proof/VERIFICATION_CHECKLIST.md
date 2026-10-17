# Verification checklist

## Local verification completed

- [x] Python 3.12 compileall over contracts, scripts and tests
- [x] `python scripts/preflight.py`
- [x] `pytest tests/unit -q`: 4 passed
- [x] `pytest tests/direct -q`: 19 passed, including validator re-fetch/quote-grounding and disagreement cases
- [x] `genvm-lint check` passes for both contracts with `GENVM_VERSION=v0.3.0-rc7`
- [x] CLI target confirmed as stable `studionet`, chain ID 61999, RPC `https://studio.genlayer.com/api`
- [x] All five fixture URLs are pinned to commit `1ddcce53a43099fa25ec651a1bc06646f4a4771d` and fetched bytes match their Keccak-256 digests

## Stable StudioNet verification completed

- [x] Corrected CoverageSeal and CoverageGate deployed; both deployment receipts are finalized
- [x] Two required dimensions and two pinned documents assessed across all four edges
- [x] Both positive-positive pairs assessed as `NO_CONFLICT`; package finalized `COMPLETE`
- [x] Exact certificate pins return true; substituted package hash, incomplete certificate and unknown package return false
- [x] CoverageGate recorded a valid action with persisted execution receipt
- [x] Wrong-pin, replay and incomplete-package actions finalized with expected rollback reasons
- [x] Required-missing finance package finalized `INCOMPLETE`
- [x] Transaction IDs, receipt finality, consensus and execution outcomes recorded in `verified-studionet.json`
- [x] `python scripts/preflight.py --final` passes against the proof record

Receipt finality was checked with GenLayerJS `2.0.0-rc.1`; the StudioNet endpoint does not expose `gen_getTransactionLifecycle`. The linter reports a newer runner is available, while the contracts remain pinned to the v0.3.0-rc7 runner validated by Direct Mode and the explicit semantic checks.
