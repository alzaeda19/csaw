# Encryption explanation and AI-record recovery addendum

Prepared November 12, 2026 (Eastern) for review and integration into `submission/addenda/2026-11-12/`. This is a documentation/evidence supplement. It does not replace or modify the sealed original 262-file package, its design, testbench, runner or recorded test results. Integration and GitHub publication belong to the coordinating chat.

## Start here

- [Proposed encryption explanation](explanation/PROPOSED_ENCRYPTION_EXPLANATION.md): original-baseline architecture, data movement, memory role and completion timing, with observations separated from interpretation.
- [Evidence map](explanation/EVIDENCE_MAP.json) and [static inventory](explanation/STATIC_BASELINE_ANALYSIS.json): source hashes and exact line references.
- [Extended selected generation-task transcript](records/generation_tail/VISIBLE_TASK_TRANSCRIPT.md): preserved earlier records plus the recovered packaging tail.
- [Reviewer record recovery](records/reviewer_recovery/README.md): native reviewer sources, overlap with prior exports, exact missing prompt bodies and truncation.
- [Generation-record coverage](records/generation_tail/GENERATION_RECORD_COVERAGE.json): existing Qwen records and exact final-file text found in visible records.
- [Original-package preservation](verification/ORIGINALS_PRESERVATION.json): final byte/hash comparison with all 263 protected artifacts (262 original package files plus the sealed ZIP).

## What improved

The explanation now traces a shared 32-register serial input/readout chain, a separate 32-register working bank, processing control state, direction selection and four initialized memory blocks. Static source inspection shows the memories are not written during normal operation. Their payloads were not decoded. A checked control identity explains why the original baseline needs a CS-high clock after BUSY falls to load the result into the serial bank. These are structural and control findings, not a new cipher identification or key recovery.

The selected parent transcript expands from 155 to **199 retained native records**: all original 155 are unchanged and **44 packaging-tail records are added**. Its boundary is native lines 32–697, ending at the original task-complete event on November 12 at **7:49:30.998 PM Eastern** (00:49:30.998 UTC on November 13). The final user-facing response at line 694 is now included. The old export ended at line 573, before final packaging. All 666 eligible native records are accounted for as 199 retained and 467 omitted.

Reviewer recovery retains **74 native records**, with 231 whole-record omissions across two frozen source prefixes. Two reviewer final responses were absent from the prior reviewer app exports; seven other finals exactly match those exports. Reviewer records can duplicate content in the parent transcript and must not be counted as additional independent interactions. See the comparison ledger for exact overlap.

## Exact remaining gaps

| Category | Current status and implication |
| --- | --- |
| Visible generation/review input records | **12 delegation/steering prompt bodies remain inaccessible**: nine task requests and three messages. Root and child records describe the same 12 exchanges, not 24 separate gaps. They include review/report/record-packaging work that informed the workflow. The routing wrappers and responses do not reconstruct the exact prompt text. |
| Source-truncated tool output | Two report-review outputs retain their original truncation markers, reporting 1,546 and 2,535 omitted tokens. No exporter adds truncation. Full source documents, where separately available, are evidence artifacts rather than replacements for the authentic truncated tool response. |
| Qwen timeout | All three Qwen prompts, received raw streams and native session copies were already preserved. The third run timed out without saving the testbench or producing a completed response. That nonexistent continuation is not a recoverable missing record. Codex saved its validated template; mixed AI authorship remains explicit. |
| Intentionally excluded material | Hidden reasoning, platform/system/developer instructions, encrypted values, inherited prior context and unrelated private content are excluded. Their exclusion must not be presented as missing visible generation prompts or as an automatic rubric failure. |
| Earlier project history | This supplement covers the selected generation/correction/packaging task and its reviewers. It does not claim a complete reconstruction of every earlier baseline-recovery conversation. The rubric concerns the relevant generation prompts/responses; unrelated historic chats are not required merely because they exist. |
| Encryption understanding | The architecture and control are explained more precisely. Named algorithm, table semantics, key handling and cryptographic strength remain unestablished. The supplied pair and historical representation-equivalence results do not prove universal encrypt/decrypt inversion. This is a proposed explanation, not a claim that exhaustive cipher proof was required or obtained. |

All script execution in this follow-up was record processing or static source/Boolean analysis. No HDL, modified design or attack code was executed; no design logic, key or board work was performed. Published solutions and shared solution conversations were not consulted. No repository was edited or pushed by this chat.

## Integrity and reuse

Native records carry original line numbers and SHA-256 values; selected source prefixes are separately hashed. Retained text is unchanged, although JSON formatting is normalized. Read each export manifest for its exact boundary, omissions and limits. Original absolute source paths remain in provenance receipts; documentation uses relative links or explicit original-package paths. A top-level MANIFEST.json seals this staging supplement after verification; it excludes itself.

The original local ZIP remains SHA-256 `0c053f3595079dbe7aa11789e69b1e26d359619b7af72d7535d1da004ce0ca83`. The currently published augmented ZIP has its own separate identity, managed by the integrating chat. This addendum makes no claim to have changed or submitted either archive.
