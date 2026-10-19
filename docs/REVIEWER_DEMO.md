# Reviewer demonstration (executed on stable StudioNet)

Use stable `studionet` / chain **61999** / `https://studio.genlayer.com/api` only. The manifest and fixture namespace are pinned to a pushed immutable fixture commit:

`https://raw.githubusercontent.com/BeatyXO/CoverageSeal/1ddcce53a43099fa25ec651a1bc06646f4a4771d/fixtures/`

The live deployment addresses, finalized transaction IDs, hashes, and status values are in `proof/verified-studionet.json`.

## Positive complete case (verified)

The two pinned documents each support both required dimensions: Atlas Labs ownership percentages and 2024/2025 revenue. Assess every requirement × artifact edge. Since both documents positively cover each requirement, assess each positive-positive pair before finalizing. The finalized two-requirement package and consumer action are recorded in `proof/verified-studionet.json`.

## Negative cases (live and Direct Mode)

- A package containing only `ownership_only.txt` leaves required `FINANCES` missing and finalizes `INCOMPLETE` (status 3), not `COMPLETE`.
- Direct Mode: `PARTIAL` under `REQUIRE_FULL` does not satisfy the requirement.
- `incidents_clear.txt` and `incidents_conflicting.txt` both returned `FULL`; their pair returned `CONTRADICTS` with excerpts from both sources. The requirement finalized `CONFLICTED` and the package finalized `INCOMPLETE`.
- Direct Mode: changing source content without changing expected digest returns `UNAVAILABLE` (edge 5).
- The live gate rejected a wrong package hash, a replayed action hash, and the finalized incomplete package. Each transaction finalized with the expected rollback reason.

Transaction hashes and finalized statuses for the completed cases are in `proof/verified-studionet.json`.

The corrected deployment pair and all final receipt references are canonical in `proof/verified-studionet.json`. The 20 Direct Mode cases also verify that a conflict cannot hide an unresolved assessment, and that independently rerun edge and pair validators reject fabricated quotes, digest substitution and semantic disagreement. The historical pair is superseded.
