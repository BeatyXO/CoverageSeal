# Deployment evidence — not yet executed

**Target:** stable StudioNet `studionet`, `https://studio.genlayer.com/api`, chain ID **61999**.

No deployed addresses, tx hashes, consensus success counts, fee proof, or live gate executions were produced for this handoff ZIP. **Do not invent any of them.**

```bash
genlayer network set studionet
genlayer network info   # verify effective RPC and chain ID 61999 BEFORE each deploy/write
genlayer deploy --contract contracts/coverage_seal.py
# after recording a finalized CoverageSeal address:
genlayer network info
genlayer deploy --contract contracts/coverage_gate.py --args '<FINALIZED_COVERAGESEAL_ADDRESS>'
```

For test calls see `docs/REVIEWER_DEMO.md`. Use supported StudioNet fees if required by the installed stable tooling. Wait for finality and verify tx execution status before proceeding. **Never switch to studio-dev (61997) merely to work around fee/SDK issues.**

## To fill with real evidence after completion

- Source git commit SHA and pinned fixture commit SHA:
- Final CoverageSeal contract address, deploy transaction, finalized state:
- Schema creation, requirement creation, schema seal tx IDs / schema hash:
- Package creation, artifact registration, package seal tx IDs / package hash:
- Edge and pair assessment tx IDs, with source digests and consensus status:
- Finalization tx ID / package status / snapshot hash:
- CoverageGate address and deploy tx ID:
- Successful pin-correct gate action tx ID:
- Wrong-hash rejection tx ID/error:
- Replay rejection tx ID/error:
- Incomplete/conflicted proof tx IDs:
- Exact Direct Mode command and real results:
- Exact preflight command and real results:
- CLI/SDK versions, network details, fee path used:

Once genuinely verified, record `proof/verified-studionet.json` with live addresses, chain ID 61999, and links to actual explorer transactions, run `python scripts/preflight.py --final`, then push the final commit.
