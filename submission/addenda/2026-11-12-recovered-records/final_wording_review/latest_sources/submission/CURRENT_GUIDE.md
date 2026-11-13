# Current submission guide — November 12, 2026

The modified hardware code, demonstration testbench, saved results and submission archive are present. This update improves the explanation and AI evidence. It does not change the tested design or claim a new simulation run.

## Read these documents together

- [Original technical brief and reproduction directions](README.md): unchanged account of the tested package, including mixed Qwen/Codex authorship, the demonstration, failures and final results.
- [Plain-English encryption explanation](ENCRYPTION_EXPLANATION.md): input-to-output walkthrough, a data-flow sketch, and what each type of evidence establishes. It links to the unchanged detailed source analysis.
- [Recovered cross-app records](addenda/2026-11-12-recovered-records/README.md): the 101-file collection is now integrated, with original hashes, coverage limits and erroneous drafts clearly identified.
- [Extended generation export](addenda/2026-11-12/records/generation_tail/EXPORT_MANIFEST.json) and [reviewer recovery](addenda/2026-11-12/records/reviewer_recovery/README.md): authentic records with original line numbers, hashes, cutoffs and omissions.

The original README, handoff, AI index and manifests are preserved as dated evidence. Their statements about the old export cutoff or pre-upload stage must be read alongside this current guide and [publication status](PUBLICATION_STATUS.md).

## What the stronger explanation says

The recovered design accepts one 32-bit word through a serial input. A separate working register bank processes it through Boolean logic and four initialized memory blocks whose write clocks are disabled. A mode input selects encryption or decryption behavior inside the datapath. The result returns to the serial bank for readout.

The analysis also explains an observed limitation: processing status can fall before the result has been copied into the output bank. Under the documented schedule, a further clock with chip-select high performs that copy. This agrees with the existing evidence that immediate reads fail while the original host's longer schedule passes. It is an explanation of the original baseline, not a new fix or hardware timing measurement.

The source inventory identifies the 32 serial registers, 32 working registers, control state, memory connections and registered output. It deliberately does not identify the stored tables, recover a key or import an algorithm from another solution. The separate professor-supplied AES example is not evidence that this design implements AES.

## What was recovered

The later cross-app supplement preserves 15 Qwen setup attempts, a 100-line prompt-only history, scoped Claude observations and additional own-chat records. Three clean-status messages, fourteen bitstream messages and four selected caveat excerpts supplement earlier history. The final generation files already matched the repository. These additions improve process documentation; they do not resolve the twelve unreadable reviewer instructions. Read the supplement index before interpreting any historical completion or local-only claim.


- The parent export now retains **199 records**, including **44 beyond the old cutoff**, through the original packaging-completion event. The original 155 retained records match exactly.
- **74 native reviewer records** add provenance to the two reviewer histories. They include **two previously unexported final responses**; seven other finals already matched the saved app exports. These numbers are record counts, not distinct prompts or independent reviews.
- All three Qwen attempts have their actual prompts, received streams and native-session copies. The third attempt timed out before a completed response existed. There is no completed response to recover for that attempt.
- The exact final modified RTL, testbench and runner text is corroborated in visible native records. That supports provenance; it does not substitute for an unavailable prompt.

## Exact remaining gaps

| Gap | What is still unavailable or unproved |
|---|---|
| Reviewer instructions | **12 encrypted inbound message bodies:** nine task requests and three steering messages. The parent and child records refer to the same 12 exchanges. None was recovered as plaintext. |
| Historical tool output | Two reviewer outputs contain original truncation markers reporting **1,546 and 2,535 omitted tokens**. The new exporter adds no truncation and does not fabricate the missing text. |
| Earlier full history | Some older project conversations and compacted context remain unavailable. Those are separate from the recovered generation/packaging tail; the qualifier specifically asks for prompts and responses used to generate the modification. |
| Internal cipher mathematics | This is now a concrete proposed architectural explanation. Algorithm identity, table meanings, round equations, key handling and cryptographic strength are still not independently established. A full cipher proof is not claimed. |
| Challenge quality and scoring | Stealth and perfect preservation of normal operation are part of the original challenge and remain unestablished beyond the documented evidence. Low overhead and end-to-end generation automation are also unproved scoring strengths. Saved finite checks are not universal proof. No new synthesis or physical-hardware result is claimed. |
| Instructor receipt | The repository is public at the user's request. Publication does not establish that the instructor has reviewed or accepted the submission. Collaborator invitations remain intentionally skipped. |

Hidden reasoning, platform instructions and unrelated private material are outside the relevant visible generation dialogue. The twelve unreadable reviewer instruction bodies are different: their actual prompt text remains unavailable. Parent and child copies describe the same twelve exchanges. This prevents a claim of an unabridged generation/review trail; unrelated recovered setup history does not replace those prompts.

The original qualifier permits predictable output corruption and requires the brief to disclose the trigger. Disclosure is therefore not, by itself, a failure of the assignment. Its preliminary phase is simulation-only, and key recovery is a bonus; neither board programming nor key recovery is presented here as a mandatory unfinished deliverable. The instructor's original-guidelines direction remains the basis; no defensive-alternative approval is assumed.

## What remains before delivery

All four requested artifact categories are present in the ZIP: modified RTL, demonstration testbench, AI records and technical brief. The archive includes this guide and both explanation/recovery supplements. There is no newly missing board-programming or key-recovery step.

The genuine outstanding issues are completeness of the relevant AI trail and evidence for the original challenge requirements, including stealth and normal-operation preservation. Missing reviewers' instructions cannot be supplied from unrelated setup history. If no original copies can be recovered, the gaps must remain disclosed and the instructor must judge their effect; no full-compliance claim is made. The encryption proposal is present but remains architectural. The brief's future hardware-reproduction detail is also limited by unverified physical pin mapping; board execution is still not a required qualifier step. Publication alone does not confirm receipt by course staff. Collaborator invitations remain skipped as requested.

## Preservation and reproduction

All 262 files from the original sealed package, including its seven frozen source/test files and existing records, remain byte-identical. New material is additive. The current publication manifest and ZIP checksum cover the augmented package. Historical manifests and test results retain their original meaning.

To reproduce the existing simulations, follow the original README after extracting the ZIP outside a Git checkout. This documentation update performed static source inspection and file/record integrity checks only; it did not run the archived design or use published challenge solutions.
