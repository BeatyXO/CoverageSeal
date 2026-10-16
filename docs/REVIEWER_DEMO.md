# Reviewer demonstration (intended workflow, not claim of execution)

Use stable `studionet` / chain **61999** / `https://studio.genlayer.com/api` only. Raw fixture namespace after first real GitHub push:

`https://raw.githubusercontent.com/BeatyXO/CoverageSeal/FIXTURE_COMMIT_PLACEHOLDER/fixtures/`

Pin first with `python scripts/pin_fixture_commit.py <real-40-char-commit>` and commit/push that pin. `fixtures/demo_manifest.json` then contains URL/digest pairs.

## Positive complete case

1. Deploy `contracts/coverage_seal.py` (no constructor args).
2. `create_schema("Atlas evidence package", pinned_source_prefix)`.
3. `add_requirement(schema_id,"OWNERS","Identify Atlas Labs owners and their ownership percentages",1,0)`.
4. `add_requirement(schema_id,"FINANCES","Provide revenue figures for 2024 and 2025",1,0)`.
5. `seal_schema` and save definition hash.
6. `create_package(schema_id, definition_hash)`.
7. `add_artifact` for `ownership.txt` and `finances.txt` with the committed digests from manifest.
8. `seal_package`; save package hash.
9. For both requirements, assess BOTH documents (4 edges). For each requirement, only one fixture should be positive. If both are positive, assess the positive-positive pair before finalization; never skip a required pair.
10. `finalize_package`; inspect status 2 (`COMPLETE`) and snapshot hash. Verify `is_complete(package_id, schema_hash, package_hash, snapshot_hash)` is true, and false with any wrong hash.
11. Deploy `contracts/coverage_gate.py`, passing the **finalized** CoverageSeal address. `execute(package_id,schema_hash,package_hash,snapshot_hash,action_hash,payload_hash)` with fresh 64-hex action/payload values. Confirm execution receipt; repeat action and wrong hash must revert.

## Negative cases

- Missing required financial document leads to `INCOMPLETE` (status 3), not `COMPLETE`.
- `PARTIAL` under `REQUIRE_FULL` does not satisfy the requirement.
- Both `incidents_clear.txt` and `incidents_conflicting.txt` should be classified `FULL` against a suitable `"Describe production incidents in 2025"` requirement, then the pair should be `CONTRADICTS`; expected requirement status `CONFLICTED`. Do not fabricate outputs if models disagree.
- Changing source content without changing expected digest returns `UNAVAILABLE` (edge 5).
- Unknown, unsealed, unassessed or mutable package cannot pass `is_complete`.

Log actual tx hashes and addresses only after they exist and are finalized.
