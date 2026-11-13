# Submission checklist — November 13, 2026

**Evidence wording update:** [Verified results and exact test boundaries](VERIFIED_FACTS.md). This states the recorded counts, encoded test conditions and checks that were not performed. No new proof or experiment is claimed.

**Final requirements audit:** [Current-rule comparison and handoff](addenda/2026-11-13-final-requirements-audit/README.md). The required artifacts are assembled; stealth and historical AI-record completeness remain unresolved. No additional detector threshold is a prerequisite to uploading the existing package. The live competition form differs from the earlier saved link; GitHub remains the user-requested course destination.


**The files are assembled and available to hand in. Full compliance with the challenge is not established.** All four required artifact categories and the ZIP exist. The important remaining concerns are completeness of the relevant AI records and the original stealth objective. These should be disclosed, not renamed optional or marked solved.

This comparison uses the preserved [original qualifier requirements](evidence/original_qualifier_README.md). The user specified GitHub as the course destination; the original competition form is a different destination and has not been used. No collaborator invitation or professor message is sent by this update.

## Required files: what is present

| Original requirement | Current submission | Status |
|---|---|---|
| AI-generated modified Verilog | `rtl/modified_protocol_dut.sv`, preserved baseline and dependencies | Present. Records identify Qwen's initial draft and substantive Codex corrections; it is not solely Qwen-authored. The no-human-written-hardware claim is supported by available records, subject to their disclosed gaps. |
| Demonstration testbench | `tb/demo_tb.sv`, `run_tests.py`, recorded successful tests and deliberately broken controls | Present. The saved original and modified ordinary tests each pass 6,726 checks; the demonstration passes 39,718 checks. Actual CSV/VCD traces are included. |
| Comprehensive prompts and AI responses used for generation | `ai/` plus authentic recovered-record addenda | Present but incomplete. Twelve original reviewer instruction bodies remain unreadable. Of two originally truncated reviewer tool outputs, one has now been completely assembled from authentic overlapping fragments; the other retains a 6,178-character gap. This is the main record-completeness concern. |
| Technical brief | Original `README.md`, [current guide](CURRENT_GUIDE.md), [current encryption explanation](ENCRYPTION_EXPLANATION.md), linked verification/pin evidence | Present. Recovery, AI tools/authorship, the disclosed demonstration, future reference-board connections and the cipher explanation are documented. No unsupported stealth claim is added. |
| Delivery ZIP | Repository-root `submission.zip` and `submission.zip.sha256` | Present on public GitHub, with archive/file integrity checked. Publication is not proof of staff receipt or acceptance. |

The unchanged original README contains historical statements such as “not uploaded” and an incomplete cipher explanation. They describe its original packaging stage. Read the current guide and encryption explanation for the verified later findings. Preserving the original README avoids rewriting the provenance record.

## What still cannot be marked complete

1. **The relevant AI trail is not unabridged.** The twelve unavailable reviewer inputs comprise nine task requests and three steering messages; parent/child copies describe the same exchanges. Two original outputs were truncated at capture time. The output marked 2,535 tokens truncated has now been completely assembled from authentic captured fragments, recovering 10,140 omitted characters. The output marked 1,546 tokens truncated gains four characters from the API prefix but still lacks 6,178 characters. The original captures remain unchanged; the recovered text is explicitly labeled a derived assembly. The rule requires comprehensive generation logs and warns about missing logs. We cannot determine how staff will classify these partial review-stage gaps. New summaries cannot replace the missing originals. Other later documentation-audit gaps are tracked separately.
2. **Stealth is unestablished; the completed evaluation shows detection under source/formal review.** The [new frozen-design evaluation](addenda/2026-11-13-detection-evaluation/README.md) records Qwen identifying the output alteration and the independent scoped formal comparison finding a mismatch. The later [detector repair](addenda/2026-11-13-detector-repair/README.md) fixes the flattened reference-joining defect and passes 11 benign fixture checks plus coverage gates before classification. HT2 detects the modified design while passing the clean control; HT4 flags both, including a false alarm; HT1 and HT3 miss the modification. The raw parser and broader temporal/physical abstraction limitations remain. The [subsequent HT1/HT3 investigation](addenda/2026-11-13-detector-miss-investigation/README.md) identifies HT3's identical final summary on the CSAW pair and documents detector reliability on 18 usable supplied examples, with five explicit abstentions. It changes neither the hardware nor these unresolved requirements. All earlier diagnostic scores and errors are preserved; the repaired results do not establish stealth. Describing the trigger in the brief is required and is not itself disqualifying. No design concealment, checkpoint tuning or new generation was performed.
3. **Normal-operation claims have a defined boundary.** There is an induction proof for arbitrarily many specified normal transactions in the synchronous model and a separate two-transaction explicit-edge check, plus passing simulations. These do not establish every malformed schedule, glitch or physical timing case. A separate universal proof for every imaginable input history is not listed as a required deliverable; the brief must state the evidence's scope honestly.

The exact cipher-operation and key-handling explanation is no longer missing: the recovered original has four rounds on a 32-bit word, using fixed-mask XOR, the AES byte substitution and byte rotation. The inverse and fixed-mask reuse are source-checked and reproduced against the original Verilog. No numeric bonus-key claim is made.

## Optional work versus higher-score improvements

| Item | How the original requirements treat it |
|---|---|
| Recovering and reporting the numeric encryption key | Explicit bonus, up to 10 points; not a mandatory missing deliverable. |
| Programming a physical board or demonstrating the attack on hardware now | Not required for the simulation-only preliminary phase. The brief must still provide enough detail for future hardware reproduction; reference-board pins and interface sequence are documented, with hardware limits disclosed. |
| A new modified-design bitstream or physical timing/power measurements | Not separately listed among the preliminary deliverables. These could strengthen hardware claims, but the original bitstream-recovery work and required RTL/testbench are already present. |
| A fully automatic generation-to-test pipeline | A higher-score system-automation target. Existing verification automation does not retroactively make historical generation fully automatic. |
| Negligible hardware overhead or a more sophisticated payload | Higher Trojan-quality scoring targets. Measured overhead is disclosed: +36 LUT4, +48 registers, +13 carry cells and unchanged RAM. Predictable ciphertext corruption is an expressly allowed payload example. |
| GHOST, TrojanGYM, a particular AI provider or all four detectors | Not mandatory tools/deliverables in the preserved qualifier rules. Earlier detector studies concern their stated designs and do not certify the current modification. |
| A complete cryptographic-strength analysis or original author's algorithm name | Not requested as a separate deliverable. The required proposed encryption explanation is present and now substantially verified. |

Stealth belongs in the unresolved objective section above; it is not being demoted to optional merely because the rubric also awards points for it.

## Final handoff

Use the public repository link and current ZIP for the course handoff. Staff can view them without invitations, but invitations remain skipped at the user's request. Confirm any course-specific access or notification requirement with staff; instructor acceptance is an administrative outcome, not a prerequisite technical artifact that can be manufactured here.

The practical handoff is the package **with its record and stealth limitations disclosed**. This checklist is a source-based readiness assessment, not instructor approval, a grade prediction, a claim of full rubric compliance or approval of the previously proposed defensive alternative.
