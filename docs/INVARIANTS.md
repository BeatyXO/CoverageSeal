# Protocol invariants

1. Schema requirements and source namespace are owner-controlled before seal and immutable after seal.
2. Schema hash deterministically commits to ordered complete requirement definitions and policies; package hash commits to source URLs and digests in order.
3. Each package pins the sealed schema hash at creation; source URLs must remain inside the originally sealed HTTPS namespace.
4. Every artifact has a unique content digest within its package, preventing exact-blob duplicate inflation (not semantic independence assurance).
5. Assessments only occur after manifest seal and only once per requirement/artifact pair; pair decisions are one-shot and ordered by artifact ID.
6. The AI is forbidden to set `COMPLETE`/`INCOMPLETE`, decide coverage thresholds, change owner/schema/manifest, or choose gate actions.
7. A `FULL` or `PARTIAL` edge requires a short excerpt in the independently fetched **digest-verified** source; decisive contradiction requires grounded excerpts in **both** such sources.
8. Validators independently re-fetch and re-run classification; malformed leader/validator decisions fail closed.
9. An unfetched, digest-changed, unresolved or ambiguous assessment prevents finalization; it must never count as `NONE` or `COVERED`.
10. Material contradiction blocks completion even if a separate artifact provides a `FULL` edge; unresolved potential contradictions also block finalization.
11. A `PARTIAL` does not satisfy `REQUIRE_FULL`; `COMBINE_PARTIAL` requires the frozen threshold over unique document-content digests.
12. Finalized snapshots are immutable; no after-the-fact assessment can rewrite history or change the pinned hash.
13. `CoverageGate` requires four bindings: package ID and three hashes; every action hash can be consumed exactly once.
14. Unknown package IDs fail `is_complete` rather than accidentally opening consumer access.
