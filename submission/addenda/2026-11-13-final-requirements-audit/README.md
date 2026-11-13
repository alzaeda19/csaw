# Final requirements audit and handoff — November 13, 2026

**The package is assembled for handoff with explicit limitations. Full challenge compliance is not established.** Jason's direction to use the original guidelines is the grading basis; no alternative scope is assumed approved. A new instructor-defined detector threshold is not a prerequisite to packaging or uploading the existing work.

## Checked against the current source

The live [qualifier README](https://github.com/JBlocklove/CSAW-AI-Hardware-Attack-Challenge-2026/blob/main/qualifier/README.md) was checked against the preserved original. The substantive artifact requirements and scoring rubric are unchanged. The competition form link has changed to https://forms.gle/d57fkBe5WFxDc9ha8. Heading/format changes are recorded in the diff. The published Solution section and its diagrams were excluded; no solution material was used.

The supplied past-challenge PDF's assignment screenshots on pages 33–34 agree with the current target and AI-authorship requirement. Earlier open-design guidance does not replace the recovered-bitstream task. The lecture was screened for title/contents; its case studies and generation material were not used. See records/SOURCE_REVIEW.md for exact inspection boundaries and file hashes.

## Required artifacts

| Requirement | Location in submission | Status |
|---|---|---|
| Modified RTL and dependencies | rtl/ | Present; frozen original files preserved |
| Demonstration testbench and reproduction instructions | tb/, run_tests.py, README.md | Present; saved positive/normal/negative-control evidence retained |
| Comprehensive generation prompts/responses | ai/ and recovered-record addenda | Present but incomplete; twelve reviewer instruction bodies and part of one output remain unavailable |
| Technical brief: recovery, AI workflow, trigger/payload, stealth methods, future hardware details and encryption explanation | README.md, CURRENT_GUIDE.md, ENCRYPTION_EXPLANATION.md and linked addenda | Present, with supported findings and limitations explicit |
| ZIP | repository-root submission.zip | Rebuilt and verified for this handoff |

The brief discloses the implemented behavior and actual evidence. It does not invent concealment methods, reconstruct absent prompts, claim the design is undetectable or promise a grade. Existing Qwen/Codex authorship records remain intact.

## Remaining substantive gaps

1. **Stealth is not established.** The objective remains in force. Current source/formal and detector evidence includes detection, misses and false alarms. A missed detection by HT1/HT3 does not satisfy the objective automatically. No specific four-detector pass criterion is in the rules. No further ordinary-test count alone can settle this qualitative requirement.
2. **Historical AI records are incomplete.** Twelve reviewer instruction bodies remain unavailable; one historical output still has a 6,178-character gap. The qualifier warns that missing generation logs can disqualify a submission. We cannot determine how staff will treat these partial review-stage gaps. Current audit logs do not repair older unavailable text.
3. **Normal-operation evidence has stated assumptions.** Saved simulations and protocol-scoped proofs support documented operation. Arbitrary malformed timing/history and physical behavior remain unproved. A separate universal formal proof is not listed as an additional artifact, but the normal-operation requirement must not be overstated.

No fresh recovery attempt is claimed in this audit: earlier bounded searches and exact remaining gaps are preserved. No available plaintext has been identified that closes those missing records.

## Scoring targets and optional work

Measured hardware overhead is documented; negligible overhead is unproved. Full historical generation-to-test automation is unproved. These affect scoring; documentation cannot retroactively create them. Predictable ciphertext corruption is an allowed example, so key exfiltration is not required. Numeric key recovery is explicitly a bonus. Physical board execution is not required for the simulation-only qualifier, although the brief must retain future hardware-reproduction details. No new detector framework or mandatory all-four-CLEAN result appears in the rubric.

## Delivery

The user explicitly selected public GitHub as the course handoff and requested collaborators be skipped. This update follows that instruction. It does not submit the competition form, send an email or claim staff receipt/acceptance. If entering the competition itself, the live README specifies its current form; public GitHub publication alone does not establish completion of that separate entry process.

Use the public repository and ZIP with these limitations visible. There is no basis to label the entire challenge completed merely because the archive is complete. The previous suggestion to seek an extra stealth criterion should not be read as a required step before handing in the current package.

## Audit scope and records

This is a final requirements/documentation review, not a new hardware-generation or stealth-improvement attempt. No RTL, testbench, detector, threshold, weights or earlier sealed evidence changed. Existing original-source cipher checks, simulations, scoped proofs, resource measurements and detector investigations retain their original scope. Integrity verification checks bytes and packaging, not a new execution of archived attack code.

One actual local Qwen advisory review is retained with request, received stream, reply and completion receipt. Its claims are checked against the rules and evidence in records/QWEN_REVIEW_NOTES.md. Qwen did not run experiments. Current visible Codex records have an explicit cutoff; hidden reasoning and missing history are not fabricated. Published-solutions material is excluded.
