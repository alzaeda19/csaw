# Submission status in plain English — November 13, 2026

**Evidence wording update:** [Verified results and exact test boundaries](submission/VERIFIED_FACTS.md). This states the recorded counts, encoded test conditions and checks that were not performed. No new proof or experiment is claimed.

**Final requirements audit:** [Current-rule comparison and handoff](submission/addenda/2026-11-13-final-requirements-audit/README.md). The required artifacts are assembled; stealth and historical AI-record completeness remain unresolved. No additional detector threshold is a prerequisite to uploading the existing package. The live competition form differs from the earlier saved link; GitHub remains the user-requested course destination.


**The package is assembled and available to hand in; full challenge compliance is not established.** The modified RTL, demonstration testbench, technical brief, available AI records and ZIP are present. The original cipher and effective key handling are now explained and verified. See the [required-versus-optional checklist](submission/SUBMISSION_CHECKLIST.md) for the line-by-line comparison with the preserved original rules.

## The remaining requirement-level concerns

- **Incomplete relevant AI records:** twelve original reviewer instruction bodies remain unavailable (nine requests and three steering messages). One formerly truncated tool output has now been fully assembled from authentic overlapping captures, recovering 10,140 previously omitted characters. The other still has a 6,178-character gap after four characters were recovered. The original captures remain unchanged and the assembly is labeled. Staff must judge the effect of these partial review-stage gaps on the comprehensive-generation-log requirement; no missing dialogue was invented.
- **Stealth is unestablished:** source review and the scoped formal comparison detect the change. The [detector repair](submission/addenda/2026-11-13-detector-repair/README.md) now fixes the flattened graph's broken signal connections, with 11 passing fixture checks and coverage gates before inference. HT2 flags the modification while passing the clean control; HT4 flags both, including a false alarm; HT1 and HT3 miss the modification. The later [HT1/HT3 investigation](submission/addenda/2026-11-13-detector-miss-investigation/README.md) explains the identical HT3 scores on this pair and records detections, misses, false alarms and five abstentions on supplied labeled examples. These results improve the evidence but do not establish stealth. The raw parser route and broader temporal/physical-model limitations remain. Stealth is an original objective, not merely optional.
- **Normal behavior has a defined evidence scope:** the saved simulations pass and formal checks cover the documented normal transaction schedule. Arbitrary malformed schedules and physical timing are outside that proof. A separate proof covering every possible input history is not an additional listed deliverable.

## What is optional or affects higher scores

Numeric key recovery is explicitly a bonus. Board programming is not required for the simulation-only preliminary phase, although the report must provide future hardware-reproduction details. A reference-board pin map and interface sequence are documented. A new modified-design bitstream, physical timing/power measurements and a particular detector/tool are not separately required preliminary deliverables.

Full generation-to-test automation, negligible overhead and a more sophisticated payload are higher-score targets. Existing verification automation is not historical generation automation. Measured overhead is +36 LUT4 cells, +48 registers, +13 carry cells and unchanged RAM; no negligible-overhead claim is made. Predictable ciphertext corruption is an allowed payload example. Stealth itself remains in the objective section above.

## Delivery and provenance

The public GitHub repository and updated ZIP are the course destination specified by the user. Collaborator invitations remain skipped. Staff receipt/acceptance is unconfirmed; it is an administrative outcome, not a technical artifact that can be created before submission. The original competition form has not replaced the user's stated course destination, and no approval of the defensive alternative is recorded.

All 262 original package files and eight prior sealed addenda remain unchanged. The latest investigation uses the repaired extractor without changing it, attempts all 23 supplied labeled examples and replays the two saved CSAW graph tensors with read-only diagnostics. Hardware and detector settings remain unchanged. Two local Qwen advisory reviews are included with their factual errors corrected; Qwen did not run or independently reproduce the tests. The earlier blocked Trojan-chat repair review remains a separate historical event. The [closeout record](submission/addenda/2026-11-13-submission-closeout/README.md) still preserves the earlier authentic record recovery.

Older full conversations and later documentation-audit gaps remain separately disclosed. Hidden reasoning, platform instructions and unrelated private content are intentionally excluded; those exclusions are not substitutes for missing ordinary prompts. Current complete Qwen request/response streams do not retroactively repair older unavailable messages.
