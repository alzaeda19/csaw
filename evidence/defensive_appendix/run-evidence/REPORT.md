# Frozen-detector evaluation of supplied existing designs

**All 23 designs completed once: 92 model results, 23 exact-DFG extractions, zero unscored designs. The original any-positive-vote ensemble detected 9 of 14 infected examples, missed 5, and falsely flagged 7 of 9 clean examples.**

This is a defensive graph-classification experiment on existing package data. No Trojan was generated or executed. These results do not establish security or completion of the course assignment.

## Results

TP means infected and flagged; FN means infected but missed; FP means clean but flagged; TN means clean and not flagged. All models scored the same 14 infected and 9 clean designs, with no missing results in these denominators.

| Detector | TP | FN | FP | TN | Recall: detected / 14 infected | False-positive rate: flagged / 9 clean |
|---|---:|---:|---:|---:|---:|---:|
| HT1 | 9 | 5 | 5 | 4 | 9/14 = 64.3% | 5/9 = 55.6% |
| HT2 | 6 | 8 | 6 | 3 | 6/14 = 42.9% | 6/9 = 66.7% |
| HT3 | 0 | 14 | 1 | 8 | 0/14 = 0.0% | 1/9 = 11.1% |
| HT4 | 4 | 10 | 2 | 7 | 4/14 = 28.6% | 2/9 = 22.2% |
| Any-vote ensemble | 9 | 5 | 7 | 2 | 9/14 = 64.3% | 7/9 = 77.8% |

The ensemble flags a design if any model predicts class 1 by argmax. No threshold was adjusted. It detects the same positive examples as HT1 while adding two false alarms on this set. No model selection or follow-up optimization was performed.

[Raw scores/results](RESULTS.json) · [Metrics and coverage](METRICS.json) · [92 model rows](per_design_model.csv) · [Readable design summary](per_design_summary.csv)

## Data and fixed method

The professor ZIP SHA-256 is `3912fd8e7afca470b57132c5af34215967c1b0e579ef2c0bc345de6a448c2832`; its nested datasets.zip is `6d66928a5fc73870e58d7265d4aa01b03788106c4bd1107d68b8fd73fcceec44`.

Only the 23 TJ-RTL-toy/{TjFree,TjIn}/*/topModule.v members were selected: 9 TjFree and 14 TjIn, all distinct source hashes, 386,410 bytes. The infected set contains four PIC16F84 variants and ten RS232 variants; their clean controls are each counted once. Previous CSAW/AES examples are excluded from every denominator. T100 suffixes are not interpreted as HT1 labels.

Archive bytes were copied into neutral design_001–design_023 folders. Truth labels come from archive directories, remain outside the inference manifest, and are joined after worker inference. They are supplied annotations; payload behavior was not simulated. Static screening found no includes, system tasks, foreign interfaces or dynamic-loading markers. The sole directive finding was a benign timescale. [Provenance](records/dataset_manifest.json), [screening](records/dataset_screening.json), [truth labels](records/truth_labels.json).

The four original checkpoint/configuration identities and ordered 37-feature vocabulary match the previous runs. Strict weights-only loading, CPU evaluation/no-gradient mode, log-softmax/argmax and the original any-vote rule were preserved. The training-graph pickle was not loaded. Forward inputs were node features, edges and batch indices; placeholder label zero was unused metadata.

The package recognizes the existing filename topModule.v and returns it unchanged. Optional concatenation, underscore removal and top renaming were not reapplied. Every saved graph input matches its original bytes. All 23 used the exact DFG backend; no heuristic fallback or large-table shortcut was used. This backend name is not a functional-equivalence or security proof.

The pre-execution policy specifies one pass, no retries/tuning, a 30-second graph deadline, 75-second worker wall limit, 60-second CPU limit and sampled 2 GiB process-group RSS guard, with two workers. Timeout/resource failure, empty/dummy graph, non-finite scores or incomplete results would be unscored. Ordinary parser failure could use the original package fallback with a separate error/route record; none occurred. [Frozen policy](records/EVALUATION_POLICY.json).

## Actual execution and verification

The run executed November 10, 2026, approximately 1:14–1:17 PM Eastern on native macOS 26.2 arm64. Controller and all 23 workers exited zero. Durations were 12.95–17.14 seconds per worker; largest sampled process-group RSS was approximately 556 MiB. No limit triggered. Sampling does not establish a true memory maximum.

Runtime: Python 3.12.1, torch 2.10.0, torch-geometric 2.3.1, NetworkX 3.2.1, PyVerilog 1.3.0, PyGraphviz 2.0.4 and Icarus Verilog 13.0. Shared packages are reused, so this runtime is not fully self-contained. Actual commands, exits, stdout/stderr and limits are under records/design_XXX; graphs, features, identities and results are under runs/design_XXX.

The only worker stderr was the Matplotlib font-cache notice. An optional version-probe helper initially failed because the dot command was absent; the error was retained and corrected to record not-found. The PyGraphviz backend worked. No design was rerun. [Environment](records/environment.stdout), [controller exit](records/controller_exit.json), [diagnostic failure receipt](records/version_probe_initial_failure.json).

Parent verification reproduced score/argmax arithmetic and confusion counts and passed 152 source/package/archive preservation checks. A separate reviewer passed all 1,053 static/artifact checks; the coordinating chat independently reproduced the metrics. These reviews did not rerun inference. [Independent review](records/method_review/INDEPENDENT_METHOD_ARTIFACT_REVIEW.md), [parent checks](records/RESULT_VERIFICATION.json), [preservation](records/preservation_check.json).

## Limits

- This small, repeated-family toy set does not establish generalization to independent designs or real hardware.
- Item-level checkpoint training overlap was not established. These numbers must not be described as held-out accuracy.
- Graph abstraction does not establish complete temporal/hardware semantics, payload activation, functional equivalence or Trojan absence.
- Softmax scores are not calibrated compromise probabilities. The observed false negatives demonstrate why CLEAN is insufficient as a security guarantee.
- No generation, training, evasion, payload simulation, outside datasets, published solutions, board programming, repository changes or old-experiment modifications were used. Repository status and HEAD remain unchanged.

[AI records and cutoff limits](AI_RECORD.md). This separate experiment leaves the previous partial submission unchanged; the instructor's scope decision remains separate.
