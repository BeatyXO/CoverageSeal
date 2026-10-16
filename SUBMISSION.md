# Submission specification

**Name:** CoverageSeal — semantic completeness and contradiction-aware coverage matrix.

**Category:** standalone reusable Intelligent Contract primitive with no frontend.

**What AI does:** evaluate bounded requirement-to-public-document coverage and contradiction between two independently fetched, content-digest-pinned documents. Every decisive excerpt must appear in the validator's own fetched source. Returned enums and content hashes are verified under custom equivalence.

**What deterministic logic does:** fix policy at seal time; enforce URL namespace, digests, duplicate prevention, all required edge/pair evaluations, thresholds, optional semantics, conflict precedence, snapshot hashing, one-time downstream execution.

**Composability:** `CoverageGate` proves a different IC can block an action until a specific sealed package and schema have a `COMPLETE` snapshot. Query takes all three hashes to prevent replay against a different definition or package snapshot.

**Minimum reviewer evidence:** successful Direct Mode matrix/hostile tests; deployed CoverageSeal and CoverageGate on 61999; finalized COMPLETE/INCOMPLETE and contradictory scenarios; correct/incorrect digest and wrong schema hash; blocked gate replay. Link to actual explorer tx evidence, not screenshots of mocked calls.

**Limitations:** This is semantic coverage, not guaranteed fact truth, source independence, legal/compliance attestation or general proof of correctness. Onchain semantic costs bounded by small matrix limits. Real deployment and all network proof unverified in handoff ZIP.
