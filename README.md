# CoverageSeal

**Reusable GenLayer Intelligent Contract primitive for semantic document-set completeness. No frontend.**

CoverageSeal does not count uploaded files or ask a model whether a package is "good enough." It independently classifies **coverage edges** (requirement × artifact), independently tests **contradiction edges** between positive artifacts, and derives each requirement's status and overall package completeness by deterministic rules fixed before assessing evidence.

**Example:** a diligence package requires owners, financial history and incident disclosures. Having 37 files does not mean it contains the needed information. A declaration may cover ownership, a financial statement may cover revenue, and two apparently complete incident statements may contradict each other. CoverageSeal emits a pinned `COMPLETE`/`INCOMPLETE` certificate that other ICs can read.

## Contract boundary

- `contracts/coverage_seal.py`: schema/package lifecycle, consensus-backed semantic edges, deterministic conflict-aware coverage aggregation, immutable final snapshot.
- `contracts/coverage_gate.py`: typed IC consumer; checks `is_complete(package_id,schema_hash,package_hash,snapshot_hash)` and enforces action replay protection.
- **Not** a truth oracle, evidence-independence oracle, generic AI evaluator, contract-execution marketplace or application/UI.

## Quick start

Python 3.12+ and stable GenLayer Direct Mode tools are required. See `requirements-test.txt`; the code pins `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` in both contracts.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
python scripts/preflight.py
python -m compileall -q contracts scripts tests
pytest tests/unit/ -v
pytest tests/direct/ -v
python scripts/fixture_digests.py
```

**Network:** stable `studionet`, chain ID **61999**, RPC `https://studio.genlayer.com/api`. Verify `genlayer network info` before **every** live deploy/write, and never substitute `studio-dev` / 61997. `gltest.config.yaml` defaults to localnet for safety; use `--network studionet` explicitly during live proof.

## Deterministic status semantics

- Requirement statuses: `MISSING=1`, `PARTIAL=2`, `COVERED=3`, `CONFLICTED=4`, `UNRESOLVED=5`.
- Package statuses: `OPEN=1`, `COMPLETE=2`, `INCOMPLETE=3`.
- Each required requirement must be `COVERED`, no contradictions anywhere, and no unresolved assessments before finalization.
- A single `FULL` is enough for `REQUIRE_FULL`; a `COMBINE_PARTIAL` threshold counts distinct content-digest artifacts after pair conflicts are resolved. Optional missing requirement does not block completion, but an optional contradiction does.

## Verification status

Local verification completed: Python 3.12 compileall, structural preflight, 4 portable unit tests, 19 Direct Mode tests, and `genvm-lint check` pass. Direct Mode and semantic validation use the contract's pinned `py-genlayer` hash from the GenVM v0.3.0-rc7 bundle; validator tests explicitly rerun the independent fetch/classifier and reject a forged quote and a semantic disagreement. Select that cached bundle with `GENVM_VERSION=v0.3.0-rc7` when running the semantic check. The linter reports a newer runner is available; the contract remains pinned to the tested v0.3.0-rc7 hash.

The corrected contracts are deployed and finalized on stable StudioNet (chain ID 61999): CoverageSeal [`0xEcC5472b8288792B0F70aEceB48Ce6fF5dd75669`](https://explorer-studio.genlayer.com/address/0xEcC5472b8288792B0F70aEceB48Ce6fF5dd75669) and CoverageGate [`0xa5e61fB8F2Ef138b291bD42d77Be1692A3fA1EcD`](https://explorer-studio.genlayer.com/address/0xa5e61fB8F2Ef138b291bD42d77Be1692A3fA1EcD). The finalized live lifecycle assessed all four edges for two required dimensions and two pinned artifacts, resolved both positive pairs, finalized `COMPLETE`, and verified the exact certificate pins. A second package finalized `INCOMPLETE` because required finance evidence was missing. A third package finalized `INCOMPLETE` because two positive incident reports contradicted each other. CoverageGate recorded one valid action and finalized rollback receipts for a wrong pin, replay, and the missing-evidence package. Detailed receipts and hashes are in [`proof/verified-studionet.json`](proof/verified-studionet.json).

Fixtures are pinned to source commit `1ddcce53a43099fa25ec651a1bc06646f4a4771d`; all five public URLs were fetched and their bytes matched the manifest Keccak digests. An earlier malformed semantic response was classified `AMBIGUOUS` and blocked finalization. The prompts now name the exact JSON keys expected by the parser, and the corrected two-dimension lifecycle finalized successfully. StudioNet does not expose `gen_getTransactionLifecycle`; finality and execution outcomes were read from receipts with GenLayerJS `2.0.0-rc.1`.

See `SUBMISSION.md`, `DEPLOYMENT.md`, `docs/ARCHITECTURE.md`, `docs/INVARIANTS.md`, `docs/THREAT_MODEL.md`, `docs/REVIEWER_DEMO.md`, and `proof/VERIFICATION_CHECKLIST.md`.

Target repo: https://github.com/BeatyXO/CoverageSeal

## Security boundary

Source URL filtering is a conservative lexical restriction, not complete SSRF protection: DNS rebinding and redirects are controlled by the GenVM web runtime. See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for limits. Semantic responses are type/length/key checked and malformed output cannot become positive evidence.
