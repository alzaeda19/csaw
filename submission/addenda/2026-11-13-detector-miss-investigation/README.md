# HT1/HT3 miss investigation — November 13, 2026

**HT3 receives different data for the clean and modified CSAW designs, but compresses them into the same final numerical summary. Its final classifier therefore gives the same answer. HT1 produces different summaries and scores, but still chooses CLEAN for both.** The diagnostic checks found no swapped-input or model-loading error. This explains the observed numerical behavior; it does not establish a training-data cause, a universal detector weakness or stealth.

The investigation used Qwen for text-only planning and review, then checked its statements against measured results. Both replies are preserved with corrections. Hardware, model weights/configurations, the already repaired extractor, feature mapping and decision rules stayed unchanged. No new Trojan, evasion method, threshold adjustment, training, HDL simulation or published challenge solution was used.

## Existing labeled designs: measured results

All **23** examples in the professor's `TJ-RTL-toy` archive were attempted: 9 annotated clean and 14 annotated infected. **18 passed the graph coverage gates**: 8 clean and 10 infected. The remaining five were unscored, not labeled CLEAN.

| Detector | Detected infected / 10 | Missed infected / 10 | False alarms on clean / 8 | Correctly passed clean / 8 |
|---|---:|---:|---:|---:|
| HT1 | 9 | 1 | 5 | 3 |
| HT2 | 10 | 0 | 6 | 2 |
| HT3 | 1 | 9 | 3 | 5 |
| HT4 | 0 | 10 | 1 | 7 |
| Existing any-positive ensemble | 10 | 0 | 6 | 2 |

HT1 missed RS232-T800. HT3 detected RS232-T500 and missed the other nine scored infected examples. Exact per-design outcomes, scores and false-alarm lists are in [PER_DESIGN.csv](analysis/PER_DESIGN.csv) and [FINDINGS.json](analysis/FINDINGS.json). HT2's high detection count comes with many false alarms; no detector is declared universally best.

All ten scored infected examples belong to the **RS232 family**. The five excluded examples are PIC16F84 and PIC16F84-T100/T200/T300/T400. Each parsed but failed the fixed coverage gate on an unresolved internal `top.c_in` register reference. Exact errors, coverage maps and command receipts remain under `runs/` and `records/`. [The source-reference inventory](analysis/UNSCORED_SOURCE_REFERENCES.json) records the declaration and reads; it does not prove complete HDL semantics or classify the source as malformed. No source was changed to make it pass, and no fallback graph was scored.

The supplied directory labels are annotations, not newly simulated behavioral proofs. Checkpoint training data and overlap are unknown. Repeated families and exclusions mean these numbers are **not held-out general accuracy**, and the ten positive cases are not ten unrelated circuit families. The missing five examples remain outside both scored denominators.

## Why HT3 gave identical CSAW scores

The two saved CSAW graph inputs have different verified hashes and node/edge content. They are the exact tensors from the preceding [detector repair](../2026-11-13-detector-repair/README.md). Each was replayed once through all four unchanged models with read-only diagnostic hooks. **All eight output-logit vectors reproduced the previous published values exactly.**

For HT3, both convolution-stage outputs and the post-pooling arrays differ in shape and hash between the two inputs. The configured global-max readout then produces **byte-identical 200-number summaries**, with 36 nonzero entries each. The subsequent linear classifier produces identical logits and the same class-1 score, 0.1632879823, for both inputs. Neither summary is zero and neither output is merely the final-layer bias.

In plain English: HT3 processes two different circuits, but its final summary is the same for this pair. The last decision stage has the same information and gives the same answer. This is the observed point of equality in the numerical pipeline. It does **not** identify which hardware feature was missed or prove why the learned weights produced that summary.

HT3 is not globally stuck at a constant output: it produced **15 distinct logit vectors across the 18 scored examples** and returned both class labels. No per-node attribution or concealment analysis was performed.

For HT1, the final summaries and logits differ. Its class-1 score changes from 0.0090214144 on the clean CSAW control to 0.0885529816 on the modified input, while the fixed two-class decision still selects CLEAN. That establishes numerical sensitivity on this pair, not reliable detection or the reason for its learned decision boundary.

All four models use the same graph input for a given design and the same configured architecture. They have different supplied checkpoint weights. There is no evidence here for the pasted response's claims that HT2 uses a separate resource-analysis pipeline or that HT1/HT3 are syntax-only detectors. HT4's false alarm does not prove faulty training labels or threshold misconfiguration.

## What was checked

- Exact professor-archive source hashes and the previous static intake screen match all 23 copied examples. Source bytes were preserved; HDL was parsed/preprocessed but never simulated. The dataset pickle and generation notebook were not executed.
- All eight checkpoint/config files match the professor's originals. Strict, weights-only loading succeeds; parameters are finite; all models use CPU evaluation mode, seed 0 and one thread.
- The prior repaired extractor and all 23 copied detector-package files are unchanged. Successful graphs preserve their reference joins and exact model-input edge sets, use the same 37-feature vocabulary, and have no unresolved bound references or unexpected unbound non-input references under the stated gates.
- Ground-truth labels are kept in a separate manifest and joined after inference. They are not passed into the model. The professor notebook's saved [inference-label excerpts](records/LABEL_CONVENTION_SOURCE.json) corroborate class 1 = TROJAN and the any-positive rule. Original training-label metadata remains unavailable.
- Read-only hooks call the original forward methods and return no replacement output. The eight exact CSAW replay results verify that these diagnostics preserve the previously measured output for those inputs.
- All preregistered inputs/scripts match their pre-inference hashes. There were 72 successful toy-example classifications, 8 diagnostic CSAW classifications and 5 coverage abstentions. There was one pass, with no score-driven retry or tuning.

These gates check the specific data-dependency representation. They are not a general parser proof or full clock, memory-cycle, physical-timing or cryptographic-semantics verification. Scores are model outputs, not calibrated security probabilities.

## Comparison with the earlier toy evaluation

The older toy run used the earlier extractor and scored all 23 designs. This run uses the already repaired extractor and stricter fail-closed coverage gates. The historical files remain unchanged. To avoid changing denominators, the table below compares only the **same 18 designs** that are scored now.

| Detector | Earlier detected / 10 → current | Earlier false alarms / 8 → current |
|---|---|---|
| HT1 | 5 → 9 | 4 → 5 |
| HT2 | 2 → 10 | 5 → 6 |
| HT3 | 0 → 1 | 1 → 3 |
| HT4 | 0 → 0 | 1 → 1 |

This is a comparison of evaluation pipelines on a fixed subset, **not evidence of model training or a guaranteed improvement in general accuracy**. The repaired connections can change both detections and false alarms. [FINDINGS.json](analysis/FINDINGS.json) retains every changed prediction and the excluded cases. The separate CSAW pair is never included in the toy-dataset counts.

## Qwen and the supplied response

Two local calls to `qwen3-csaw-agent:20261112234518` completed: planning and measured-findings review. The model digest is saved. Qwen had only the supplied text, no tools, no file-write access and no authority to change the experiment. Its full requests, received visible streams, responses and completion receipts are in [ai_logs/](ai_logs/). Qwen did not independently run the tests.

Both responses contained errors. The first incorrectly proposed that the two inputs should be identical and confused differing scores with differing labels. The second repeated a score/label confusion, overinterpreted coverage failures and called HT2 best without accounting for its six false alarms. [QWEN_REVIEW_NOTES.md](records/QWEN_REVIEW_NOTES.md) records accepted advice and every material correction. No model opinion is substituted for measured evidence.

The user-supplied response also contains unsupported explanations. Its final-answer portion and a source hash are retained, with [corrections](records/USER_RESPONSE_REVIEW.md). Its full supplied text is preserved locally as documented in [the provenance record](records/USER_ATTACHMENT_PROVENANCE.json); its reasoning preamble is not republished. The authentic current visible Codex record has a declared cutoff under `ai_logs/`. Tool-result exclusions and older unavailable AI records remain disclosed; no missing history is recreated.

## Reproduction

Use a new directory outside the sealed evidence bundle:

```sh
python3 scripts/prepare_replay.py /absolute/path/to/new-detector-investigation
```

Set `CSAW_DETECTOR_PYTHON` to a compatible interpreter and `CSAW_TOOL_SUITE` to the directory containing Icarus tools. Defaults identify the existing local setup and must be overridden on another machine. In the prepared directory:

```sh
python3 scripts/run_investigation.py
python3 scripts/analyze_results.py
```

The tested environment uses Python 3.12.1, PyTorch 2.10.0, torch-geometric 2.3.1, NumPy 2.5.4, NetworkX 3.2.1, PyVerilog 1.3.0, PyGraphviz 2.0.4, Graphviz and Icarus 14 development. Exact per-worker versions are retained. The controller uses Unix process monitoring, two concurrent workers, a 45-second extraction deadline, 90-second worker deadline and a sampled 2-GiB process-group memory guard. No GPU or training dataset cache is required for detector inference. Other environments are unverified.

The preparation helper was checked for matching input bytes without running another model batch. It does not overwrite existing directories. Do not alter frozen inputs or substitute fallback graphs to make failures disappear. Reproduction creates new records and should be labeled separately. Qwen is advisory and not required to reproduce the numerical tests; saved requests can be reviewed without making model-service calls.

## Submission meaning

This investigation is finished, with its findings and exclusions recorded. **The misses are investigated, not eliminated.** No detector or hardware was tuned to change the answer. The evidence explains HT3's identical scores on this pair and documents HT1/HT3 reliability on usable supplied examples. It does not establish stealth, universal normal operation or full challenge compliance. Historical AI-log gaps and instructor-acceptance uncertainty remain in the [current submission guide](../../CURRENT_GUIDE.md).
