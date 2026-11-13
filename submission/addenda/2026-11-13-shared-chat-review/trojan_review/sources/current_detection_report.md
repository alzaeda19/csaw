# Frozen-design detection evaluation — November 13, 2026

**The evaluation is complete. Stealth is not established: source review and the scoped formal comparison detect the existing modification.** The four supplied learned detectors also ran, but their graph-construction limitations prevent a whole-design stealth conclusion. A favorable label on an incomplete graph cannot repair that gap.

This addendum evaluates the existing clean and modified submission at base commit `65d4f51506d3cb09b49b16875bc3d9d833d89949`. It does not change the hardware, create a new modification, tune a detector, use published challenge solutions or program a board. The preregistered checks are in [TEST_PLAN.json](TEST_PLAN.json); source/package hashes are in [records/INPUT_MANIFEST.json](records/INPUT_MANIFEST.json).

## Results in plain English

| Check | Actual result | What it establishes |
|---|---|---|
| Qwen source review, labels withheld | Modified wrapper classified as extra output behavior; clean wrapper as pass-through | This reviewer can notice the visible added output expression. One pair is not a general accuracy estimate. |
| Same-flow synthesis comparison | 48 additional state bits and 44 additional generic cells, excluding scope metadata | The designs differ structurally. These generic counts include the mapped memory model; they are not physical FPGA area. |
| Independent formal comparison | Finds an output mismatch with data/mode unconstrained under the saved schedule | Detectable by this bounded white-box, compositional check. It is not an unrestricted full-cipher proof. |
| Fresh full-core simulations | Six runs, each with 270 transactions and 39,960 observed output triples; all four representation comparisons match their corresponding originals exactly | The raw and flattened analysis inputs preserve the tested behavior. The declared positive control shows the documented one-bit difference; the other 269 serial results agree. |
| HT1–HT4, raw-source representation | Clean: all CLEAN. Modified: HT1 TROJAN, HT2–HT4 CLEAN | Diagnostic only: the exact parser fails and the supplied tool falls back to an incomplete heuristic graph. |
| HT1–HT4, flattened representation | Both designs: all CLEAN | Authentic classifications of the saved graphs, but signal-name joining leaves thousands of disconnected references. They are not valid whole-design misses. |

All sixteen checkpoint/candidate classifications are saved, including unfavorable findings. There were no checkpoint/threshold changes or repeated representations selected to obtain a desired score. Both source representations were declared before inference. An environment preparation assertion was corrected before any detector result; the failed version and explanation are retained.

## Why the detector labels do not establish stealth

Raw inputs include the complete original core, the wrapper and the actual preprocessed RAM primitive definition. Both fail the package's exact parser at RAM-model `case` syntax. Its automatic fallback loses HDL hierarchy and other semantics. The HT1 flag is reported as a diagnostic finding, not promoted to complete-design validation.

The flattened inputs contain the full mapped logic and no unresolved module instances or remaining memories. They pass fresh simulations against their original versions. The exact graph backend then completes, but **successful parsing is not complete graph coverage**. The package joins signal references by replacing every underscore with a dot. With the actual underscore-containing identifiers, references and their definitions remain separate: 4,722 paired names in the clean graph and 4,765 in the modified graph. The modified MISO dependency graph has only three descendant nodes and does not reach the fault-state definition.

This is an incompatibility between the unchanged graph joiner and the underscore-preserving input names. A supplied preprocessing path normally removes underscores globally; these canonical `topModule.v` inputs use the package's built-in bypass to avoid corrupting generated identifiers. That choice was made before scores and applied equally. We did not rename the design after seeing results, repair or retrain the detector, or claim the resulting graph is semantically complete. The independent Trojan-chat review also checked that the model-input edges equal the incomplete saved-graph edges; normalization did not reconnect them.

See [graph coverage](analysis/GRAPH_COVERAGE.json), [all classifier scores](analysis/DETECTOR_COMPARISON.json) and [independent review](trojan_coverage_review/REPORT.md). Scores are model outputs, not calibrated probabilities that the circuit is compromised. One clean/modified pair cannot establish general sensitivity or false-positive rates; the four checkpoints are not four independent security certificates.

## Scope of the stronger checks

The independent [formal report](trojan_formal_review/REPORT.md) uses the unchanged existing edge-control harness: 325 samples, two transaction slots and an alternating-clock assumption. Data and mode are unconstrained. The equality assertion fails while the tool exits successfully. The core is the existing zero-output abstraction; identical real-core inputs and the independent output mask support a compositional divergence claim. Fresh full-core simulation corroborates the same word/mode and one-bit difference, but does not replay the formal witness's exact reset/idle timing.

The [simulation report](analysis/representation_validation/RESULTS.json) compares every sampled MISO/BUSY/LED triple after rising/falling edges and chip-select changes, following two reset clocks. Its 270 transactions use 135 fixed/seeded words in both modes. Unknown outputs are rejected. All four raw/flat-versus-original trace comparisons pass. These finite tests verify these transformations under the documented schedule; they are not arbitrary-history equivalence, physical timing, or stealth tests. The positive control was explicitly included, not independently discovered by simulation.

The [structural comparison](analysis/STRUCTURAL_COMPARISON.json) counts 4,722 versus 4,766 generic functional cells and 135 versus 183 state bits after mapping the RAM model to logic. These are not the earlier physical-target primitive counts. The earlier FPGA synthesis remains the relevant resource report: +36 LUT4 cells, +48 registers, +13 carry cells and unchanged RAM. Neither count establishes negligible physical overhead or concealment.

## Qwen and authentic records

Qwen performed two separate wrapper reviews and a final methods review, with no tools or write permissions. Comments were removed solely for the review presentations; identifiers and logic remained unchanged. This was label-masked, not double-blind. The shared core was opaque to those wrapper reviews. Qwen's correct classifications, incorrect explanations and final response are retained in [ai_logs/](ai_logs/), alongside exact requests, received streams and receipts. [QWEN_REVIEW_NOTES.md](QWEN_REVIEW_NOTES.md) identifies errors instead of silently accepting them.

The current user requests are in [records/](records/). The native-history export preserves visible messages and tool inputs through its explicit cutoff, excluding hidden reasoning/internal metadata and tool-output snapshots; actual run outputs are stored separately. This does not recover older missing dialogue. The independent reviews preserve their own authentic records, errors and cutoff manifests.

## What remains for the submission

The existing RTL, demonstration testbench, report, available AI logs and ZIP are present. This follow-up resolves the question of what these checks show; it does **not** close the original stealth objective. The existing modification is visible to source review and detected by the scoped formal comparison. The four detector results do not support a competing whole-design stealth claim.

The older twelve unavailable reviewer instruction bodies and one 6,178-character tool-output gap remain disclosed. New Qwen conversations cannot replace missing originals. Normal-operation evidence remains conditional on its documented protocol/model assumptions. Staff determine how the package meets the rubric; publication alone does not establish receipt or acceptance.

Key recovery is an explicit bonus. Board programming and a particular detector are not separate preliminary deliverables. Negligible overhead, sophisticated payload and full historical generation automation are higher-score targets. This evaluation does not create any of those properties.

## Reproduction and integrity

See [REPRODUCE.md](REPRODUCE.md). Run only in a new disposable analysis directory; source hashes identify the frozen inputs. No dependency installation or training is performed by the scripts. Runtime caches and simulator executables are omitted from the publication copy; commands, source inputs, stdout/stderr, graph/model inputs and results are retained. The publication manifest records all included bytes. Earlier sealed evidence is unchanged.
