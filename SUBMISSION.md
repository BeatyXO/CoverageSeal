# Submission specification

**Name:** CoverageSeal — semantic completeness and contradiction-aware coverage matrix.

**Category:** standalone reusable Intelligent Contract primitive with no frontend.

**What AI does:** evaluate bounded requirement-to-public-document coverage and contradiction between two independently fetched, content-digest-pinned documents. Every decisive excerpt must appear in the validator's own fetched source. Returned enums and content hashes are verified under custom equivalence.

**What deterministic logic does:** fix policy at seal time; enforce URL namespace, digests, duplicate prevention, all required edge/pair evaluations, thresholds, optional semantics, conflict precedence, snapshot hashing, one-time downstream execution.

**Composability:** `CoverageGate` proves a different IC can block an action until a specific sealed package and schema have a `COMPLETE` snapshot. Query takes all three hashes to prevent replay against a different definition or package snapshot.

**Verified reviewer evidence:** successful Direct Mode matrix/hostile tests; finalized CoverageSeal and CoverageGate on stable 61999; finalized COMPLETE, required-missing INCOMPLETE, and contradictory-evidence INCOMPLETE packages; exact/wrong certificate pins; persisted gate action, wrong-pin rejection and replay rejection. See `DEPLOYMENT.md` and `proof/verified-studionet.json` for transaction evidence.

**Limitations:** This is semantic coverage, not guaranteed fact truth, source independence, legal/compliance attestation or general proof of correctness. Onchain semantic costs are bounded by small matrix limits.

**Toolchain:** Python 3.12, GenLayer CLI 0.39.1, GenVM Linter 0.11.0, Testing Suite 0.29.2, official GenVM v0.3.0-rc7 runner bundle. Verification includes 4 unit and 20 Direct Mode tests, strict typing, semantic validation, ABI generation, and final structural preflight.

The finalization closeout fixes conflict precedence hiding an unresolved assessment. Both corrected deployments match contract source revision `447464f6b52d4942bd78e6c1a15a7b742617dcb2`. [Clean Ubuntu engineering CI](https://github.com/BeatyXO/CoverageSeal/actions/runs/39218358805) passed compilation, 4 unit tests, 20 Direct Mode tests, final preflight, both semantic validations, strict typing and ABI generation. The final evidence/documentation commit uses the same workflow; its exact SHA and Actions run identify the submitted revision.
