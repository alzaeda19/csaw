# Independent method and artifact review

Outcome: **PASS_WITH_LIMITATIONS**. 1053/1053 checks passed.

This review checked frozen code and saved artifacts only. It did not run a model or evaluate a design.

Reviewed scored design artifacts: 23. Aggregate available: True.
Coverage: {'total': 23, 'scored': 23, 'unscored': 0, 'model_rows': 92, 'scored_model_rows': 92, 'scored_routes': {'exact_DFG': 23}, 'exact_extraction_status_counts': {'success': 23}}.

Frozen checkpoint/configuration hashes and model records match the prior audited AES run. All 37 vocabulary entries match. The worker uses CPU evaluation mode, strict weights-only loading, no-grad inference, two-class log-softmax and argmax, and the same four-model any-positive rule. The graph cache is not loaded. Catalog labels are absent from the worker input manifest and joined by the controller only after the inference pool completes.

All source hashes and passthrough graph-input hashes match the inventory. Saved graph counts, node normalization, feature counts and edge indices agree independently. Saved logits, log probabilities and probabilities are finite and agree arithmetically; class predictions, ensemble votes, confusion counts, coverage denominators, aggregate joins and all 92 CSV rows agree.

The static resource-handling review found no blocking issue. Deadline, resource and empty-graph exceptions bypass the package fallback handler. The parent guards worker wall time and process-group RSS, cleans up the process group, and leaves incomplete results unscored. Ordinary exact errors may use only the existing package fallback and retain explicit status/error evidence.

## Findings

No failing artifact checks.

| Model | TP | FN | FP | TN | Recall | False-positive rate |
|---|---:|---:|---:|---:|---:|---:|
| HT1 | 9 | 5 | 5 | 4 | 64.29% | 55.56% |
| HT2 | 6 | 8 | 6 | 3 | 42.86% | 66.67% |
| HT3 | 0 | 14 | 1 | 8 | 0.00% | 11.11% |
| HT4 | 4 | 10 | 2 | 7 | 28.57% | 22.22% |
| ensemble | 9 | 5 | 7 | 2 | 64.29% | 77.78% |

The largest sampled process-group RSS was 568,944 KiB. The longest recorded worker wall time was 17.137 seconds. All 23 workers exited 0. The only nonempty stderr line was the Matplotlib font-cache notice, present for all 23 isolated worker cache directories.

## Limits

- No model computation was rerun; review is static and based on saved artifacts.
- Directory labels are supplied annotations; checkpoint training overlap is unknown, and repeated families are not independent held-out examples.
- Exact DFG success records successful execution of the supplied backend, not an independently validated complete semantic model of each design.
- No heuristic fallback or resource failure occurred in this run; those handling paths were reviewed statically only.
- Parent RSS monitoring is sampled, not a kernel-enforced memory cap.
- Softmax scores are uncalibrated; detector predictions do not establish hardware security or functional equivalence.
