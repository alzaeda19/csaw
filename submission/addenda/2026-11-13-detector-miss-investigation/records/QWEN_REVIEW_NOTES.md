# Qwen advice and evidence review

## Planning reply 01

The completed local Qwen request and received stream are preserved under `ai_logs/01_planning/`. It had no tools and performed no tests.

Accepted: verify identities and handling; separate model scores from security probabilities; disclose unknown training overlap and lack of generalization evidence.

Corrections:
- The two candidate tensors are intentionally different. They should match their own recorded hashes, not each other or every stage. Qwen's request to confirm identical shape/hash across stages contradicts the supplied facts.
- HT1 labels both candidates CLEAN and HT4 labels both TROJAN. Qwen's statement that they show different labels is wrong; their numeric scores differ.
- Ground-truth labels are not inputs to the inference functions. Label interpretation can affect the names and confusion matrix but cannot explain identical raw logits in this implementation.
- Equal outputs for one distinct input pair establish equality on that pair only, not broad model invariance, robustness, or a training-data cause.
- The toy set can support observed TP/FN/FP/TN counts under this pipeline. It cannot establish training overlap, general accuracy or a causal explanation without additional evidence.

No hardware, model, threshold or graph-repair change was made in response to this advice.

The professor notebook was statically inspected for inference-label statements only. Its saved excerpts corroborate class 1 = TROJAN and the any-positive ensemble. This verifies the supplied inference convention; original checkpoint training-label metadata remains unavailable. The notebook was not executed.

## Findings reply 02

The second completed request received the measured findings, counts, stage comparisons and explicit uncertainty. It had no tools and did not independently reproduce them.

Accepted: all four TP/FN/FP counts match the scored 18-example subset; five abstentions and training-overlap uncertainty should remain visible. There is no evidence connecting training history to these outcomes.

Corrections and rejected claims:
- HT1 and HT4 do not have identical class-1 scores across the CSAW pair. Each keeps the same class label for both designs but has different scores. No label misalignment or training bias follows from that.
- For the CSAW pair, only HT3 has an identical readout and identical logits. HT4 has different readouts and logits. Duplicate score vectors elsewhere in the toy set do not establish the same mechanism without a separate comparison.
- HT3 is not globally constant because 15 distinct logit vectors were observed across the scored examples. Identical outputs on a pair would not, by itself, prove this.
- The measured pair-level mechanism is an identical max-readout summary after distinct pre-readout tensors. Why the learned weights yield that summary remains unknown. The low toy-set detection count does not identify a training cause.
- The five excluded files parse but have an unresolved internal register reference under this abstraction. Calling them malformed is unsupported; the source occurrence inventory is not a complete semantic proof.
- Reproduced logits show reproducibility. Independent byte-hash checks establish unchanged hardware, extractor, model/config files and inputs; matching scores alone would not establish byte identity.
- HT2 has the highest observed detection count but falsely flags 6 of 8 clean examples. 'Best performance' is not justified without specifying how misses and false alarms are weighted.
- Qwen's abbreviated HT3 missed-design list must not be read as including RS232-T500, which HT3 detected. The complete exact lists are in analysis/FINDINGS.json and PER_DESIGN.csv.

The report uses measured records and these corrections, not the model's unsupported causal claims. No third call was needed to change the experimental conclusions.
