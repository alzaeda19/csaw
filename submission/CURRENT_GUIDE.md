# Current submission guide — updated November 13, 2026

**Latest handoff:** [Required versus optional checklist](SUBMISSION_CHECKLIST.md) and [plain-English stealth evidence](addenda/2026-11-13-submission-closeout/STEALTH_IN_PLAIN_ENGLISH.md). All four artifact types are present. Complete relevant AI logs and the stealth objective remain unresolved; key recovery is a bonus and full automation/negligible overhead are higher-score targets. One previously incomplete reviewer tool output has now been fully assembled from authentic captures, as detailed below.

The modified hardware code, demonstration testbench, saved results and submission archive are present. The follow-ups add fresh synthesis, protocol-scoped formal checks, a reference-board pin audit, original-source cipher reconstruction, frozen-design detection evaluation and Qwen review records. They do not change the tested design or rerun the archived original suite; the latest evaluation runs a separate full-core representation-validation suite on both frozen versions.

## Latest investigation of detector misses

The [HT1/HT3 investigation](addenda/2026-11-13-detector-miss-investigation/README.md) is complete. HT3 produces different intermediate arrays for the frozen CSAW pair but identical final numerical summaries and logits. HT1 produces different summaries/scores while still choosing CLEAN. All eight prior CSAW logits reproduce exactly with read-only diagnostics; hardware and model settings are unchanged.

All 23 supplied labeled designs were attempted. On the 18 that pass the fixed graph checks, HT1 detects 9/10 annotated infected designs and falsely flags 5/8 clean designs; HT3 detects 1/10 and falsely flags 3/8. Five PIC16-family examples are unscored due to unresolved internal register references. The report includes all four models, earlier-run comparisons on the same 18 examples, two actual Qwen reviews and explicit corrections to their errors. The ten scored positive examples are all RS232 variants, and checkpoint training overlap is unknown.

The investigation explains measured numerical behavior and records reliability limitations. It does not identify a training-data cause, eliminate false negatives, establish stealth or recover missing historical AI messages.

## Earlier repaired-detector results

The [detector-repair addendum](addenda/2026-11-13-detector-repair/README.md) fixes the specific reference-joining defect on frozen flattened inputs. All 11 benign fixture checks and both dependency/model-input coverage gates passed before classification. HT2 detects the modified design and passes the clean control. HT4 flags both, producing a false alarm on the control. HT1 and HT3 pass both, missing the modification. The unchanged any-positive ensemble flags both.

This is an evaluated dataflow repair, not a complete temporal/physical model, calibrated general accuracy study or stealth result. The earlier raw parser failure remains. No hardware, flattened source, checkpoint or decision rule was changed. The repair and tests were frozen before scores; there was no outcome-driven tuning. All errors and available visible records are saved. The new Trojan-chat review attempt was blocked before a response, so no new Qwen or independent-review result is claimed.

## Earlier detection follow-up

The [frozen-design evaluation](addenda/2026-11-13-detection-evaluation/README.md) is complete. Qwen identifies the added output expression, and the independent bounded formal comparison finds a divergence. Same-flow synthesis confirms added logic/state. Six new full-core simulations each cover 270 transactions and 39,960 sampled output triples; both raw and flattened analysis representations match their original design's tested traces exactly.

All four checkpoints ran on clean/modified inputs in both predeclared representations. Raw inputs fail exact parsing and use incomplete fallback graphs; HT1 flags the modified design. Flat graphs are labeled CLEAN by all four but have thousands of unjoined signal references, confirmed by the independent Trojan-chat review. These diagnostic scores do not establish whole-design stealth. This is a completed negative/limited evaluation, not a positive stealth certificate. The design, thresholds and checkpoints were never tuned to the results. Missing older AI messages remain missing.

The [shared-Claude-chat review](addenda/2026-11-13-shared-chat-review/README.md) reconciles those older conversations with the current package and preserves a new Qwen response with its errors corrected. None supplies verified current stealth evidence. The rubric does not require universal undetectability or all-four-CLEAN labels, and source/formal detection alone is not an automatic failure decision. The recorded limitations and instructor-acceptance uncertainty remain.

## Read these documents together

- [Original technical brief and reproduction directions](README.md): unchanged account of the tested package, including mixed Qwen/Codex authorship, the demonstration, failures and final results.
- [Plain-English encryption explanation](ENCRYPTION_EXPLANATION.md): input-to-output walkthrough, a data-flow sketch, and what each type of evidence establishes. It links to the unchanged detailed source analysis.
- [Recovered cross-app records](addenda/2026-11-12-recovered-records/README.md): the 101-file collection is now integrated, with original hashes, coverage limits and erroneous drafts clearly identified.
- [Extended generation export](addenda/2026-11-12/records/generation_tail/EXPORT_MANIFEST.json) and [reviewer recovery](addenda/2026-11-12/records/reviewer_recovery/README.md): authentic records with original line numbers, hashes, cutoffs and omissions.

The original README, handoff, AI index and manifests are preserved as dated evidence. Their statements about the old export cutoff or pre-upload stage must be read alongside this current guide and [publication status](PUBLICATION_STATUS.md).

## Latest verification follow-up

Read the [new evidence report](addenda/2026-11-12-qwen-verification/README.md) for exact assumptions, measured overhead, all nine board-pin mappings and one-command verification instructions. The cyclic synchronous model has an induction proof for indefinitely many prescribed normal transactions; the edge-explicit model covers two transactions. Both quantify over all allowed words/modes and retain intentional-fault controls. These do not prove the underlying cipher, arbitrary protocol histories or physical timing.

Synthesis adds 36 LUT4 cells, 48 registers and 13 carry cells, with memory unchanged. No negligible-overhead or stealth claim follows automatically. The twelve-step verification workflow reran successfully in a fresh directory; it is validation automation, not historical generation automation. Three Qwen reviews are preserved with explicit corrections to unsupported model claims.

The reference-board mapping is now documented. Physical BUSY is pin 23 and LED pin 38; the unchanged simulation adapter labels the identical logical outputs oppositely. Board-unit/revision compatibility and the earlier automatically pinned bitstream remain unverified. The [new reconstruction](addenda/2026-11-12-cipher-reconstruction/README.md) now establishes the exact round operations and effective key handling: four rounds of fixed-mask XOR, AES byte substitution and one-byte rotation, with the inverse path checked independently.

## What the stronger explanation says

The recovered design accepts one 32-bit word. Its forward path performs four rounds of XOR with a hardwired 32-bit mask, AES byte substitution and one-byte rotation. A separate working-register path performs the inverse concurrently. The mode input selects the completed result at the serial-bank load. The mask stays fixed; there is no normal runtime key load or evolving key schedule.

The analysis also explains an observed limitation: processing status can fall before the result has been copied into the output bank. Under the documented schedule, a further clock with chip-select high performs that copy. This agrees with the existing evidence that immediate reads fail while the original host's longer schedule passes. It is an explanation of the original baseline, not a new fix or hardware timing measurement.

The source inventory identifies the 32 serial registers, 32 working registers, control state, memory connections and registered output. The newer analysis identifies the stored AES S-box after restoring the original bit wiring and verifies the round equations against the untouched original Verilog: 2,564 transactions, 20,512 round-state comparisons and zero failures. The fixed mask is derived internally for reproduction; no numeric bonus-key artifact is emitted. No algorithm was imported from a challenge solution. The separate professor-supplied AES example remains unrelated evidence.

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
| Historical tool output | Original captures retain the **1,546- and 2,535-token truncation markers**. The latter output is now fully assembled from authentic overlapping captures, restoring **10,140 characters**. The first gains four characters but retains a **6,178-character gap**. This is labeled derived assembly, not an invented transcript or a rewrite of the original captures. |
| Earlier full history | Some older project conversations and compacted context remain unavailable. Those are separate from the recovered generation/packaging tail; the qualifier specifically asks for prompts and responses used to generate the modification. |
| Cipher limits after reconstruction | The exact four-round operations, AES S-box ordering and effective fixed-mask handling are established. Author naming/rationale and cryptographic strength remain unverified. Exact byte/control checks and finite end-to-end simulations are not a whole-system proof for arbitrary protocol or physical behavior. |
| Challenge quality and scoring | Stealth remains unestablished. Source/formal checks detect the change. The repaired flattened dependency graphs pass their stated coverage gates: HT2 detects the modification while passing the control; HT4 flags both; HT1 and HT3 miss it. Raw parsing and temporal/physical abstraction limits remain. Normal preservation now has a cyclic synchronous induction proof under explicit protocol assumptions and a bounded edge-explicit check. General behavior outside that scope is unproved. Mapped overhead is measured; negligible physical overhead and full historical generation automation are not established. |
| Instructor receipt | The repository is public at the user's request. Publication does not establish that the instructor has reviewed or accepted the submission. Collaborator invitations remain intentionally skipped. |

Hidden reasoning, platform instructions and unrelated private material are outside the relevant visible generation dialogue. The twelve unreadable reviewer instruction bodies are different: their actual prompt text remains unavailable. Parent and child copies describe the same twelve exchanges. This prevents a claim of an unabridged generation/review trail; unrelated recovered setup history does not replace those prompts.

The original qualifier permits predictable output corruption and requires the brief to disclose the trigger. Disclosure is therefore not, by itself, a failure of the assignment. Its preliminary phase is simulation-only, and key recovery is a bonus; neither board programming nor key recovery is presented here as a mandatory unfinished deliverable. The instructor's original-guidelines direction remains the basis; no defensive-alternative approval is assumed.

## What remains before delivery

All four requested artifact categories are present in the ZIP: modified RTL, demonstration testbench, AI records and technical brief. The archive includes this guide and both explanation/recovery supplements. There is no newly missing board-programming or key-recovery step.

The genuine outstanding issues are completeness of the relevant AI trail, stealth, and behavior outside the explicitly proved normal protocol/model assumptions. Missing reviewers' instructions cannot be supplied from unrelated setup history. If no original copies can be recovered, the gaps must remain disclosed and the instructor must judge their effect; no full-compliance claim is made. The encryption explanation now includes exact original-source round equations and verified key handling. The brief now includes a reference-board pin map, with physical BUSY/LED labels corrected in documentation. A particular board and board-constrained build remain unverified; board execution is still not a required qualifier step. Publication alone does not confirm receipt by course staff. Collaborator invitations remain skipped as requested.

## Preservation and reproduction

All 262 files from the original sealed package, including its seven frozen source/test files and existing records, remain byte-identical. New material is additive. The current publication manifest and ZIP checksum cover the augmented package. Historical manifests and test results retain their original meaning.

To reproduce the existing simulations, follow the original README after extracting the ZIP outside a Git checkout. Earlier documentation-only updates retain their dated scope. The follow-ups run synthesis/formal verification and a new original-baseline reconstruction simulation. They do not rerun the archived modified-design simulation runner or use published challenge solutions.

The new pin-audit records disclose four unreadable peer-task exchanges and three progress messages from documentation review. They are separate from the original twelve generation-review instructions. The earlier three Qwen verification calls and two later cipher-review calls retain requests, received streams and replies, including rejected overclaims. Current record cutoffs and any separate documentation-audit gaps are disclosed in each addendum.

The cipher-analysis audit preserves 93 visible records with exact-value checks and discloses three unreadable peer instruction exchanges plus two unreadable progress messages. These are new documentation-analysis gaps, separate from the historical twelve reviewer instructions and the earlier pin-audit gaps. Both current peer final responses are preserved. Current Qwen prompts and received replies are complete; record cutoffs do not pretend to include future publication messages.

The November 13 bounded records recheck and Qwen review are in [the closeout addendum](addenda/2026-11-13-submission-closeout/README.md). It changes documentation and adds authentic recovered tool-output text; it does not add concealed behavior or claim a new detector result.
