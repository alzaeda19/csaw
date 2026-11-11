# Paired baseline / regenerated-bitstream behavioral regression

The immutable recovered baseline RTL and the logic decoded from the regenerated baseline bitstream produce identical nine-functional-port traces in all four executed cases. This is finite behavioral regression, not a formal proof, independent cipher validation, or physical board validation.

| Case | Transactions per model | Nine-port checkpoints | Full pin event timestamps | Trace mismatches | Supplied values |
|---|---:|---:|---:|---:|---|
| Original-host timing, 50 kHz | 88 | 26,336 | 15,502 | 0 | 8/8 match |
| Original-host timing, 1 MHz | 88 | 26,336 | 15,502 | 0 | 8/8 match |
| Original-host timing with pauses, 1 MHz | 88 | 26,868 | 15,502 | 0 | 8/8 match |
| Read at first BUSY-low, 1 MHz | 88 | 24,928 | 14,798 | 0 | 0/8 match; same baseline behavior |

Each model executes 352 transactions. Each case includes reset, the original plaintext readback, CS-high idle clocks, all four pairs of consecutive encrypt/decrypt mode choices without reset between pair members, eight original supplied-vector transactions, and 80 arbitrary-word transactions. Arbitrary words are equivalence stimulus only. The paused case stops the clock during both transfer and processing. All sampled outputs and transaction results were known, with no x/z output samples.

The source host program executes seven clocks after launch. These cases use that exact count with a 1 ns settled sample after each rising edge. BUSY first falls three clocks after launch. In the immediate-read case, both models return the supplied input word instead of the expected transformed word at all eight original-vector checks. Those counterexamples are preserved and reported as mismatches to the original expected value; equivalence passes because the two unchanged models behave identically. No readiness repair was made.

The shared testbench touches only the nine functional ports. It is adapted from the clean `baseline_confirmation_2026-11-06/tb/normal_tb.sv` driver, with its internal diagnostics removed and paired-transaction coverage added. The expected P/C values come only from the preserved original host program. The original host program is not executed.

`io_trace.csv` captures every port before/after clock edges and at sideband transitions and pause endpoints. Raw `pins.vcd` files are retained. Full VCD comparison uses the final value after delta-cycle settling at every timestamp in the union of both files. It retains all nine pins and unknown values from time zero through completion; no initialization window or signal is masked. This is functional, zero-delay comparison, not a routed timing simulation; intermediate delta-cycle ordering is not compared.

Both independent simulations use the same unmodified OSS CAD Suite Yosys `cells_sim.v`, including actual initialized `SB_RAM40_4K` behavior. No primitive is stubbed, and no target signal is forced. `NO_ICE40_DEFAULT_ASSIGNMENTS` is the Icarus compatibility define used for compilation. Icarus compiler and runtime report version 14.0 (devel), `s20260301-831-g1cb990b6f-dirty`; version output and compile warnings are retained. Compile warnings only concern inherited timescales.

The run occurred from 2026-11-07T17:23:29.246959Z to 2026-11-07T17:23:37.489144Z. Exact compiler/runtime commands, absolute working directories, start/end times, return codes, stdout and stderr are in `records/commands.json` and each run directory. Input snapshots and source hashes are in `sources/` and `records/source_manifest.json`. `records/input_preservation.json` verifies all copied sources were unchanged. `SUMMARY.json` and `records/case_results.json` contain machine-readable outcomes. `records/output_hashes.json` is finalized after logs close.

To reproduce in a fresh simulation directory, preserve the sibling `inputs` and `decode` files, copy this runner and testbench, and execute `python3 run_paired.py`. The runner deliberately refuses to reuse existing model run directories, preserving prior evidence.
