# CoverageSeal — repository completion & stable StudioNet proof handoff

You are taking over a **substantially implemented GenLayer Intelligent Contract repository named CoverageSeal**. You will receive `CoverageSeal-complete-handoff.zip`. **Do not return only a plan, checklist, commentary, website, or mockup.** Unzip and inspect the entire repository, perform the implementation/testing/deployment work in that existing folder, and push the completed result to:

**https://github.com/BeatyXO/CoverageSeal**

This is a newly created repository, initially empty at handoff. You may need to initialize the git repo locally. Do **not** clone a different existing project into it or replace CoverageSeal with another product. Preserve the protocol boundary below unless a real SDK/GenVM failure requires a documented change. Commit in logical phases. You must supply real proof, not guessed results.

## Product boundary: what CoverageSeal is

CoverageSeal is a **standalone reusable Intelligent Contract primitive**, **not** an app. **There must be no frontend**, website, wallet UI, API server, backend service, or general-purpose dashboard.

CoverageSeal certifies whether a bounded **set of pinned external artifacts** substantively covers a sealed **requirement schema**. The primitive has two separate consensus jobs:

1. Semantic **coverage edges** `(requirement, artifact)` classify `NONE`, `PARTIAL`, `FULL`, `AMBIGUOUS`, `UNAVAILABLE`. `FULL` and `PARTIAL` need verbatim decisive excerpts grounded in the **independently fetched** document, not merely leader text. `UNAVAILABLE` is for source error, changed/mismatched content digest or inaccessible evidence.
2. Semantic **contradiction edges** compare two positively covering artifacts against one requirement and classify `NO_CONFLICT`, `CONTRADICTS`, `AMBIGUOUS`, `UNAVAILABLE`. `CONTRADICTS` requires decisive excerpts **from both** separately fetched sources, verified by validators.

The **LLM must never decide package completeness**. The IC deterministically constructs the coverage/contradiction matrix and computes requirement statuses `MISSING`, `PARTIAL`, `COVERED`, `CONFLICTED`, `UNRESOLVED`, then package `COMPLETE` or `INCOMPLETE` from frozen policies:

- `REQUIRE_FULL`: one genuine FULL edge required; partials alone never count.
- `COMBINE_PARTIAL`: at least the frozen N partial edges from different content digests, subject to resolved pairwise contradictions.
- `OPTIONAL`: missing/partial does not block completion, but an actual contradiction anywhere still does.
- Any unassessed requirement/artifact edge, pending pair between positive edges, ambiguous/unavailable semantic result or content digest mismatch **blocks finalization** until resolved through the intended protocol. `CONFLICTED` can be finalized as `INCOMPLETE` but never `COMPLETE`.
- Definition hash commits to schema/source namespace; package hash commits to ordered artifact URLs and content hashes; final snapshot hash commits to all status summaries. No history rewrite or post-seal source substitution.

`contracts/coverage_gate.py` must remain a **real second IC** that performs a typed synchronous view read `is_complete(package_id, schema_hash, package_hash, snapshot_hash)` on CoverageSeal, rejects wrong hash pins, and disallows replay of an `action_hash`. It should record a genuine protected state change, not just print a result.

**This is not** another source-independence quorum (Corroborate), factual assurance DAG (AssureGraph), revision/correction lineage (Errata), licensing graph (LicenseMesh), rule-engine (ExceptionTree), or semantic single-document classifier. The distinct novelty is **conflict-aware semantic set coverage under a frozen completeness policy**. Do not simplify it to `AI decides if uploaded documents are enough`.

## Non-negotiable network: stable StudioNet

- Network alias: `studionet`
- **Chain ID: 61999**
- RPC: `https://studio.genlayer.com/api`
- Explorer: `https://explorer-studio.genlayer.com`
- Currency: GEN

This is **not** `studio-dev` (61997), `studio-next`, Asimov or Bradbury. Before **every** live deploy/write workflow, inspect effective CLI/SDK network target (for CLI, `genlayer network info`) and verify chain ID 61999 and exact RPC. If an SDK/CLI API differs, use the compatible stable StudioNet SDK path rather than moving networks.

## First-pass order — start by doing real work

1. Unzip; inspect **every** tracked file, especially `README.md`, `SUBMISSION.md`, `DEPLOYMENT.md`, all `docs/`, both contracts, all tests, fixtures, manifest, scripts, and CI workflow. Understand invariants and known unverified areas before editing.
2. Run `python scripts/preflight.py` **immediately** and record the actual result.
3. Use an isolated Python 3.12+ environment. Install the pinned `requirements-test.txt` and execute `python -m compileall -q contracts scripts tests`, `pytest tests/unit -v`, `pytest tests/direct -v`. Obtain `genvm-lint` and check both contracts against the header's pinned stable `py-genlayer` version; don't replace the SDK just to evade issues.
4. Fix every *actual* failure. Do not weaken assertions, skip tests, fake model outputs, remove the contradiction layer, change consensus to strict equality for semantic decisions, or bypass web access merely to get green results.
5. Read the official current GenLayer docs for SDK storage constraints (`TreeMap`, `@allow_storage`, `DynArray`, dataclasses), `gl.vm.run_nondet_unsafe` leader/validator behavior, `gl.nondet.web.get` response handling, JSON prompts, `Keccak256`, events, and typed IC reads. In particular, verify custom validator serialization under actual GenVM and `gl.vm.Return` handling. Update only on documented stable behavior or observed failures.

## Mandatory security and correctness work

Review and harden all of the following, then **prove the specific failure modes with Direct Mode tests**:

- Validators re-fetch the **same pinned source URL** independently and re-evaluate the semantic judgment, not merely inspect leader output shape. For each FULL/PARTIAL quote, validators check their own raw digest-matched bytes actually contain the cited evidence. For contradiction, both quoted fragments must be independently grounded.
- Validate all numeric codes, returned keys, excerpt/rationale lengths and malformed JSON/fault responses fail closed. Leader-forged `FULL`, invented quote, forged `CONTRADICTS`, source digest mismatch, validator/leader semantic disagreement and injected documents must be tested.
- A source URL is only admissible under the prefix frozen in the sealed schema. Harden redirects, DNS/rebinding where practical, local/private addresses, IP-literal obfuscations, unusual URL delimiters, query/fragment and path encoding, URL credential tricks, disallowed protocols, cross-host redirects and prefix-confusion; avoid introducing SSRF. The current starter's lexical filter is *not* a complete SSRF solution. Record remaining web runtime limits honestly.
- User-provided names, natural-language requirements and source text are untrusted. Do not let instructions within documents change classifier policy.
- Distinct artifacts must have distinct expected content digests; explain clearly that content deduplication does **not** establish source-origin independence (different problem).
- Bound requirements (8), artifacts per package (8), fetched source bytes, matrix size, pair count, excerpts, prompts, state growth and exposure to unbounded loops or unexpected resource cost.
- Ensure the full matrix is correctly traversed: all artifact × requirement classifications exist before finalization, all positive pairs are resolved, any contradiction dominates otherwise sufficient coverage, optional requirements cannot conceal contradictions, and ambiguity/unavailability blocks finalization.
- Prevent cross-schema/cross-package assessment, wrong-schema hash, unsealed package, duplicate pair, reverse-order pair, duplicate assessment, unauthorized schema changes/finalize, reset of sealed schemas or finalized packages, and accidental `COMPLETE` after data substitution.
- Snapshot/certificate binding: definition hash, manifest hash, snapshot hash; no weak hash construction, missing field, string ambiguity, reordered item collision, misleading false-positives for unknown packages.
- Ensure `CoverageGate` makes a **real typed IC-to-IC view call**, rejects unfinalized, INCOMPLETE, wrong package/schema/snapshot and replayed action hashes. Test both contracts deployed together in Direct Mode if possible and **definitely** in stable StudioNet.
- Add meaningful events or accessors where they improve auditability, without redesigning into a frontend or emitting secrets.

## GitHub and immutable fixtures (two-stage push)

The remote target is **BeatyXO/CoverageSeal**. Do not push the starter until real local checks are sensible, but the fixtures must first become addressable at a real Git commit. Once a first git commit that contains `fixtures/` has been pushed:

1. Read its **actual full 40-character commit SHA** from Git (no made-up SHA).
2. Run `python scripts/pin_fixture_commit.py <FULL_40_CHAR_COMMIT_SHA>` in the repository.
3. Confirm `fixtures/demo_manifest.json` and `docs/REVIEWER_DEMO.md` now reference immutable raw URLs such as `https://raw.githubusercontent.com/BeatyXO/CoverageSeal/<commit>/fixtures/ownership.txt` and the correct Keccak-256 content digests. Verify reachable bytes against digest with a real external request. The ZIP's placeholder is intentionally not pinned yet.
4. Commit and push the pin as a second commit. Do not leave `FIXTURE_COMMIT_PLACEHOLDER` in final evidence or live tests.
5. Keep fixture content unchanged after pinning; if it changes, create/push a new immutable fixture commit and update the pin coherently. Never use a mutable `main` branch URL as the decisive live source.

## Mandatory test expansion and proof

Write/revise Direct Mode tests so they exercise **real contract behavior**, not only source-string checks. Minimum cases: sealed schema hash, unsealed rejection, ownership, requirement policies/thresholds, excessive cardinality, source namespace and private-host protection, duplicate content digest, manifest hashing, full and partial coverage, two partials with no contradiction, partial-below-threshold, unassessed edges, pair pending, contradictory FULL documents, ambiguous semantic results, forged positive quote, forged contradiction, leader-validator disagreement, malformed LLM results, unreachable source, changed content, duplicate/reversed pairs, finalization one-way, wrong hash pin, unknown package, cross-package IDs, real consumer gate success/rejection/replay. Add multi-requirement composite tests, not only 1×1. Run the validator path, not just leader mocks; capture evidence for validator independence.

Preserve both offline static tests and Direct Mode tests. If a test failed because the expected behavior was wrong, document why and replace it with a stronger assertion rather than silently relaxing it.

## Mandatory live proof on stable StudioNet, chain 61999

After Direct Mode is genuinely green, run at least this **real finalized chain lifecycle**:

- Deploy CoverageSeal at a real chain-61999 address and save finalized deploy tx.
- Create schema with **at least two** required distinct dimensions; seal and obtain a genuine 64-hex definition hash.
- Create package with **two** pinned public fixture URLs and their actual Keccak-256 digests; seal and get non-empty 64-hex package hash.
- Independently consensus-assess every required edge; if any two artifacts positively cover one requirement, assess that pair. Produce a `COMPLETE` snapshot from deterministic matrix rules, with 64-hex snapshot hash.
- Show `is_complete` true only for the exact package ID + triple hash pin, false for substituted hashes and unknown/noncomplete packages.
- Deploy CoverageGate with the finalized CoverageSeal address. Demonstrate one correct permitted action with a recorded execution receipt, wrong-hash action rejection, and repeated action-hash replay rejection.
- Demonstrate at least one **negative** case: required missing evidence -> `INCOMPLETE`, and ideally conflicting incident reports -> `CONFLICTED`/`INCOMPLETE` (if actual model consensus succeeds; otherwise report validator disagreement, do not fake outcome).
- Read results using finalized state, never assume submitted or initial `ACCEPTED` means immutable finality.

If the live tooling requires fee estimation, use the stable Studionet-compatible documented fee path. Keep transaction identifiers and receipts for all steps. If a transaction fails or the network cannot be accessed, be explicit and finish the honest locally verifiable work; **never claim live success without actual evidence**.

## Documentation and final gates

Update `README.md`, `SUBMISSION.md`, `DEPLOYMENT.md`, all `docs/`, reviewer demonstration, proof checklist, CI, and the recorded test commands/results only with verified facts. Add `proof/verified-studionet.json` **only after** real proof exists; include chain ID, both deploy addresses, hashes, transaction IDs, explorer links and timestamp evidence where available. Do not invent addresses, transaction hashes, dates, pass counts, validator quorum evidence or CI status.

Before final push:

- `python scripts/preflight.py --final` passes (if genuine network proof exists).
- Python compile and all Direct Mode tests pass; GenVM lint passes.
- No frontend, secrets, `.env`, private keys, caches, build artifacts, huge binaries, virtual environments or unrelated files tracked.
- No accidental `studio-dev`/61997 network references in deployment paths; all actual live actions target 61999.
- Inspect `git diff`, tracked files, `git status`, remote branches and final GitHub file tree. Push `main` to `https://github.com/BeatyXO/CoverageSeal` and confirm the remote SHA.

**At the end, report** exactly what changed, what tests truly ran (count/pass/fail), live contract addresses/tx IDs/explorer proof (if produced), pinned fixture commit, final pushed Git SHA, and any outstanding limitations. No completion claim until the repository contains your committed final work.
