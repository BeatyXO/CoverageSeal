# Threat model & limitations

**Leader-forged FULL:** code/quote shape is insufficient; validator independently fetches digest-matched bytes and reruns classification, and verifies the leader excerpt occurs in its own source.

**Fabricated contradiction / evidence poisoning:** two independently fetched documents are required; both quoted excerpts must be grounded. An adversarial document contains untrusted text and is explicitly marked as data in prompts. Prompt injection is still an LLM risk; adversarial tests should include injected instructions and source confusion.

**Mutable URL, source swap or Git branch drift:** the package commits expected Keccak-256 digests and schema source namespace. A changed web body returns `UNAVAILABLE`, not silent reclassification. Live fixtures must use raw GitHub URLs pinned to a real 40-hex commit.

**SSRF:** schema namespaces require ordinary ASCII DNS labels and HTTPS, and reject IP literals (including integer/octal spellings), credentials, ports, IDN/punycode labels, local/test suffixes, query/fragment delimiters, percent escapes and dot/empty path segments. Artifact paths are restricted to unescaped ASCII URL path characters below that frozen prefix. This is a lexical guard only: contract code cannot resolve DNS or control the GenVM web client redirect policy. DNS rebinding and redirects to private/link-local addresses therefore remain runtime-level limitations; do not describe this IC as a complete SSRF boundary.

**Missing evidence and contradictions:** an incomplete assessment matrix or an unadjudicated pair blocks finalization. A material contradiction blocks `COMPLETE` even if other evidence is full. Optional requirements are not a channel to hide conflicts.

**Repeated document count:** duplicate content digests are blocked but independent source origin is **not proven**. Corroborate is a different primitive. For independence-critical workflows, consume a separate source-independence oracle.

**Semantic uncertainty:** validators may legitimately disagree on qualitative coverage, especially composite requirements, causing transaction rejection. Narrow criteria, stable source material and bounded fixture tests are essential. Do not falsely claim deterministic LLM agreement.

**Cost and liveness:** worst case `8 requirements × (8 edges + 28 pairs)` semantic writes; no single monolithic all-sources LLM. Completeness is not necessarily economical at the maximum. Documents beyond 24 KB are unavailable, deliberately bounded.

**Consumer replay:** gate has a one-shot `action_hash` receipt, typed `is_complete` view read and complete schema/package/snapshot hash pinning. Cross-contract reads must be tested on actual StudioNet; static presence alone isn't proof.

**Malformed model output:** exact response keys and primitive types are required. Numeric strings, booleans, unexpected keys, overlong excerpts and overlong rationale fail closed as ambiguous; excerpts are never truncated into apparently valid evidence.
