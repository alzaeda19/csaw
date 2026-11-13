# Current submission guide — November 12, 2026

The modified hardware code, demonstration testbench, saved results and submission archive are present. The latest update adds fresh synthesis, protocol-scoped formal checks, a reference-board pin audit and Qwen review records. It does not change the tested design or rerun the original simulation suite.

## Read these documents together

- [Original technical brief and reproduction directions](README.md): unchanged account of the tested package, including mixed Qwen/Codex authorship, the demonstration, failures and final results.
- [Plain-English encryption explanation](ENCRYPTION_EXPLANATION.md): input-to-output walkthrough, a data-flow sketch, and what each type of evidence establishes. It links to the unchanged detailed source analysis.
- [Recovered cross-app records](addenda/2026-11-12-recovered-records/README.md): the 101-file collection is now integrated, with original hashes, coverage limits and erroneous drafts clearly identified.
- [Extended generation export](addenda/2026-11-12/records/generation_tail/EXPORT_MANIFEST.json) and [reviewer recovery](addenda/2026-11-12/records/reviewer_recovery/README.md): authentic records with original line numbers, hashes, cutoffs and omissions.

The original README, handoff, AI index and manifests are preserved as dated evidence. Their statements about the old export cutoff or pre-upload stage must be read alongside this current guide and [publication status](PUBLICATION_STATUS.md).

## Latest verification follow-up

Read the [new evidence report](addenda/2026-11-12-qwen-verification/README.md) for exact assumptions, measured overhead, all nine board-pin mappings and one-command verification instructions. The cyclic synchronous model has an induction proof for indefinitely many prescribed normal transactions; the edge-explicit model covers two transactions. Both quantify over all allowed words/modes and retain intentional-fault controls. These do not prove the underlying cipher, arbitrary protocol histories or physical timing.

Synthesis adds 36 LUT4 cells, 48 registers and 13 carry cells, with memory unchanged. No negligible-overhead or stealth claim follows automatically. The twelve-step verification workflow reran successfully in a fresh directory; it is validation automation, not historical generation automation. Three Qwen reviews are preserved with explicit corrections to unsupported model claims.

The reference-board mapping is now documented. Physical BUSY is pin 23 and LED pin 38; the unchanged simulation adapter labels the identical logical outputs oppositely. Board-unit/revision compatibility and the earlier automatically pinned bitstream remain unverified. Full cipher/key semantics are still unknown, although fixed-table properties and the lack of a separately documented runtime key transaction are now evidenced.

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
| Internal cipher mathematics | Architecture, fixed-table properties and the documented external key-interface boundary are evidenced. Exact algorithm identity, round equations, embedded key semantics and cryptographic strength remain unestablished. |
| Challenge quality and scoring | Stealth remains unestablished. Normal preservation now has a cyclic synchronous induction proof under explicit protocol assumptions and a bounded edge-explicit check. General behavior outside that scope is unproved. Mapped overhead is measured; negligible physical overhead and full historical generation automation are not established. |
| Instructor receipt | The repository is public at the user's request. Publication does not establish that the instructor has reviewed or accepted the submission. Collaborator invitations remain intentionally skipped. |

Hidden reasoning, platform instructions and unrelated private material are outside the relevant visible generation dialogue. The twelve unreadable reviewer instruction bodies are different: their actual prompt text remains unavailable. Parent and child copies describe the same twelve exchanges. This prevents a claim of an unabridged generation/review trail; unrelated recovered setup history does not replace those prompts.

The original qualifier permits predictable output corruption and requires the brief to disclose the trigger. Disclosure is therefore not, by itself, a failure of the assignment. Its preliminary phase is simulation-only, and key recovery is a bonus; neither board programming nor key recovery is presented here as a mandatory unfinished deliverable. The instructor's original-guidelines direction remains the basis; no defensive-alternative approval is assumed.

## What remains before delivery

All four requested artifact categories are present in the ZIP: modified RTL, demonstration testbench, AI records and technical brief. The archive includes this guide and both explanation/recovery supplements. There is no newly missing board-programming or key-recovery step.

The genuine outstanding issues are completeness of the relevant AI trail, stealth, and behavior outside the explicitly proved normal protocol/model assumptions. Missing reviewers' instructions cannot be supplied from unrelated setup history. If no original copies can be recovered, the gaps must remain disclosed and the instructor must judge their effect; no full-compliance claim is made. The encryption proposal is present but remains architectural. The brief now includes a reference-board pin map, with physical BUSY/LED labels corrected in documentation. A particular board and board-constrained build remain unverified; board execution is still not a required qualifier step. Publication alone does not confirm receipt by course staff. Collaborator invitations remain skipped as requested.

## Preservation and reproduction

All 262 files from the original sealed package, including its seven frozen source/test files and existing records, remain byte-identical. New material is additive. The current publication manifest and ZIP checksum cover the augmented package. Historical manifests and test results retain their original meaning.

To reproduce the existing simulations, follow the original README after extracting the ZIP outside a Git checkout. Earlier documentation-only updates retain their dated scope. The latest follow-up runs synthesis and formal verification of unchanged files; it does not rerun the archived simulation runner or use published challenge solutions.

The new pin-audit records disclose four unreadable peer-task exchanges and three progress messages from documentation review. They are separate from the original twelve generation-review instructions. All three new Qwen calls retain their requests, received streams and replies, including rejected overclaims.
