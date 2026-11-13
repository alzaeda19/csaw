# Four-detector evaluation of recovered baseline — November 10, 2026

**All four models completed inference and returned CLEAN, with zero of four Trojan votes. Exact full-design graph extraction failed. The scores classify the package's heuristic fallback graph; they do not prove that the complete baseline is Trojan-free.**

The unchanged candidate is the recovered baseline, not the repaired derivative, AES teaching reference or regenerated-bitstream decode. SHA-256: 180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765.

## Actual results

| Model | Prediction | P(clean), model score | P(Trojan), model score |
|---|---|---:|---:|
| HT1 | CLEAN | 0.92415720 | 0.07584280 |
| HT2 | CLEAN | 0.64483154 | 0.35516843 |
| HT3 | CLEAN | 0.78389078 | 0.21610928 |
| HT4 | CLEAN | 0.95355976 | 0.04644027 |

The supplied ensemble declares TROJAN if any model predicts class 1. Here it reports CLEAN, 0/4 votes. Mean P(Trojan) is 0.17339019, maximum 0.35516843 and minimum 0.04644027. These are classifier outputs and descriptive aggregates, not calibrated probabilities of hardware compromise.

The completed process returned exit 0, with empty stderr and no timeout. Four distinct checkpoint files and serialized tensor payloads were independently verified. Each loaded strictly with no missing/unexpected tensor keys, on CPU in evaluation mode.

[Full results](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/RESULTS.json), [stdout](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/detector_02.stdout), [command/result](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/detector_02_command.json), [checkpoint identities](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/model_loads.json).

## Extraction failure and limitations

The actual exact-extraction error was:

> No such module: SBRAM404K

The source has four SB_RAM40_4K instances, but no definitions or include directives for their behavioral implementations. The package globally removes underscores during preprocessing, hence SBRAM404K in the exception. It then uses its own built-in heuristic fallback. No fallback was invented to obtain a favorable prediction.

The resulting graph has 5,728 nodes, 10,947 edges and one weakly connected component. Its raw nodes comprise 2,848 signals and **2,880 operations, all labeled generic branch**. After supplied normalization, it uses only four of 37 feature categories: 2,771 signal, 2,880 branch, 38 input and 39 output labels. These are graph features, not physical port counts. Empty/dummy graphs were explicitly rejected.

Material limits:

1. **RAM-body semantics are absent.** This is not complete elaboration of the simulation model; its external primitive library was not supplied to this detector run.
2. **The graph is coarse.** Assignment dependencies and generic branch labels do not fully represent LUT behavior, sequential/control conditions, hierarchy or memory behavior.
3. **Preprocessing changes representation.** Comments/underscores are removed and the selected top is renamed in a disposable graph-input file. No semantic-equivalence proof for that transformation was performed.
4. **Applicability and calibration are unvalidated.** Accuracy on this recovered FPGA netlist, its relation to the training distribution and false-negative rates cannot be established by one baseline run.
5. **Functional equivalence is separate.** These classifications do not replace prior functional proofs, fix the baseline readiness issue, establish algorithm correctness or certify a physical board.

The supported claim is: **“HT1–HT4 did not flag the heuristic graph extracted from the unchanged recovered baseline.”** It is not four complete-design security certifications.

[Extraction log](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/extraction.stdout), [preprocessing audit](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/preprocessing.json), [raw graph](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/graph_before_normalization.json), [exact model inputs](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection_02/model_input.json).

## Method and reproducibility

A fresh isolated folder contains byte-identical source/package copies. The candidate is 1,213,314 bytes and 45,711 lines, with top module chip. The functional-role adapter was copied for provenance but not fed into the detector, avoiding a wrapper-only graph.

The runner uses the supplied HW2GRAPH, DataProcessor and neural-network classes without modifying package code. It follows the notebook's exact-first path and automatic fallback. No large lookup-table shortcut was triggered. A 30-second extraction bound was configured; the actual missing-module failure and fallback took under one second.

All four configurations use 37→200→200 graph convolutions, SAGPooling ratio 0.8, max readout and a 200→2 output layer. Inference preserves the supplied feature vocabulary and normalization, log-softmax/argmax calculation and ensemble rule. All four models are required; a partial ensemble is rejected. CPU inference uses seed 0, one thread and evaluation mode.

Two disclosed detector-only adaptations:
- Checkpoints load with weights_only=True and strict state loading; weights remain unchanged.
- The training-graph pickle is not loaded. Independent source review confirmed it only adds cached graphs and initializes the fixed feature count; inference selects the last appended candidate graph. The same 37-feature map is preserved, with no cached labels or statistics entering the forward calculation.

The graph's label=0 is the notebook's placeholder metadata. It is not a verified truth label and is not passed into the x/edge_index/batch model calculation.

Environment: native macOS 26.2 arm64, Python 3.12.1, PyTorch 2.10.0, PyTorch Geometric 2.3.1, PyVerilog 1.3.0, NetworkX 3.2.1 and PyGraphviz 2.0.4. Full versions, locations and installation records are retained. The local venv reuses shared site packages, so it is not fully self-contained. The package recommends Python 3.10/3.11; this run verified required imports and inference on the available 3.12.1, without claiming broader compatibility.

[Runner](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/run_detectors.py), [environment summary](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/environment_summary.json), [setup commands](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/environment_commands.jsonl).

## Preserved failures

- PyGraphviz was initially missing; a native venv-local wheel supplied the required Graphviz libraries. Import and synthetic layout checks passed.
- Shared PyArrow/Safetensors binaries had the wrong architecture; same-version native wheels were installed only inside the venv. Other dependency changes are logged.
- The first detector launch exited 1 before model loading because PYTHONNOUSERSITE exposed incompatible global x86_64 PyTorch. The second used the verified native user-site PyTorch. Source, package, weights and runner were unchanged.
- Exact graph extraction failed on the missing RAM module. The original package catches the exception and cleans some parser scratch files; its error message is preserved. No nonexistent full backend traceback is claimed.

The first launch produced no detector result. Only baseline_detection_02 supplies the four scores.

[First launch traceback](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/detector.stderr), [first command/result](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/detector_command.json), [failed run record](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/runs/baseline_detection/failure.txt).

## Independent review, preservation and AI records

A separate reviewer passed 25 checks covering source/model identities, distinct tensor payloads, graph transformations and ordering, strict loading, inference equations and ensemble calculations. It found the numbers consistent within float precision and no hidden fallback. This was evidence review, not an independent training run or hardware-security assessment.

All 138 source/copy/original hash checks passed. The repository remains clean at a3006f61f55fd8b6a232377d292fcec3138bf1ae. Recovered RTL, original challenge files, source course package and user repository are unchanged.

No solutions, generation/repair/evasion loop, AI gateway, key extraction, training or board programming were used. Network activity was limited to ordinary dependency installation; RTL was not sent to an AI service.

[Independent review](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/input_audit/INDEPENDENT_RUN_REVIEW.md), [preservation receipt](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/records/preservation_check.json), [AI record and gaps](/Users/al-zayedal-hassan/Documents/CSAW_2026_Detector_Baseline_2026-11-10_122045Z/AI_RECORD.md). The output manifest records its explicit scope; runtime installation contents are separately inventoried.

