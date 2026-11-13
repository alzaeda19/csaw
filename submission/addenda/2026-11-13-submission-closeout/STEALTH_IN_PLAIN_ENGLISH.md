# What “stealth not established” means

**The tests show that the modification behaves as documented. They do not show how difficult it is to discover.** That is the distinction between demonstrating functionality and providing evidence of stealth.

An unusual trigger may keep a change inactive during ordinary tests. That alone does not make the change hard to find by reading the source or comparing the hardware. Conversely, the assignment explicitly requires the report to explain the trigger: honest disclosure in the report is not itself a failure.

## What the current evidence says

- The existing wrapper has a visible input comparison, extra state and an output-altering expression. A source review can identify the modification. No concealment method was implemented or established in this closeout.
- Normal tests and the protocol-scoped proofs support preserved normal behavior in their stated scope. They are not tests of whether a reviewer or detector notices the change.
- Synthesis records added logic and registers. The percentage increase differs greatly by resource type; a small LUT increase does not erase the larger register increase or establish negligible overhead.
- The earlier four-detector CLEAN result concerns the **unmodified baseline**, not the current modified submission. Its complete graph extraction failed, and the fallback graph omitted memory semantics. It therefore cannot certify the current modification or establish full-design stealth.

These facts support the current label: **functionality demonstrated; visible changes documented; stealth not established**. They do not prove how a particular physical or gate-level inspection would behave.

## What Qwen can contribute

Qwen can act as an assistant to the reviewer: read the frozen design and evidence, identify unsupported claims, check whether a comparison is fair, and help explain observed results. Its opinion is not a detection experiment or security certificate. The current Qwen review received the existing source and evidence, with no tools or permission to change the design.

A defensible evaluation would state who or what is trying to find the change, what information the evaluator receives, which exact design files were tested, and how the clean control behaves. Any automated detector must process the intended complete design; an extraction failure or incomplete fallback must be reported. The results should include detections, misses and false alarms, together with tool/model versions and limitations. An independent assessment should avoid using its outcome as a feedback loop to tailor the submission to that detector.

The strongest justified conclusion from a particular missed detection is narrow: “This check did not flag this exact design under these conditions.” It is not “the design is undetectable.” A source reviewer may also find a change that a learned classifier misses; both results matter.

No new detector run or stealth improvement is claimed here. The preserved qualifier does not prescribe a particular detector or guarantee that passing one satisfies the stealth objective. Staff decide how the submitted evidence meets the rubric. Documentation alone cannot turn an untested quality claim into an established property.

## Evidence locations

- Existing wrapper: `sources/EXISTING_WRAPPER.sv` in this closeout bundle; byte-identical to the submitted source at the audited commit.
- Previous baseline detector limitations: `sources/EXISTING_BASELINE_DETECTOR_REPORT.md`.
- Resource measurements and normal-preservation assumptions: the earlier `2026-11-12-qwen-verification` addendum.
- Actual Qwen request, received response and completion receipt: `ai_logs/03_stealth_evidence/`.
- Rejected model claims and corrections: `QWEN_REVIEW_NOTES.md`.
