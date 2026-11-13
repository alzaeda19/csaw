# Verified results and exact test boundaries

This document replaces vague readiness wording with results recorded in the saved evidence. It reports existing measurements; no new experiment or hardware change was performed for this wording update. Historical reports and proof files remain unchanged.

## Normal-operation evidence

- The saved baseline and modified ordinary simulation runs each record 88 transactions and 6,726 checks with zero failures. The demonstration records 39,718 passing checks. Deliberately broken controls fail their tests. These are check counts, not that many independent input words. See the [artifact checklist](SUBMISSION_CHECKLIST.md) and original [technical brief](README.md).
- The [formal verification result](addenda/2026-11-12-qwen-verification/analysis/VERIFICATION_RESULTS.json) records a successful base case and temporal-induction step at length 100 for the cyclic synchronous model. Its harness resets once and repeats an 80-cycle transaction schedule.
- That harness uses complete 32-bit frames, a mode held stable through each transaction, the prescribed start/processing/readout sequence and idle interval. It allows arbitrary permitted words and modes per transaction. The previously disclosed intentional encryption fault case is excluded from the normal-case proof and included in negative controls, which fail as expected.
- The separate explicit-clock model checks two transactions over 325 global samples. It is bounded; it is not the unbounded induction model.
- The proof abstracts the common core and checks that the wrapper does not alter sampled outputs under those encoded conditions. It does not prove the original cipher's correctness. The later [cipher reconstruction](addenda/2026-11-12-cipher-reconstruction/README.md) provides separate original-source and simulation evidence.
- No result in those formal records establishes behavior for every malformed frame, changing mode mid-transaction, clock glitch, metastability or physical-board timing. No physical board was tested in these follow-ups.

These conditions are facts about the models that were checked. They are not measurements showing that every possible hardware interaction follows that schedule. Removing them from a claim would change what the proof says.

## Detector results

The frozen CSAW pair yields CLEAN/CLEAN for HT1 and HT3, CLEAN/TROJAN for HT2, and TROJAN/TROJAN for HT4. For HT3, different intermediate arrays produce a byte-identical final numerical summary; all eight diagnostic replay logits match the prior saved values exactly.

All 23 supplied toy examples were attempted. Eighteen passed the graph checks: 10 annotated infected RS232 variants and 8 annotated clean designs. HT1 detected 9/10 infected cases and falsely flagged 5/8 clean cases; HT3 detected 1/10 and falsely flagged 3/8. Five PIC16-family examples failed coverage due to an unresolved internal register reference and received no score. These counts describe that subset; the records do not identify the checkpoint training sets or establish general accuracy. See the [measured investigation](addenda/2026-11-13-detector-miss-investigation/README.md).

The results include detection of the submitted modification. They do not establish a successful stealth claim.

## Hardware and cipher measurements

Identical synthesis settings produce 1,439 versus 1,475 LUT4 cells, 71 versus 119 registers, 0 versus 13 carry cells, and four RAM4K blocks in both designs. These are mapped resource counts; no physical timing/power or negligible-overhead result follows from them. See [the measurements](addenda/2026-11-12-qwen-verification/analysis/OVERHEAD.json).

The original-source reconstruction identifies a custom 32-bit, four-round transform using fixed-mask XOR, AES byte substitution and byte rotation, with an inverse path. Its saved checks record 2,564 transactions and 20,512 internal round-state comparisons with zero failures. This is not standard AES-128. No numeric bonus-key submission is claimed.

## Records and delivery

The modified RTL, demonstration testbench, technical brief, available AI records and ZIP exist. Twelve original reviewer instruction bodies and 6,178 characters of one historical output remain unavailable in the recovered records. No text has been invented to replace them.

The user selected public GitHub for the course handoff and skipped collaborator invitations. The repository is public. The separate competition form has not been submitted by this work, and no staff-acceptance receipt is recorded. Jason's reported direction is to follow the original guidelines; no approved alternative submission is recorded.

The current [requirements audit](addenda/2026-11-13-final-requirements-audit/README.md) distinguishes required artifacts, bonus work and scoring targets. Full challenge compliance has not been established by the saved evidence.
