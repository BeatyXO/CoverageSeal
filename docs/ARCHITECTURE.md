# Architecture: coverage, not truth or source independence

CoverageSeal is an IC primitive for certification of a **set** against a sealed requirement schema. A caller defines a bounded list of requirements with `REQUIRE_FULL` (1), `COMBINE_PARTIAL` (2, requiring N distinct content digests), or `OPTIONAL` (3). A sealed schema yields a 64-hex definition hash. A package binds that exact schema hash and a sealed, ordered manifest of 1–8 source URLs and their expected Keccak-256 digests. Source prefix is committed with schema and cannot be substituted later.

## AI boundary

A nondeterministic coverage edge `(package, requirement, artifact)` asks if *one independently fetched artifact* substantively covers the requirement: `NONE`, `PARTIAL`, `FULL`, `AMBIGUOUS`, `UNAVAILABLE`. `FULL`/`PARTIAL` require a verbatim excerpt independently present in the fetched source. A separate pairwise operation checks whether **two already-positive edges** make contradictory claims about that requirement. This is not a global truth oracle and not an independence adjudicator. Same-content digests cannot be repeated in a package, but two paraphrases are not asserted independent. We never say two partials guarantee meaningful coverage in domains requiring diversity of origin; callers should add that upstream.

Each custom `run_nondet_unsafe` validator reruns the web fetch and semantic judgment independently and compares stable codes/digests. Contradiction evidence excerpts must be grounded in the validator's independently fetched sources. Invalid/missing/mutated/unreachable content is `UNAVAILABLE` and blocks finalization; ambiguity is not silently downgraded to `NONE`. Source digests gate semantic access; mutable sources cannot quietly change the certified meaning.

## Deterministic completion

For each requirement, scan all package artifacts and evaluate each edge. For each *pair of positive edges*, require a pairwise contradiction certificate before finalization. Contradiction makes status `CONFLICTED`, including for optional requirements; missing/ambiguous/unavailable edges or pair outcomes make it `UNRESOLVED`, preventing finalization. Else one `FULL` yields `COVERED`; under `COMBINE_PARTIAL`, at least N `PARTIAL` yields `COVERED`; a remaining partial yields `PARTIAL_STATUS`; otherwise `MISSING`. Optional requirements do not block completeness merely for `MISSING` or `PARTIAL_STATUS` but material contradictions do. A package is `COMPLETE` only when every required requirement is `COVERED` and no requirement is `CONFLICTED`. Otherwise it finalizes `INCOMPLETE`. There is no completeness score invented by the LLM.

`finalize_package` computes the deterministic snapshot hash from the *full* ordered requirement summary plus package and schema hashes. Finalized state is immutable: cannot reassess edges or pairs. Consumers must pin all three hashes (`schema_hash`, `package_hash`, `snapshot_hash`), not just package ID or a permissive boolean.

## Data layout and limits

Storage uses `TreeMap` indices for schemas, ordered requirement slots, packages, ordered artifact slots, edge assessments and pair assessments. Limits: 8 requirements and 8 artifacts per package, 64 edge evaluations and up to 224 pair evaluations. Those are deliberately small to bound costs and execution. The package owner finalizes; public actors may submit evidence assessments for a sealed package. Every assessment is a unique write, no overwrite. No onchain storage of full fetched content; excerpts/reasoning are bounded.

## Consumer

`CoverageGate.execute` performs a **typed IC-to-IC synchronous view read** of `is_complete` and records an irreversible execution receipt keyed by an action digest. It rejects definition/payload snapshot substitution and replay. This is a minimal demo consumer, not a frontend or general escrow application.
