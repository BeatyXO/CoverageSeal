# Verification checklist

## Verified locally

- [x] Python 3.12 compileall over contracts, scripts and tests
- [x] `python scripts/preflight.py`
- [x] `pytest tests/unit -q`: 4 passed
- [x] `pytest tests/direct -q`: 19 passed, including validator re-fetch/quote-grounding and disagreement cases
- [x] `genvm-lint lint` passes for both contracts
- [x] CLI network info reports `studionet`, chain ID 61999 and `https://studio.genlayer.com/api`
- [x] Fixture Keccak-256 values calculated from local fixture bytes

## Still required

- [ ] `genvm-lint check` semantic validation against pinned SDK (blocked locally by Windows access denied reading the cached SDK)
- [ ] Push fixture commit, obtain its actual SHA, pin manifest/demo URLs and verify reachable remote bytes
- [ ] Deploy CoverageSeal and CoverageGate on stable StudioNet and capture finalized transaction evidence
- [ ] Prove successful and rejected consumer actions on chain, including replay rejection
- [ ] Record a real negative package lifecycle and publish `proof/verified-studionet.json`
- [ ] Run final preflight, inspect remote tree and push the pinned final commit to GitHub

No chain deployment or live transaction proof is claimed in this repository state.
