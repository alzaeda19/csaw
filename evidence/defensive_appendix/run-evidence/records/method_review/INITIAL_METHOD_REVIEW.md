# Initial frozen-method review

Scope: static review only of the prior audited AES runner and its copied HW2GRAPH package. No design or model was evaluated by this reviewer. This document precedes review of the new runner and outputs.

## Frozen inference requirements

- Preserve the exact ordered 37-entry DFG vocabulary, package normalization, four original model configurations/checkpoints, strict tensor-only checkpoint loading, CPU evaluation mode, deterministic settings, and single-graph inference.
- Preserve two-class log-softmax, class-index argmax, and the ensemble rule: any of the four models voting class 1 means TROJAN. Do not introduce thresholds, tune parameters, train, deserialize the graph cache, or replace the graph representation.
- Model input must derive only from the graph, not the clean/infected catalog label. The existing graph label 0 is a placeholder; actual catalog labels belong in output records.
- Retain original file hashes, preparation hashes, observed concatenation order, preprocessing route, graph counts, normalized input, model identities, and output values. File concatenation is not hierarchy elaboration.

## Resource and validity findings

1. `HW2GRAPH.process` catches `Exception` around exact DFG generation. A SIGALRM handler that raises `TimeoutError` is caught there; this converts an extraction timeout into a heuristic fallback unless an independent timeout state overrides it. A timeout sentinel derived directly from `BaseException` avoids this particular handler, but a parent deadline is still required for native code and child processes.
2. `MemoryError` is also caught by this handler and must not be treated as an ordinary parser error. Resource exhaustion must leave the design unscored, even if fallback subsequently returns a graph.
3. Isolate each design in a worker process with a separate process group. On timeout/resource cancellation, terminate the entire group, then wait/reap; killing only the Python worker can leave parser/preprocessor children behind. Parent deadlines should also cover import/model loading, normalization, inference, and output serialization.
4. macOS address-space and resident-memory limits may not provide reliable enforcement. Record whether each configured resource limit was actually applied. A parent monitor of worker plus descendant resident memory provides a separate bounded-run safeguard; resource termination should be explicit in the record.
5. Follow the prior runner's graph checks: no null graph, at least two nodes, at least one edge, and no dummy graph. Require valid feature indices, edge-index dimensions/range, and exactly one input graph. A final empty, dummy, or otherwise invalid graph is unscored.
6. Check finiteness of logits, log probabilities, and probabilities individually. Checking probabilities alone permits negative-infinite log probabilities with finite zero probabilities. Require two outputs per model and all four completed valid model records before an ensemble verdict.
7. A worker exit without a complete valid result is unscored. Atomic final result publication helps distinguish completed work from partial output. JSON must not contain NaN or Infinity.

## Fallback scoring and coverage

An ordinary exact-parser/extraction exception may lead to a scored design if the unmodified package's preexisting fallback produces a valid graph and all four frozen models produce finite outputs. This is faithful to the package detector path. It must not be reported as successful exact extraction.

Record separate facts: `scored`, `route`, `exact_extraction_attempted`, `exact_extraction_status`, exact exception/error text where available, `fallback_status`, and overall failure reason if unscored. A preexisting large-lookup shortcut is `exact_not_attempted`, not `exact_failed`.

If the exact backend returns an empty graph and the package falls back, explicitly record `exact_empty_graph`; do not silently label this as exact success. A valid package fallback can be reported as fallback coverage only if that interpretation is consistent with the task's requirement for empty extraction results. A final empty graph must always remain unscored.

Report all eligible designs as the fixed inventory denominator, with mutually exclusive exact-scored, fallback-scored, shortcut-scored, and unscored counts. Also report exact attempted/succeeded/failed/empty/timed-out counts separately. Accuracy, sensitivity, and false-positive counts should state their scored-subset denominators and unscored counts by catalog label. Missing outcomes must not become CLEAN predictions or be silently omitted from coverage.

These are within-package labels and observations, not proof of Trojan absence or an independent held-out accuracy estimate. Training-set overlap is unknown unless independently documented. Heuristic graphs omit HDL elaboration and full sequential/control semantics; their scores are not calibrated compromise probabilities.

## Reviewed reference paths

- `/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/run_aes_detectors.py`
- `/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/package/hw2vec/hw2vec/hw2graph.py`
- `/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/package/hw2vec/hw2vec/scripts/graph_processer.py`
- `/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Clean_AES_2026-11-10_123555Z/records/independent_review/INDEPENDENT_RUN_REVIEW.md`

Pending: new runner source review, frozen identity comparison, output schema/arithmetic checks, inventory/coverage reconciliation, and final artifact review without rerunning inference.
