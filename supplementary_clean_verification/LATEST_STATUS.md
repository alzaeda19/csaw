# CSAW latest evidence and submission handoff — 2026-11-11

This is a read-only evidence review, not a fresh HDL/model experiment. Source files, original challenge materials, old repository and existing bundles were not edited. New review records are confined to this folder. No published solutions or contaminated work were consulted. GitHub creation/push belongs to the coordinating chat.

## Current technical evidence

| Evidence | Saved result and limitation |
|---|---|
| Recovered baseline → actual regenerated binary decode | Direct transition proof covers all 135 related state bits and three outputs; both fixed-schedule, independent-initialization transaction modes pass. 352 paired simulated transactions/model; 24/24 original-host known answers/model. The later equivalence report supersedes the older build chat's unresolved status. |
| Baseline readiness | Immediate first-BUSY-low read still fails 8/8 known-answer observations/model. Equivalence preserves this failure; it does not establish readiness correctness. |
| Separate readiness repair | Strict boundary bench: baseline 14 failures/1,122 checks; repaired derivative 1,122/1,122 pass. 864 differential comparisons over 432 operations match the baseline's original-host schedule. Intentional behavior change; not exact recovery. |
| ROM disabled-read coverage | 67,584 assertions across 6,144 scenarios pass; eight synthetic omitted-enable controls rejected. Earlier RE-disabled check was nondiscriminating and remains documented. |
| Synthesis/fit/timing | Baseline/repaired: 1,443/2,920 of 5,280 packed logic cells; estimated internal Fmax 35.8243/29.2543 MHz. Tested 1 MHz route passes under assumed UP5K/SG48 and automatic pins. No verified board PCF, external timing or hardware validation. |
| Repaired RTL versus mapped netlist | Fourteen simulation pairs agree; 1,115 common checks/candidate pass, with seven unavailable internal monitors untested. Matched-state 135-bit transition proof passes; independent-state reset 8-step proof passes; unrestricted longer attempt times out. |
| One/two complete transactions | Prescribed one-transaction proofs pass both modes. Two-transaction mode pairs 00, 01, 10, 11 pass for all 2^64 payload pairs per pair, 141 solver states, without intervening reset. Fixed spacing/mode-change point; arbitrary schedules/unbounded independent-power-up equivalence unproved. |
| Four baseline detectors | HT1–HT4 all CLEAN, 0/4 votes, recorded exit 0 November 10. Exact extraction failed on SBRAM404K; classifications concern a coarse fallback graph omitting RAM internals. No Trojan-free certification or calibrated compromise probability. |

All six originals freshly match size/SHA256/Git-blob receipts. A reviewer also checked25 selected report/result/proof-log entries against saved manifests. No tests were rerun for this review.

## Package contents and omission

Existing archive:
`/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/outputs/CSAW_submission_review_2026-11-11.zip`

SHA256 `24563946d5a809ee3ed2c1afd10f63c06e5decbbdd5591815a80e43c61f9506b`; 6,876,751 bytes; 753 entries; CRC check passes. Reviewer verified 752 manifested entries with no size/hash or membership discrepancies, plus the manifest itself.

The package includes the baseline, regenerated binary, later completed baseline-equivalence evidence, and all 190 files of the available November 10 AI-log recovery bundle byte-identically. It does not include the standalone repaired RTL/netlist and readiness, ROM, synthesis, post-synthesis, reset-transaction or two-transaction technical report bundles. The historical AI export includes the two-transaction final message, which is not a replacement for its technical evidence. November 11 detector readback also postdates package sealing and is absent.

Use `SAFE_ARTIFACTS.json` for explicit source paths/hashes of existing supplementary reports/receipts. This is an inventory, not a new submission or a claim that every listed report's full dependency tree was packaged. Keep repaired derivative distinct from recovered baseline and the auto-pin board image.

## AI records and Claude

The available November 10 recovery index reports 2,271 distinct bounded native records: 378 additional and 1,893 carried forward, including 36 finals. Earlier overlapping exports must not be added again. All 17 clean-stage prompt/final pairs existed in the authentic earlier clean export; old indexes saying their finals are absent are stale. Recoveries include 89 Mac-root records, 18 bitstream-root completion records and 42 detector-tail records; 14 of the latter cover the baseline root completion.

Remaining gaps: encrypted collaboration text; 13 historical truncated records and two compaction boundaries; omitted mixed/pre-clean history; unmapped chats and original Claude histories; exporter/recovery-worker and later packaging/readback activity outside snapshots. Hash consistency is not provider attestation or project-wide completeness.

The package retains an actual one-shot Claude CLI review under `core_evidence/verification/detector_comparison_and_reviews/`: input, response and exit 0 command receipt, session 76afd5f6-79d8-4a0e-a493-8dae812ec2fd. Recorded modelUsage labels are `claude-opus-4-8[1m]` and `claude-haiku-4-5-20251001`. This is not an original Claude web-history export or review of later experiments. No Claude web-conversation URL was found in the scoped indexes. Current CLI reports 2.1.187; no Claude connector was available in this tool session. Opus 5.5 availability is not verified. No new Claude inference was launched by this review.

This folder preserves actual read-only command receipts and exact selected visible chat items from the latest relevant turns. These are scoped extracts, not a complete native export. The current review's full native log and final response are not separately exported here; no missing text was invented.

## Exact submission gaps

1. Original assignment's modified RTL and demonstration testbench are absent from the partial package.
2. Full technical-brief and comprehensive AI-log compliance are not established.
3. Instructor approval of alternative defensive scope remains unconfirmed; do not present this package as fully compliant.
4. Supplementary repaired-derivative technical artifacts should accompany any claims about that work.
5. Board package/pins/electrical constraints/external timing and physical validation remain unverified. Do not program the automatic-pin binary.
6. Current course submission destination and authoritative deadline remain unverified. The original qualifier preserves a historical Google Form; a GitHub push is not itself a course-submission receipt.

The prior user-stated date was November 13, 2026, 3 PM Eastern. The latest human message said 30 hours in a turn beginning November 11, 10:15:37 AM Eastern; arithmetic yields approximately November 12, 4:15 PM Eastern. This is a conflict between user-provided scheduling evidence, not instructor confirmation. Use the tighter window operationally until confirmed.

## Account and preservation

Fresh 17:10:50 UTC check: authenticated GitHub account `alzaeda19`; `alzaeda19/csaw` lookup returned not found at that instant. Only the coordinator may create/push; this review made no GitHub writes. Original repository remains clean at `a3006f61f55fd8b6a232377d292fcec3138bf1ae`. No professor message, portal submission, hardware programming, presentation creation or Paper 5 changes occurred in this review.

