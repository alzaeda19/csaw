# Frozen-design differential detection check

**The modification was detected by this check.** One fresh run of the existing edge-explicit formal harness found a legally framed input for which the modified output differs. This is evidence against invisibility to this particular white-box comparison, not a universal stealth score or an evaluation of every detector.

The run used the unchanged `formal/edge_control.ys`, unchanged harness and unchanged modified wrapper copied from commit `65d4f51506d3cb09b49b16875bc3d9d833d89949`. It completed on macOS with Yosys 0.70+344, git `2f2307ad6`, in **2.625 seconds**, exit code **0**. The solver's result is **`SAT proof finished - model found: FAIL!`**: the output-equality assertion failed because a counterexample exists; the tool itself executed successfully. Exact commands, stdout, stderr, witness and timing receipt are in `formal/edge_control/`.

## What the solver was allowed to choose

The unchanged script enables `ALLOW_DISCLOSED_FAULT_CASE`, disabling the harness's two data-exclusion assumptions. Both 32-bit transaction words and both stable direction bits are arbitrary. Extraction MOSI is arbitrary. The only active `assume` statement fixes alternating clock phases. Reset, serial framing, START and readout timing are supplied by the prescribed two-transaction schedule; these timing/control inputs are not unconstrained. The bound is 325 global samples.

No input word or direction value was supplied as a solver assumption. The solver has access to the modified RTL, including its visible comparison logic. Reviewers already know the documented design, so this is not a blinded source-review experiment.

The solver selected first word `c5a02026` in mode 0. The abstract output differs at cycle 43, visible at WaveJSON indices 86 and 87. The second transaction is available in the harness but is unnecessary to witness the first difference. `ANALYSIS.json` records all selected values and the active assumptions.

## What is abstracted, and what corroborates the result

This existing harness substitutes a zero-output `chip` to expose the wrapper's XOR output mask. It is **not** a newly run full-cryptographic-core equivalence miter. The baseline and modified adapters connect the same six input signals directly to the same recovered core; BUSY and LED are direct outputs. The output-mask logic is independent of core outputs. Thus a mask-one event means a different MISO bit for a coupled, determinate real-core output. The check does not establish cipher correctness.

The preserved original full-core simulation supplies corroborating evidence for the discovered word and mode. Its `trigger_no_gap` case produces baseline `a9ddcba5`, modified `29ddcba5`, XOR `80000000`; only the first extracted bit differs. The actual serial trace was independently decoded, and its core/wrapper/primitive/testbench hashes match the frozen files. That historical simulation's 39,718 checks passed, including the expected difference. BUSY and LED agree in the corroborating case.

This task did **not** rerun simulation. The saved simulation uses different idle/reset spacing from the complete formal witness, so it corroborates the input/mode and observed bit change, rather than replaying the exact whole solver trace. Original simulation logs and command receipts are copied under `historical/simulation/`.

## Limits and preservation

- The result establishes an observable difference within one prescribed digital protocol/model. It does not measure physical timing, board behavior, side channels, random-test hit rates, detector recall or broad stealth.
- Earlier normal-operation proofs deliberately excluded the exceptional input in the relevant mode. This check includes it. The results therefore do not contradict one another.
- The test was neither changed nor optimized after observing the result. No RTL, trigger, concealment or attack logic was generated or modified. No solution material was used. No Qwen/model call was made in this independent subtask; the coordinating chat handles its separate Qwen reviews.
- All 18 copied source/evidence inputs match their original hashes after execution. Git HEAD remains the stated commit and the repository status is clean. This task wrote only inside its isolated folder.
- Raw Yosys WaveJSON contains invalid backslash escapes in internal signal names, causing a strict JSON parsing error. The error is retained in `records/PARSING_ERRORS.json`. The raw file is unchanged; six original valid signal lines were selected and parsed with their source line numbers/hashes. This analysis correction did not rerun or alter the formal check.
- Two exploratory console displays were truncated while inspecting old witness/simulation evidence. Complete source files were copied and checked directly; the final formal stdout/stderr and witness are saved to disk without display truncation.
- `ai_records/` preserves bounded authentic visible audit records and exact-field verification, with a stated cutoff. Hidden reasoning, platform content and duplicate events are excluded; future sealing/handoff messages are outside the snapshot. These new records do not replace missing historical AI dialogue.

The current AI snapshot retains 28 visible records with 185 verified scalar fields, covering native lines 2276–2367 through 2026-11-13 05:59:20.850 UTC. Its 64 excluded records are separately indexed. The record exporter exited zero.

`records/SOURCE_MANIFEST.json` identifies every copied input. `records/SETUP.json` records the environment and tool identity; `records/PRESERVATION.json` records the unchanged inputs and repository state. `MANIFEST.json` seals this bundle. To repeat the same check, first copy the bundle to a new folder, then use the existing runner with a compatible Yosys executable; do not rerun inside sealed evidence.
