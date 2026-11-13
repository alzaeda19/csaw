# Defensive detector repair and fixed-design evaluation — November 13, 2026

**The signal-connection defect is repaired and the four unchanged detectors have been evaluated on the frozen clean and modified designs. HT2 flags the modification while passing the clean control. HT4 flags both designs, including a false alarm on the clean control. HT1 and HT3 miss the modification. Stealth is not established.**

This completes the authorized detector-repair task. It does not complete every challenge objective or establish instructor acceptance. No hardware source, existing flattened Verilog, detector checkpoint, feature vocabulary, classification threshold or ensemble rule was changed. No new Trojan, concealment or evasion method was generated. No published challenge solution was used.

## Results

| Fixed detector | Clean control | Existing modified design | Observed outcome on this pair |
|---|---|---|---|
| HT1 | CLEAN | CLEAN | Clean control passes; modification missed |
| HT2 | CLEAN | TROJAN | Clean control passes; modification detected |
| HT3 | CLEAN | CLEAN | Clean control passes; modification missed |
| HT4 | TROJAN | TROJAN | Modification detected; clean control falsely flagged |
| Existing any-positive ensemble | TROJAN | TROJAN | Both flagged, including a false alarm |

These are eight classifications of one labeled pair, not eight independent benchmark designs. There is no defensible estimate of general detection accuracy from this sample. The saved softmax scores are model outputs, not calibrated probabilities that a circuit is malicious or secure. The result does not identify which particular logic caused a model's vote.

| Detector | Clean model score for TROJAN | Modified model score for TROJAN |
|---|---:|---:|
| HT1 | 0.009021 | 0.088553 |
| HT2 | 0.430256 | 0.747342 |
| HT3 | 0.163288 | 0.163288 |
| HT4 | 0.925836 | 0.956767 |

Full precision, logits, class decisions, model identities and versions are in [analysis/inference/](analysis/inference/). All four models use their supplied weights and configuration, CPU inference, evaluation mode, seed 0, one thread, strict weight loading and the original two-class decision. There was one fixed inference run after the repair gates passed. No result was used to change the design, repair, weights or decision rule.

## What was broken and repaired

The supplied dataflow extractor tried to connect a reference to its definition by replacing every underscore with a dot. Literal underscores in recovered/generated signal names therefore became incorrect hierarchy separators. Thousands of internal references were left as disconnected graph leaves. Different hierarchy/name combinations could also silently collide.

The local extractor copy now uses the parser's exact symbol encoding, captures each definition identity directly, preserves feedback edges and refuses ambiguous names. A valid escaped dotted identifier exposed a second string-reparsing problem; the repair retains the parser's typed symbol identity for tree lookup. The downstream graph normalization and classifier code remain unchanged. The [patch](records/EXTRACTOR_PATCH.diff), original module, unsuccessful revisions and [refinement record](records/REFINEMENTS.md) are preserved.

The strict runner calls the repaired extractor directly. Parse errors or coverage failures stop the workflow; it does not use the old heuristic fallback. This repair covers the previously validated flattened inputs. The raw unflattened parser limitation is still present and that route was not rerun or represented as fixed.

## Validation before classification

All **11 benign circuit fixtures** passed the final checks: plain names, underscores, generated names, escaped dotted names, child-module hierarchy, register feedback, shared fan-in, slices/concatenation, constant output, ambiguous naming and malformed HDL. The final two pass by being explicitly rejected. The original extractor's broken cases and both unsuccessful repair runs are retained. The previously supported plain-name graph remains exactly unchanged.

Both target extractions then passed these gates before any classifier score was computed: every bound definition is retained; bound references are reconnected; no ambiguous symbols, unresolved bound references or unexpected unbound non-input references remain; expected output/input and state dependencies are reachable; all graph edges and nodes are preserved in the exact model input; the same 37-feature vocabulary is used. See [PRE_INFERENCE_GATES.json](analysis/PRE_INFERENCE_GATES.json) and the timestamped [pre-inference freeze](records/INFERENCE_FREEZE.json). Their `inference_not_yet_run` fields describe their creation time, not the final state.

| Graph measure | Earlier clean | Repaired clean | Earlier modified | Repaired modified |
|---|---:|---:|---:|---:|
| Nodes | 18,841 | 14,119 | 19,014 | 14,249 |
| Edges | 19,839 | 19,839 | 20,018 | 20,018 |
| Weakly connected components | 606 | 79 | 611 | 79 |
| MISO dependency descendants | 1 | 12,557 | 3 | 12,686 |
| Internal reference nodes reconnected by this repair | — | 4,722 | — | 4,765 |

The reduced node count reflects removal of duplicate reference leaves after their edges are connected to definitions. It is not removal of hardware or model-input pruning. Each repaired graph has one main component (13,959 clean / 14,089 modified nodes), one six-node clock-alias component and 77 two-node constant-definition components. All three observed output roots are in the main component. The clock aliases remain separate because this backend represents data dependencies, not event timing. Component details and post-inference frozen-hash checks are in [FINAL_AUDIT.json](analysis/FINAL_AUDIT.json).

The earlier flattened run labeled both designs CLEAN in all four models, but it used broken connections. Those historical scores remain preserved and cannot be used as whole-design stealth evidence. The repaired run changes HT2's modified-design vote and both HT4 votes. The earlier raw/fallback results remain a separate, incomplete representation and are not combined with these results as additional reliable trials.

## Limits and submission implications

The gates validate the specific reference-joining repair and the stated dataflow abstraction. They are not a general proof of the parser, complete HDL semantics, cycle/clock timing, physical behavior or classifier training-distribution compatibility. The flattened RAM logic is included in the graph, but graph classification is not a temporal memory-equivalence proof. Wider naming collisions are deliberately rejected rather than guessed. No broad benchmark, checkpoint retraining or calibration study was performed.

The exact original and flattened source bytes are the same ones tested in the preceding [representation-validation addendum](../2026-11-13-detection-evaluation/README.md). Its six full-core simulations, each covering 270 transactions and 39,960 output triples, remain the evidence for those finite trace comparisons. No new HDL transform or simulation is claimed in this repair. Archived source/formal detection results, measured hardware overhead and protocol-scoped normal-behavior checks retain their original scope.

The current package contains modified RTL, a demonstration testbench, a technical brief and the available AI records. **The remaining substantive concerns are the stealth objective and incomplete historical AI records.** The new detector results are useful evidence, including both detection and false alarms; they are not a positive stealth result or a grading decision. Normal-behavior claims remain limited to their documented tests and protocol assumptions. Numeric key recovery and physical board execution are not mandatory preliminary deliverables. The original rules do not require passing these particular four detectors or universal undetectability; staff judge the submitted evidence.

## Reproduce safely in a separate directory

The supplied detector files and checkpoints are included under `package/`, with their license. The only changed package file is `hw2vec/hw2vec/hw2graph.py`; all other copied files are hash-verified. Frozen target inputs and original sources are included. The scripts `run_detectors.py`, `run_matrix.py` and `ask_qwen.py` are unchanged historical reference copies and are **not** used by this repair workflow.

Requirements from the tested environment: Python 3.12.1, PyTorch 2.10.0, torch-geometric 2.3.1, NumPy 2.5.4, NetworkX 3.2.1, PyVerilog 1.3.0, PyGraphviz 2.0.4, compatible Graphviz and Icarus preprocessing. The Icarus build used was 14.0 development. The included fixed model configurations determine the network architecture. No GPU, training dataset, model-service account or new hardware generation is needed. Existing environment packages were reused; there was no installation in this task. Other versions/platforms are unverified.

From this addendum directory, first prepare a new directory outside the evidence bundle:

```sh
python3 scripts/prepare_replay.py /absolute/path/to/new-detector-replay
```

Set `CSAW_DETECTOR_PYTHON` to your compatible interpreter and `CSAW_TOOL_SUITE` to the directory containing the Icarus tools. Defaults in `run_python.py` name the original local environment and will need overriding on another machine. In the prepared directory run, in order:

```sh
python3 scripts/run_python.py final_fixtures scripts/test_extractor.py --label final --expect-repaired
python3 scripts/run_python.py target_extraction scripts/extract_targets.py
python3 scripts/run_python.py repaired_inference scripts/infer_repaired.py
```

The preparation step copies only inputs, scripts and the preserved original plain-name control graph; it does not run a model or overwrite saved evidence. The successful fixture/extraction/inference commands were executed in the original work directory. The preparation helper was separately checked to produce matching frozen inputs; its new prepared directory was not used for a second classifier run. Result directories must not already exist. Stop on any failed step; do not substitute a fallback graph. A later reproduction creates new records and must be reported separately from this single saved experiment.

## Agent records and errors

Codex performed the local detector repair. The existing Trojan chat was asked for read-only validation criteria, but its turn was blocked by an automated cybersecurity check before a reply. The exact error is preserved in [COORDINATION_ERROR.json](records/COORDINATION_ERROR.json); no retry or alternate route was used to obtain that blocked review. There is **no new Qwen response or independent peer-review claim** in this addendum. Prior Qwen/Trojan reviews remain in their dated addenda.

The authentic visible user/assistant messages and tool inputs for this repair are saved with native line hashes and an explicit cutoff under `ai_logs/`. Actual test errors, failed fixtures, refinements, commands, exit statuses, runtime versions and complete inference results are saved separately. A tool-display truncation affected what fit in the conversation view; the saved inference stdout/stderr, receipt and full results were subsequently read and verified. It was not a failed inference or a missing model response. Hidden reasoning and unrelated platform/private data are not exported. Older unavailable messages are not recreated or declared recovered by this new record.
