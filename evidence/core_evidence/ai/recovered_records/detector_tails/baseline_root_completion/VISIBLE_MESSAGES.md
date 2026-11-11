# Recovered visible detector tail: baseline_root_completion

Exact native visible text; authored historical claims are preserved, not independently revalidated. Logged commands were not executed during recovery. Full retained tool/command fields are in visible_events.jsonl.

## assistant_commentary — 2026-11-10T12:29:03.486Z

Source line 1312.

The independent review confirmed that four distinct checkpoints were used, the baseline was unchanged, and the reported scores match the saved model inputs and outputs.

It also found that all 2,880 operation nodes in the fallback graph became generic “branch” nodes. That is another reason to treat these as limited detector results. I’m sealing the report, failure logs, and AI-record export now.


## assistant_final_answer — 2026-11-10T12:30:20.258Z

Source line 1336.

**All four detectors ran and returned CLEAN—0/4 Trojan votes—but only on a heuristic graph. Exact graph extraction failed.**

| Detector | P(clean) | P(Trojan) | Prediction |
|---|---:|---:|---|
| HT1 | 92.42% | 7.58% | CLEAN |
| HT2 | 64.48% | 35.52% | CLEAN |
| HT3 | 78.39% | 21.61% | CLEAN |
| HT4 | 95.36% | 4.64% | CLEAN |

The important limitations:

- Exact extraction failed because the four FPGA RAM primitives lacked definitions in the detector input.
- The package’s built-in fallback produced **5,728 nodes and 10,947 edges**. All **2,880 operation nodes** became generic “branch” nodes.
- These scores **do not certify the complete baseline as Trojan-free**. RAM semantics, detailed logic behavior, and applicability to this recovered netlist remain unvalidated.

Four distinct checkpoints loaded successfully, and an independent review verified the inputs and calculations. The extraction failure and earlier environment-launch failure are preserved.

[Full report and execution evidence](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/REPORT.md) · [AI records and gaps](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/AI_RECORD.md)

The AI export contains **200 records**, with encrypted-message and snapshot-cutoff gaps disclosed. Your repository, recovered baseline, and originals remain unchanged. No solutions were used.

