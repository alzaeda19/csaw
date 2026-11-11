# Recovered baseline versus regenerated bitstream

Executed on the user's native Mac on 2026-11-07. **Functional equivalence passed within the digital model and explicit state relation described below.** Both normal-operation transaction proofs and the paired simulations also passed. The unchanged baseline's immediate-read readiness failure remains present in both candidates.

This work compares the recovered baseline with a model independently decoded from the actual regenerated binary. It does not use the readiness-repaired derivative. All new outputs are contained in this isolated folder. No board programming or repository modification occurred.

## Verified results

| Check | Actual result | Exact scope |
|---|---|---|
| Binary decode and functional interface | PASS | Actual binary unpacked and decoded; nine functional signals checked against saved placement/configuration. This is not board package-pin validation. |
| Direct baseline-to-binary-decoded transition proof | PASS, exit 0 | All 135 next-state bits and MISO, BUSY, ICE_LED for every common binary input and every paired current state. |
| Independent-initialization full transaction, mode 0 | PASS, exit 0 | Every stable 32-bit payload, fixed original-host schedule, solver states 0–75; independently unspecified RAM read states. |
| Independent-initialization full transaction, mode 1 | PASS, exit 0 | Same scope as mode 0. |
| Final-read reachability, both modes | PASS, exit 0 | Completed compact traces reach state 74 with all 32 readback bits compared. |
| Paired simulation | PASS, zero model differences | 352 transactions per model, 104,468 nine-port checkpoints, 61,304 settled trace timestamps. Four cases and all four consecutive mode pairs. |
| Original-host known-answer checks | PASS, 24/24 per model | Original supplied values at 50 kHz, 1 MHz, and 1 MHz with clock-stopped pauses. These rates describe behavioral simulation, not measured hardware timing. |
| Read immediately at first BUSY-low | FAIL, 8/8 known-answer mismatches per model | Both models return the input rather than the expected transformed result. Their equality passes; readiness correctness does not. |

The simulation runner's “all_cases_pass” field means the two models agree and its protocol assertions pass. It intentionally retains the immediate-read known-answer mismatches as observations; that field must not be presented as proof that every baseline behavior meets the specification.

Evidence: [simulation summary](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/simulation/SUMMARY.json), [simulation methodology](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/simulation/README.md), [formal report](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/REPORT.md), [formal audit](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/FORMAL_AUDIT.json), [parent log/hash checks](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/parent_formal_review.json), and [parent simulation checks](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/parent_simulation_review.json).

## What the formal result means

The direct proof compares the unchanged recovered RTL with the behavior decoded from the delivered binary, not merely with the synthesis netlist. All four real RAM primitives on each side are expanded with a hash-pinned iCE40 behavioral library. No functional blackboxes or unexpanded memories remain. All state elements use positive-edge SCK.

The state correspondence is a bijection of 135 bits: 71 initialized-zero logic register bits and 64 unspecified RAM read-output bits. SAT proves equality of every corresponding next-state bit and all three outputs, with no protocol or output-equality assumptions. **Once the paired state relation holds, it remains true for arbitrarily long common input sequences, with equal outputs.** The sets of possible initial states correspond; this does not claim equal traces for two independently selected unspecified RAM states. A stronger repeat replaces the two optimizer-generated unknown branches with independent arbitrary defined values and still passes.

The separate bounded proofs leave those RAM states independent. They cover reset at cycle 0, release at 1, load at 2–33, launch at 34, seven additional clocks at 35–41, and read at 42–73. Output equality is asserted at states 1–74; the full 32-bit read is checked at state 74. Every stable 32-bit payload is quantified for each mode. Other source-defined initialization remains in force.

The finite simulation adds two consecutive transactions without an intervening reset and all mode transitions, clock pauses, and settled-edge observations. It does not establish a universal independent-power-up proof for every arbitrary sequence, four-state sequential formal equivalence, delta-cycle glitch equivalence, physical timing, or independent algorithm correctness.

An independent agent reviewed the paired models, complete state correspondence, clocking, primitive expansion, always-enabled transition assertion, bounded schedule, and final read sampling. It found no material proof defect. This is review of the saved proof and models, not a second independent implementation of the decoder or solver.

Final proof evidence: [transition success](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/transition_decoded_undef_independent/stdout), [state correspondence](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/transition_decoded_state_correspondence.json), [mode 0 proof](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/direct_transaction_mode0_bmc/stdout), [mode 1 proof](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/formal/baseline_mapped/direct_transaction_mode1_bmc/stdout).

## Candidate identities and execution

| Artifact | SHA-256 |
|---|---|
| Recovered baseline | 180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765 |
| Baseline functional-role adapter | 5c841870a9c4735e35f0dc1b07f6dfb7881898729ecf24e2408f73bb1b800089 |
| Regenerated binary, 104090 bytes | fa823078f0fef95a3b093b3db547a50030864c81c80a17ef445e86206cbc5fb7 |
| Preserved original challenge binary | 5fa5fda9768c36808780398d8e24d125d860aacc62b61af8b4c5124dd759ddbe |

The binary was independently unpacked to ASC and decoded with the existing pinned generic IceStorm tool. Two declaration-only edits make its output compile: a register output declaration and relocation of its initialization statement. No logic was repaired or replaced. The decoded functional adapter was checked against this build's placement/configuration. The final state correspondence is version 3; earlier mapping attempts are preserved.

Native environment: Darwin 25.2.0 arm64, macOS 26.2 build 25C56. Icarus/VVP 14.0-devel, Yosys 0.70+344 (2f2307ad6), and Bitwuzla 0.9.1. Exact tool hashes, commands, times, exit codes and stdout/stderr are retained in the per-run records. This task did not perform a new synthesis/place/route run.

Sources: [input manifest](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/input_manifest.json), [decode summary](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/decode/DECODE_SUMMARY.json), [decode commands](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/decode/commands.jsonl), [environment](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/environment.json).

## Failures retained and limitations

The following unsuccessful attempts remain available alongside the successful runs:

- Raw decoded Verilog compilation failed before the two declaration compatibility edits.
- The supplemental direct, unpermuted LUT encoding comparison did not match for 1315 cells. Its encoding/permutation cause was not established. It is not claimed as a passing check or as a functional counterexample; the actual decoded next-state equations were subsequently proved equal.
- Superseded decoder correspondence/record-sealing attempts and two formal alias-resolution failures are retained. Only version 3 correspondence is used in the final proof.
- EQY initially rejected unused generic blackbox declarations; after cleanup, its partition subprocess segfaulted. No success is attributed to either attempt.
- A generic sequential-equivalence attempt exceeded 240 seconds.
- Mode 1's initial full internal-wire cover trace timed out after reaching state 74. The partial trace is retained. Both later compact cover exports completed successfully.
- Minor help/path preparation failures are preserved in the formal report.

No counterexample to baseline-versus-regenerated functional equality was found in the completed checks. This conclusion relies on the decoder, signal-role correspondence, behavioral primitive models, and formal tool semantics. It is not an independent comparison against physical silicon or a new proof of the original binary's recovery.

## Board-readiness handoff

The existing build still assumes iCE40-UP5K/SG48, automatic I/O allocation, no board PCF, a 1 MHz target clock and seed 1. The supplied handoff's internal estimated Fmax of 35.8243 MHz is prior place/route evidence; it was not remeasured here and does not constrain external timing. **Do not treat this image's automatic pins as board wiring.**

Still needed before a board-specific rebuild: authoritative board/model/revision and FPGA package/speed grade; verified FPGA package pins and signal polarities; bank voltages, host levels and shared-net details; real clock/reset/host timing constraints; and the board's programming/recovery procedure. The functional-role adapter and BUSY/LED duplication do not identify physical board pins. No board was programmed or tested.

## Preservation and AI records

All six original challenge files, nine source build inputs and their copies, and the supplied handoff and its copy passed final hash comparison: 26 checks. Repository HEAD and clean status remain unchanged at a3006f61f55fd8b6a232377d292fcec3138bf1ae. No published solutions, contaminated folders, repository writes, hardware operations, or presentation work were used.

See [preservation receipt](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/records/final_preservation.json), [AI record and export limitations](/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/baseline_bitstream_equivalence_2026-11-07_20261107T172039Z/AI_RECORD.md), and the root OUTPUT_HASHES.json manifest. Existing failures and AI records were retained. The new AI record distinguishes authentic exported material from work summaries and records unavailable/encrypted portions explicitly.

