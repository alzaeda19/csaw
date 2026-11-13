# Submission status in plain English — November 13, 2026

**The package is assembled and available to hand in; full challenge compliance is not established.** The modified RTL, demonstration testbench, technical brief, available AI records and ZIP are present. The original cipher and effective key handling are now explained and verified. See the [required-versus-optional checklist](submission/SUBMISSION_CHECKLIST.md) for the line-by-line comparison with the preserved original rules.

## The remaining requirement-level concerns

- **Incomplete relevant AI records:** twelve original reviewer instruction bodies remain unavailable (nine requests and three steering messages). One formerly truncated tool output has now been fully assembled from authentic overlapping captures, recovering 10,140 previously omitted characters. The other still has a 6,178-character gap after four characters were recovered. The original captures remain unchanged and the assembly is labeled. Staff must judge the effect of these partial review-stage gaps on the comprehensive-generation-log requirement; no missing dialogue was invented.
- **Stealth is unestablished, and the completed checks show detectability:** Qwen source review identifies the added output behavior; the scoped formal comparison finds a mismatch. All four supplied detectors were run, but both graph routes have completeness defects, so their labels cannot establish whole-design stealth. The [new evaluation report](submission/addenda/2026-11-13-detection-evaluation/README.md) preserves every result, control, error and limitation. Stealth remains an original objective, not merely optional.
- **Normal behavior has a defined evidence scope:** the saved simulations pass and formal checks cover the documented normal transaction schedule. Arbitrary malformed schedules and physical timing are outside that proof. A separate proof covering every possible input history is not an additional listed deliverable.

## What is optional or affects higher scores

Numeric key recovery is explicitly a bonus. Board programming is not required for the simulation-only preliminary phase, although the report must provide future hardware-reproduction details. A reference-board pin map and interface sequence are documented. A new modified-design bitstream, physical timing/power measurements and a particular detector/tool are not separately required preliminary deliverables.

Full generation-to-test automation, negligible overhead and a more sophisticated payload are higher-score targets. Existing verification automation is not historical generation automation. Measured overhead is +36 LUT4 cells, +48 registers, +13 carry cells and unchanged RAM; no negligible-overhead claim is made. Predictable ciphertext corruption is an allowed payload example. Stealth itself remains in the objective section above.

## Delivery and provenance

The public GitHub repository and updated ZIP are the course destination specified by the user. Collaborator invitations remain skipped. Staff receipt/acceptance is unconfirmed; it is an administrative outcome, not a technical artifact that can be created before submission. The original competition form has not replaced the user's stated course destination, and the defensive alternative is not assumed approved.

All 262 original package files and five prior sealed addenda remain unchanged. This latest addendum adds fresh full-core simulation of both frozen versions and their analysis representations, fixed-checkpoint detector results, structural comparison, independent formal/coverage reviews and Qwen records. No hardware source or detector checkpoint was changed. Earlier documentation-only reports remain dated history; their no-new-run statements do not describe this evaluation. The [closeout record](submission/addenda/2026-11-13-submission-closeout/README.md) still preserves the earlier authentic record recovery.

Older full conversations and later documentation-audit gaps remain separately disclosed. Hidden reasoning, platform instructions and unrelated private content are intentionally excluded; those exclusions are not substitutes for missing ordinary prompts. Current complete Qwen request/response streams do not retroactively repair older unavailable messages.
