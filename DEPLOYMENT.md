# Stable StudioNet deployment and lifecycle proof

**Network:** StudioNet only, chain ID **61999**, RPC `https://studio.genlayer.com/api`.

Contract source revision: `447464f6b52d4942bd78e6c1a15a7b742617dcb2`. Final submission revision: `git rev-parse HEAD` after checkout of `main`.

## Corrected deployment pair

The finalization correction checks `detail['unresolved']` before snapshot creation, including when status is CONFLICTED. This genuine behavior change required redeployment. The earlier pair and its 38 reverified receipts remain in the archived proof; they are superseded.

| Contract | Address | Finalized deployment transaction |
| --- | --- | --- |
| coverage_seal | [0x9870C77C84DA42785B115457669dCccbfa77994D](https://explorer-studio.genlayer.com/address/0x9870C77C84DA42785B115457669dCccbfa77994D) | [0x9a635735c439a573ec42d5d4bbee0f98ee9df9de729f39dedf6c2af07ab4d455](https://explorer-studio.genlayer.com/tx/0x9a635735c439a573ec42d5d4bbee0f98ee9df9de729f39dedf6c2af07ab4d455) |
| coverage_gate | [0x7498e0B11358C21d977727F6b9c21b5a88264867](https://explorer-studio.genlayer.com/address/0x7498e0B11358C21d977727F6b9c21b5a88264867) | [0x37a35f4098bafa025db6d00ce7f98f12a59f3661f554ecd781752866bf5da888](https://explorer-studio.genlayer.com/tx/0x37a35f4098bafa025db6d00ce7f98f12a59f3661f554ecd781752866bf5da888) |

Both deployments have FINALIZED status, MAJORITY_AGREE consensus and leader-mode SUCCESS execution. The decoded CoverageGate constructor pins the CoverageSeal address above; source inspection confirms this field is initialized once and never reassigned.

## Deployed-source correspondence

Sources were retrieved with `gen_getContractCode`, decoded from base64 as UTF-8, converted from CRLF/CR to LF, and given exactly one terminal LF. No other whitespace, annotation, comment or code changes are ignored. SHA-256 is computed over those UTF-8 bytes.

| Contract | Matching local and deployed SHA-256 |
| --- | --- |
| coverage_seal | `0958d56ba2316616332e36a4137d2305ddc4e3e6fcd150c94aed05511823ef0a` |
| coverage_gate | `6b9e6ea227bd7e9ae10d7b13bd6b46e748eb5f91ed1277f391aff75161c8a934` |

## Finalized live evidence

| Case | Result | Final transaction |
| --- | --- | --- |
| Two requirements, two artifacts; all four edges and both positive pairs assessed | COMPLETE (2) | [0xf8006f2bf5dde1c7b6b1ff79804605e1b2ddd4f6c6f26c47765d0e5473bfcdfc](https://explorer-studio.genlayer.com/tx/0xf8006f2bf5dde1c7b6b1ff79804605e1b2ddd4f6c6f26c47765d0e5473bfcdfc) |
| Required finance evidence missing | INCOMPLETE (3) | [0xb5f6f76efe0eb7914d807d9a496f9839ee81420dda0ace2f20fca5a73ed43abe](https://explorer-studio.genlayer.com/tx/0xb5f6f76efe0eb7914d807d9a496f9839ee81420dda0ace2f20fca5a73ed43abe) |
| Two FULL incident reports; CONTRADICTS pair | CONFLICTED requirement (4), INCOMPLETE package (3) | [0xd71893d6d1d18c433335fc27e484d06a8cf7d98810caba1dc3381b84f337f840](https://explorer-studio.genlayer.com/tx/0xd71893d6d1d18c433335fc27e484d06a8cf7d98810caba1dc3381b84f337f840) |
| Exact complete certificate | SUCCESS; execution receipt persisted | [0xfabb4b9bf6054425212e6a61e0883783aa5e532133c2b58e5fdc3771d1b78b55](https://explorer-studio.genlayer.com/tx/0xfabb4b9bf6054425212e6a61e0883783aa5e532133c2b58e5fdc3771d1b78b55) |
| Wrong package hash | Rollback: coverage certificate missing or mismatched | [0x0f0c4454733f761f14f50277df923bd002a2ebee5a41eb438e964008e07893c9](https://explorer-studio.genlayer.com/tx/0x0f0c4454733f761f14f50277df923bd002a2ebee5a41eb438e964008e07893c9) |
| Duplicate action hash | Rollback: action replay | [0xa870ff6dd46df9cc35e79045743deed7fd1af216de649d18ca07564437bad939](https://explorer-studio.genlayer.com/tx/0xa870ff6dd46df9cc35e79045743deed7fd1af216de649d18ca07564437bad939) |
| Exact incomplete certificate | Rollback: coverage certificate missing or mismatched | [0x7f769823bf50e43c388dc89df81507f55015b24f320a6f414b4559cec237e210](https://explorer-studio.genlayer.com/tx/0x7f769823bf50e43c388dc89df81507f55015b24f320a6f414b4559cec237e210) |

## Certificate pins

| Package | Schema | Manifest | Snapshot |
| --- | --- | --- | --- |
| complete | `9c03b9b84c7e93f6060d19c0c2ecef4bf88743e427fb4c8b5ccbc650f2d5053e` | `adff5c6906d20151552d12e965274bd4abb23b132eb6cd2ce0913bd5fabaee51` | `31a711fb8f391c9435e9b45bd67651a9dc117214c43f5ffbf1fb68367151f4fb` |
| missing | `9c03b9b84c7e93f6060d19c0c2ecef4bf88743e427fb4c8b5ccbc650f2d5053e` | `828f5fab9ec765d5a0c158bc9628db6bd7c181b6a1e05856cedc6216bcea2bc9` | `082e20aec394c901fd1853739ab15ea57933f9c76039e2b70e059bce69930d4f` |
| conflict | `aa6500b96905584406274b0055177a6c35f17f04ba44f7c518bb847f4f10309f` | `00ff8df21215a75d61cacee12d1b1e27c778e694819bac514ef32fcb95bfaf7e` | `333affb45a5e549f9481ffaecb971552be8675fad7c439635c10c7a2601e39e9` |

All 38 closeout transactions were re-read until FINALIZED. Receipt verification checks consensus and leader-mode execution separately; cancelled idle validators are not confused with the leader. Every rejection's result bytes have rollback discriminator 1 and the exact recorded reason. Finalized-state read-backs match the three certificates and persisted consumer action.

The source, detailed edge/pair results, hashes and receipts are in [verified-studionet.json](proof/verified-studionet.json) and [closeout-journal.json](proof/closeout-journal.json). All five pinned fixture URLs were freshly fetched and matched the manifest Keccak-256 digests.

## Toolchain and checks

Python 3.12; GenLayer CLI 0.39.1; GenVM Linter 0.11.0; Testing Suite 0.29.2; official GenVM v0.3.0-rc7 `genvm-runners-all.tar.xz`, SHA-256 `e218a1854214681560351051f76fe2b878545cf3409455ef372d57014a88ca67`.

[Engineering CI](https://github.com/BeatyXO/CoverageSeal/actions/runs/39218358805) succeeded on `447464f6b52d4942bd78e6c1a15a7b742617dcb2`. The final submission commit runs the same workflow: compilation; 4 unit tests; all 19 original Direct Mode tests plus 1 regression; final structural preflight; `check`, `validate`, `typecheck --strict`, and ABI generation for both contracts. Strict checking retains runtime validation and uses narrowly scoped annotations at untyped SDK boundaries.

Run the Quick start in README to prepare the checksum-verified compatibility cache before Direct Mode. The archive is copied unchanged from the linter cache to the cache filename expected by Testing Suite 0.29.2.

## Limits

`gen_getTransactionLifecycle` returns `-32601`, `Method not found: gen_getTransactionLifecycle`. Supported `eth_getTransactionByHash` receipts provide final status, consensus and leader execution. StudioNet transient HTML responses and its 30-request/minute rate limit were handled with read retries and a resumable transaction journal.

CoverageSeal establishes semantic coverage against sealed requirements. It does not independently establish supplied documents as truthful, authoritative or genuinely independent. URL restrictions remain lexical and rely on the GenVM runtime for DNS and redirect controls.
