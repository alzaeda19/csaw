# Clean AES four-detector comparison — November 10, 2026

**The actual clean AES process completed with exit 0. HT1–HT4 each returned CLEAN, giving zero of four Trojan votes. The retained recovered-baseline run also returned four CLEAN classifications. Both classify approximate graphs, not complete hardware semantics.**

This is a separate experiment on the professor-supplied clean AES reference. It does not replace or rerun the recovered baseline. The source user explicitly requested coordination with the trojan orchestrator, a clean AES run, comparison to retained results, and separate assignment-readiness review. No generation or adaptive detector-feedback loop was executed.

## Actual scores

| Model | Baseline P(Trojan) | Clean AES P(Trojan) | AES minus baseline, percentage points | Predictions |
|---|---:|---:|---:|---|
| HT1 | 0.075842798 | 0.048238419 | -2.760438 | CLEAN / CLEAN |
| HT2 | 0.355168432 | 0.047571383 | -30.759705 | CLEAN / CLEAN |
| HT3 | 0.216109276 | 0.163287982 | -5.282129 | CLEAN / CLEAN |
| HT4 | 0.046440266 | 0.023782268 | -2.265800 | CLEAN / CLEAN |

The original ensemble declares TROJAN if any model predicts class 1. Both references receive zero votes. Mean P(Trojan) is 0.070720013 for clean AES and 0.173390193 for the retained baseline. These are uncalibrated classifier scores and descriptive averages; smaller values are not evidence that one design is safer.

The AES command ran from 12:37:14.813109Z to 12:37:27.262606Z, returned 0 and did not time out. Its only stderr was the ordinary Matplotlib font-cache notice. No new execution failure occurred. Exact AES graph extraction was deliberately skipped by the supplied notebook's large-lookup policy, not attempted and failed.

[Results](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/runs/clean_aes_detection/RESULTS.json) · [comparison](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/COMPARISON.json) · [command and exit receipt](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/detector_command.json) · [stdout](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/detector.stdout) · [stderr](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/detector.stderr)

## Source and preprocessing

Three unchanged design files were copied from the separately verified professor reference:

- aes_128.v: SHA-256 60835b67fb0c424ab4a1a5d7ee11a2b5a7301bf45677def9653f7491c92cb1a6
- round.v: SHA-256 a9c7504563285ded97dc072a653547938b457ea1918b006651d168c61a4ef362
- table.v: SHA-256 36171c0297f95a036285d418b9be3a0d4c4d4e5248a8f0a6133ed7956b37b157

They contain nine module definitions: aes_128, expand_key_128, one_round, final_round, table_lookup, S4, T, S and xS. The testbench was copied for provenance but excluded from detector input. The copied package has 64 files; the input manifest covers those and the four HDL files. The source receipt ties these to the professor ZIP SHA-256 3912fd8e7afca470b57132c5af34215967c1b0e579ef2c0bc345de6a448c2832.

Following the supplied notebook, include directives are removed only from disposable graph-input copies, since all three files are supplied once. The unchanged package concatenates files, removes comments/underscores and renames the selected AES top. Actual concatenation order was table.v, aes_128.v, round.v. All nine definitions are present; the AES module is correctly renamed top.

The 512 qualifying lookup entries exceed the notebook's 128-entry threshold, selecting its direct heuristic path. The resulting graph has 835 nodes, 1,121 edges and three weakly connected components. Raw nodes are 301 signals and 534 operations: 513 branch, 17 xor and four concat. Normalized input/output labels describe graph features, not physical FPGA ports.

This is source concatenation and regex assignment extraction, not hierarchical elaboration. Same-named signals may merge across modules. Case selection, lookup behavior, sequential/control semantics and instance hierarchy are not fully represented. Inclusion of every source file therefore does not establish full semantic coverage.

## Method parity and retained baseline failure

All four checkpoint/configuration records and the feature-vocabulary bytes exactly match the retained baseline run. The same CPU inference core, strict weights-only loading, evaluation mode, fixed 37-feature map, probability calculation and any-positive ensemble rule are used. No training occurred. The cached training-graph pickle was not loaded; the previously reviewed adaptation preserves the fixed feature map and does not feed cached labels or statistics into inference. Placeholder label zero is graph metadata, not an input to the model's forward calculation.

The retained baseline source SHA-256 is 180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765. Its exact extraction failed with `No such module: SBRAM404K`: four external RAM instances lacked supplied definitions and preprocessing removed underscores. Its automatic heuristic fallback produced 5,728 nodes and 10,947 edges, with all 2,880 operation nodes classified as generic branch. That historical failure and the initial runtime launch failure remain preserved. The baseline was not rerun for this comparison.

Different representations and omitted semantics prevent interpreting the score differences as a validated security ranking. These runs do not measure false-negative rates, detection sensitivity, design equivalence, functional correctness or physical-board readiness.

[Retained baseline report](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/REPORT.md) · [baseline receipts](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/baseline_evidence_receipt.json)

## Environment, review and preservation

Actual execution was native macOS arm64, using Python 3.12.1, torch 2.10.0, torch-geometric 2.3.1, NetworkX 3.2.1, PyVerilog 1.3.0 and PyGraphviz 2.0.4. It reused the baseline inference interpreter without new installations; temporary/cache files were redirected into this new experiment. Shared site packages mean the runtime is not fully self-contained. Environment outputs and runner changes are retained.

The independent artifact reviewer passed 28 checks, including input and model hashes, all nine module definitions, observed concatenation order, graph edges/features, logits-to-probability arithmetic and the ensemble. This was an evidence review, not another inference run or independent security certification.

Final preservation receipts check all 68 source/copy pairs and six baseline evidence files, plus repository status and HEAD. Existing source inputs and the clean repository remain unchanged. No published solutions, contaminated work, generated Trojans, evasion loop, key extraction, board programming or repository modifications were used. Existing AI records were preserved.

The coordinating chat separately produced an assignment-readiness report and a tool-disabled Claude Code review. Claude's input preceded these new AES results; do not claim it reviewed the new scores. Four CLEAN classifications do not complete the assignment. Required deliverable coverage and AI-record completeness remain separate questions.

[Independent review](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/independent_review/INDEPENDENT_RUN_REVIEW.md) · [preservation receipt](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/preservation_check.json) · [AI records and gaps](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/AI_RECORD.md) · [coordinator readiness report](/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/outputs/detector-comparison-review/REPORT.txt)
