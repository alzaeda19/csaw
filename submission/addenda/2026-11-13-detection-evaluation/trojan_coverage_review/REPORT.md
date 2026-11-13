# Independent review of detector interpretation and graph coverage

**The reported limitations are justified. The four flat-source CLEAN labels do not establish full-design stealth.** They are authentic classifications of the generated graphs, but those graphs leave many signal references disconnected from their corresponding definitions. No source, detector, checkpoint, threshold or design was changed in this review, and no model, simulation or synthesis was rerun.

## Confirmed saved results

| Representation | Clean design | Modified design | Interpretation |
|---|---|---|---|
| Raw hierarchy | All four checkpoints CLEAN | HT1 TROJAN; HT2–HT4 CLEAN | Exact parsing failed before RAM `case` syntax and invoked the documented heuristic fallback. These are diagnostic classifications, not validated whole-design results. |
| Flattened source | All four checkpoints CLEAN | All four checkpoints CLEAN | Exact-backend extraction completed, but the graph-coverage defect below prevents a whole-design stealth conclusion. |

Both flat `RESULTS.json` files already set `valid_whole_design_result` to false. The term `exact_DFG` identifies a completed backend route; it does not certify complete hardware semantics. Neither detector probabilities nor four checkpoints constitute independent security certificates.

## Independently confirmed graph defect

The unchanged `DFGGenerator` calls `generate(..., walk=False)` separately for each binding, then attempts to join references to definitions. At source lines 396–400, its lookup replaces **every** underscore with a dot. Under this evaluation's underscore-preserving input flow, `top_read_count` becomes `top.read.count`, which does not match the actual definition label `top.read_count`. Generated `_NNNN_` signal names exhibit the same mismatch. This is a naming/normalization incompatibility in the current pipeline; this review did not alter either side.

The saved clean graph contains **4,722** concrete paired underscore names whose definition nodes have zero incoming edges and a nonzero outgoing edge while their reference nodes have incoming edges and zero outgoing edges. The modified graph contains **4,765** such pairs. These are counts of inspected name pairs, not an estimated percentage of missing hardware semantics.

The modified graph includes, for example:

- `top.read_count_graphrename_8801`: incoming 0, outgoing 1; distinct `top_read_count`: incoming 4, outgoing 0.
- `top.fault_active_graphrename_8775`: incoming 0, outgoing 1; distinct `top_fault_active`: incoming 2, outgoing 0.
- `top.ingress_count_graphrename_8785`: incoming 0, outgoing 1; distinct `top_ingress_count`: incoming 6, outgoing 0.

The exact nodes, neighboring edges and source-code excerpt are preserved. The graph sizes are 18,841 nodes / 19,839 edges for clean and 19,014 / 20,018 for modified. Every saved model-input edge matches the corresponding pre-normalization graph edge after indexing by the saved node order; later preprocessing did not reconnect these references. Merely counting disconnected components would not by itself establish a bug; the specific failed name joins supply the evidence here.

This does **not** establish that the naming defect caused any particular classification, or that a complete representation would change a model's verdict. No such experiment was run.

## Simulation and Qwen interpretation

Independent parsing of all six saved simulation outputs confirms 270 transactions and 39,960 observed MISO/BUSY/LED triples per run, with the recorded PASS lines. For each design, both raw and flat representations exactly match all original `T` observation and `R` transaction lines. Between clean and modified, only transaction 8 differs, with two differing sampled triples in that declared positive-control case. These are finite HDL trace-consistency results. They do not validate the downstream detector graph or certify stealth.

The two preserved Qwen replies classify the modified wrapper as `extra_output_behavior` and clean wrapper as `pass_through`, consistent with the supplied wrapper code. Candidate R's limitations are wrong about state location and visibility: the supplied wrapper contains `fault_active` and its setting conditions; they are not hidden inside `chip`. The finding can be retained with this correction. Labels were withheld, but source identifiers and logic were retained; this is not double-blind validation or a measured detection-accuracy estimate.

## Evidence and preservation

`REVIEW_RESULTS.json` contains the computed findings. `GRAPH_NEIGHBORHOODS.json` preserves exact selected node/edge evidence. `DFG_GENERATOR_EXCERPT.json` preserves source lines 362–420. `SOURCE_MANIFEST.json` records hashes and sizes for 37 read sources, all unchanged at completion. Small original results, extraction logs and Qwen request/reply files are copied exactly under `snapshots/`; large graphs, tensors and simulation logs are identified by hashes in the parent evaluation bundle rather than duplicated. Reproduction of the complete graph comparison requires that source bundle.

`review.py` completed with exit code zero. An exploratory combined console display was truncated; this did not truncate the underlying saved files. The successful review reads full files directly, and its results retain the distinction between display limits and missing source evidence. Current authentic visible AI records are exported with an explicit cutoff; missing older dialogue is not reconstructed. No new Qwen calls were made here. All writes were confined to this review folder.

The AI snapshot retains 24 visible records and 157 exact scalar fields from native lines 2394–2475, through 2026-11-13 06:08:41.121 UTC. It separately indexes 58 omitted internal/context/event records. Final sealing and handoff messages are after that snapshot.
