# Bounded clean-project AI log recovery — November 10, 2026

**Recovered 378 additional visible native records relative to the checked exports, and reverified/carried forward 1,893 existing records. This portable bundle contains 2,271 distinct native records, including 36 final-answer records. It does not establish complete project-wide AI logs.**

Counts are native record counts, not unique conversational turns or commands. A command invocation and its execution/output can be separate records. Each session manifest identifies source files, lines, threads and available turn IDs. Current coordinator work is bounded by its snapshot; it is not a completed conversation export.

| Scope | Additional records | Existing records carried forward | Result |
|---|---:|---:|---|
| Historical clean chat, 17 stages | 0 | 1,305 | All 17 prompts and 17 finals already existed in the November 7 export |
| Earlier bitstream snapshot | 0 | 587 | Portable filtered projection of 597 earlier records |
| Mac infrastructure root task | 89 | 0 | First bounded root-task export; final recovered |
| Bitstream root completion | 18 | 0 | Post-snapshot records and final recovered |
| Baseline/AES detector completion | 42 | 0 | Two root finals and report/checksum records recovered |
| Coordinator clean AES setup | 32 | 0 | Bounded setup/verification task and finals |
| Coordinator comparison/current work and review child | 197 | 1 | One source user request was already exported |
| **Total** | **378** | **1,893** | **2,271 distinct native records** |

The older consolidated index's missing baseline_recovery and baseline_followup finals were found in an existing authentic export; they were not newly generated. They are now directly available at [baseline recovery final](historical_clean/finals/01a1b177-6f8e-73f2-853f-64c8d11e662d.txt) and [baseline followup final](historical_clean/finals/01a1b193-429c-7521-8e9e-e69cb31bfc2c.txt). Protocol-harness and source-intake finals were also already present. [All 17 stage mappings](historical_clean/INDEX.md).

## Where to read

- [Historical clean chat](historical_clean/INDEX.md): portable prompts, finals and structured tool/command records.
- [Mac and bitstream recovery](bitstream_and_mac/INDEX.md): two recovered root finals, earlier bitstream projections and explicit omissions.
- [Detector completion recovery](detector_tails/README.md): baseline and AES completion records with native boundaries.
- [Coordinator comparison/current-work index](coordinator/RECOVERY_INDEX.json) and [earlier clean AES setup](coordinator/earlier_clean_aes_reference/RECOVERY_INDEX.json).
- [Combined index](RECOVERY_INDEX.json), [independent consistency check](records/FINAL_VERIFICATION.json), and [AI-record scope](AI_RECORD.md).

## Remaining gaps and exclusions

1. Encrypted collaboration bodies remain unavailable in readable form. No decryption or reconstruction was attempted. Invocation metadata and omission references are retained where available.
2. Original truncated output is still truncated. The historical clean chat contains 13 native output records with truncation markers and two compaction boundaries. Missing words cannot be restored from these records.
3. Hidden reasoning and system/developer/platform messages are excluded. Ten instruction-output records and 46 encrypted argument fields were removed from the portable earlier-bitstream projection. Original source files remain unchanged. Other original visible tool evidence may include ordinary local-guidance file reads; these are tool observations, not hidden system/developer messages.
4. Chat-read output elements that embedded mixed earlier history were omitted entirely. Pre-clean/solution-contaminated history and the coordinator's initial pasted-history task were excluded. No published solutions were opened.
5. The coordinator snapshot ends at native line 501; its precise timestamp and the readiness-review child's separate cutoff are in the combined index and session manifests. The present recovery workers, current final replies and final submission packaging after those cutoffs are outside this bounded export.
6. Only enumerated native sources and prior exports were checked. Other original Claude conversations, unrelated sessions and unmapped chats were not exported. Global completeness, exact serving-model identity and provider attestation are not established.

These records narrow the AI-log gap. They do not complete missing technical assignment deliverables or establish that the comprehensive-log requirement is fully satisfied.

## Integrity and execution limits

Parent verification checked all 2,271 unique source-line identities, 15,753 retained fields under documented schema rules, 166 sub-bundle file hashes, and 392 existing detector/source hashes. The historical exporter normalizes 388 command record type labels from native `CommandExecution` to `command_execution`; these labels are validated explicitly. Other retained historical payload values match native values. An initial verification mismatch caused by that normalization is documented in records/initial_verifier_schema_mismatch.json; no source content was changed to resolve it.

Repository status and HEAD remain unchanged at a3006f61f55fd8b6a232377d292fcec3138bf1ae. Agents additionally recorded preservation checks for consulted originals. All writes are inside this new recovery folder. Historical commands are records only: no simulation, detector inference, model review, board action, repository edit or experiment rerun occurred during recovery.

SHA-256 manifests provide local consistency checks. They do not make this an immutable archive or prove that no other AI conversations existed.
