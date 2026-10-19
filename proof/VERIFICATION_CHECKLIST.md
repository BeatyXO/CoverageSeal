# Verification checklist

- [x] StudioNet chain ID checked as 61999 before other RPC operations.
- [x] Python 3.12 compilation and final structural preflight.
- [x] 4 unit tests and 20 Direct Mode tests (19 original plus 1 regression).
- [x] Both contracts: GenVM Linter 0.11.0 check, validate, strict typecheck and ABI generation.
- [x] Official v0.3.0-rc7 runner SHA-256 verified; unchanged bytes copied into the legacy Direct Mode cache.
- [x] Corrected deployments finalized; retrieved sources exactly match under documented LF normalization.
- [x] Consumer constructor pins the corrected CoverageSeal address.
- [x] Complete two-requirement lifecycle, missing-evidence lifecycle and contradictory-evidence lifecycle.
- [x] All 38 closeout transaction receipts FINALIZED; consensus and leader execution checked separately.
- [x] Exact complete pins accepted; wrong pins, missing-evidence certificate and conflicting certificate return false.
- [x] Consumer success persisted; wrong-pin, replay and incomplete-certificate rollbacks decoded and checked.
- [x] Finalized-state package and consumer read-backs verified.
- [x] Both independent validators reject forged quotes, wrong digests and classification disagreement.
- [x] Conflict cannot hide an unresolved assessment; regression passes.
- [x] Five immutable fixture URLs fetched again and matched manifest digests.
- [x] Historical 38 transaction references independently reverified and archived as superseded.
- [x] Clean Ubuntu engineering CI: [SUCCESS](https://github.com/BeatyXO/CoverageSeal/actions/runs/39218358805) on source revision `447464f6b52d4942bd78e6c1a15a7b742617dcb2`.

The final submission SHA and corresponding Actions run are reported after the evidence commit is pushed. The workflow repeats every required check. Repository-local preflight checks recorded source hashes and finalized receipt structure; it does not replace independent live receipt verification.

See [deployment evidence](../DEPLOYMENT.md), [canonical proof](verified-studionet.json), and [receipt journal](closeout-journal.json). Semantic coverage does not establish document truth, authority or source independence.
