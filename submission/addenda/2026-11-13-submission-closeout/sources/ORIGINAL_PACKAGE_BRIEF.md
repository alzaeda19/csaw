# CSAW 2026 — simulation demonstration and evidence

This package contains the preserved recovered baseline, an AI-authored modified interface wrapper, its testbench, a reproducible runner, technical brief, and available AI records. It is a checked simulation package for review. It has not been uploaded, programmed onto hardware, or certified as satisfying every grading criterion.

## Start here

- `HANDOFF_SIMPLE.md`: plain-English completed work and remaining limitations.
- `rtl/modified_protocol_dut.sv`: final modification; `rtl/baseline.v` is unchanged.
- `tb/demo_tb.sv`: normal-versus-modified comparison and documented fault demonstration.
- `ai/AI_RECORDS_INDEX.md`: authorship, exact logs, timeout/failure records and gaps.
- `evidence/final_runs/20261113T004430Z_hihzqs6r/result.json`: actual final-file test results.
- `SOURCE_HASHES.json`: frozen inputs used by the runner. `MANIFEST.json`: package contents.

## Reproduce the simulations

Use Python 3 and the compatible Icarus Verilog/VVP toolchain. The actual tested versions were **14.0 (devel), s20260301-831-g1cb990b6f-dirty**, from the preserved OSS CAD Suite. Full version output is in the final-run evidence. Tools are not bundled into this archive. Different versions/platforms are unverified.

From the extracted `submission` folder on this Mac:

```sh
python3 run_tests.py --tool-bin /Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06/synthesis_fit_timing_2026-11-06/tooling/oss-cad-suite/bin
```

On another machine, set `--tool-bin` to the directory containing compatible `iverilog` and `vvp`. The runner creates a new `runs` subfolder, verifies the frozen sources, retains command arguments, versions, stdout/stderr and exit codes, and returns zero only when all five test outcomes match expectations. It refuses to write results inside a Git repository. No original RTL is edited: deliberately broken control versions exist only in the new run folder.

## Final saved-file verification

The actual packaged sources were compiled and simulated on the Mac. Each real design run compiled and simulated with exit code 0.

| Test | Actual outcome |
| --- | --- |
| Unmodified baseline ordinary operation | 88 transactions; 6,726 checks; 0 failures |
| Modified wrapper ordinary operation | 88 transactions; 6,726 checks; 0 failures |
| Independent demonstration | 39,718 checks; 0 failures; 120 complete reads: 114 normal and 6 faulted |
| Control with the fault removed | Correctly rejected: simulation exit 1; 14 failures |
| Control with output permanently inverted | Correctly rejected: simulation exit 1; 9,209 failures |

The demonstration repeats 10 known-answer operations from the original plaintext/ciphertext pair. It observes exactly seven expected flipped samples: six complete faulted reads plus one interrupted read followed by reset. The counts are assertions and repeated examples, not thousands of independent cipher test vectors. The no-fault control has exactly seven MISO relation failures, six word relation failures, and one flip-count failure. All negative-control failures are retained and are expected evidence that the tests discriminate incorrect behavior.

The seven frozen runner/RTL/testbench files were also archived, freshly extracted into a different path containing spaces, hash-checked, and rerun. All five expected outcomes reproduced; see `evidence/portable_reproduction/result.json` and `evidence/SOURCE_ARCHIVE_CHECK.json`. This checks source-package relocation with the same external toolchain, not cross-platform compatibility.

Inherited timescale warnings are saved in compiler logs. No synthesis, place-and-route, physical timing test or board programming was performed for this new wrapper. Earlier project proofs apply to their own baselines/derivatives and do not prove this modification. The original baseline's extra-clock read-readiness limitation is retained; the tests use the supported host schedule.

Six original challenge files still match their source receipt. Four pinned source inputs match their saved hashes. Both existing repositories retain their previous HEAD and working-tree status, including pre-existing uncommitted audit files. See `evidence/FINAL_PRESERVATION.json` for the exact check scope. No GitHub changes, solution access, or key recovery was performed by this task.

# Technical brief: documented output-fault simulation

## Scope and status

This work adds an AI-authored interface wrapper to a preserved, bitstream-derived FPGA simulation model and demonstrates a publicly specified one-bit output fault. It is a simulation-only exercise. The recovered core is unchanged; the demonstration does not access secrets, recover a key, identify a cipher, optimize concealment, or evaluate detector evasion. No board was programmed or tested. Published solutions and set-aside materials were excluded from this work.

The original qualifier requests modified RTL, an exploit testbench, comprehensive AI transcripts, and a technical brief. This package documents its artifacts and evidence without claiming complete satisfaction of every grading criterion. In particular, physical wiring, synthesis/timing suitability of this wrapper, and hardware execution remain unverified. Historical AI records have acknowledged gaps; newly retained interactions cannot retroactively fill them.

## Baseline recovery and understanding

The preserved recovery report describes starting with the original qualifier binary, SHA-256 `5fa5fda9768c36808780398d8e24d125d860aacc62b61af8b4c5124dd759ddbe`. Official Project IceStorm tooling was pinned to commit `00da9c3e6ceff056248e3451dd6fd3210d6ceec9`. `iceunpack` produced an ASC configuration for a 5k device; `icepack` reportedly reproduced the original bytes. This is evidence of an exact packing round trip, not proof of Verilog translation equivalence. Unmodified `icebox_vlog.py` generated the structural Verilog candidate.

Icarus rejected an output declared as a net in the module header and separately declared as a register. The retained derivation script performs two declaration compatibility replacements: `output io_16_31_1` becomes `output reg io_16_31_1`, and `reg io_16_31_1 = 0;` becomes `initial io_16_31_1 = 0;`. The procedural driver and initial value remain. A separate adapter connects inferred protocol roles to recovered ports without substituting data or adding target clocks. The supplied baseline used here has SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`.

Primitive simulation uses official Yosys `techlibs/ice40/cells_sim.v` from commit `5e740962d0c7b8c21b6701fe7a70a5e7ebe28661`, SHA-256 `b5b2bcd86c0d6eea269015aaebff1d5fb66e7ec3f7eded0bde07406e5ac99527`. Yosys itself was not built or run for that recovery. Functional signal mapping was inferred from recovered connectivity and original interface material; it is not a recovered board pin map. The initial recovery report also retained an optional IceStorm input-enable check failure for the inferred clock pad. This is a historical failure record, not a claim that later validator repairs remain broken. This package does not independently validate physical clock-pin wiring.

The defensible algorithm interpretation is limited: the model accepts a serial 32-bit word, processes it under a mode/control interface, and returns a serial 32-bit result. Its structural logic includes state and four RAM primitives. The original example associates mode 0 with `59c359c3` → `9cd84392`, and mode 1 with the reverse mapping. That pair is consistent with the documented encryption/decryption roles, but does not identify a named cipher, establish invertibility for all inputs, explain a key schedule, or recover a key. The separate professor-provided AES reference is not evidence that this recovered system implements AES.

Sampling and completion timing matter. The initial unchanged harness sampled before recovered register updates and failed its three data comparisons. A separately retained experiment sampling one nanosecond after each rising edge passed the supplied pair. Later preserved evidence reports broader paired simulations and conditional digital-model equivalence; those historical proofs were not rerun here and do not prove this new wrapper. The present demonstration retains seven additional clock pulses after the START pulse, following the original host schedule. It does not claim that reading immediately at the first BUSY-low is valid; prior evidence recorded failures under that shortened schedule.

## AI workflow and authorship

The new generation workflow used local Ollama with Qwen3:8b, through Claude Code as the file-tool client, with model alias `qwen3-csaw-agent:20261112234518`. Codex coordinated the bounded task, reviewed generated files, ran simulation checks, and supplied substantive corrections. The use of Claude Code as a client should not be read as a claim that a Claude model authored the design.

Authorship is mixed AI authorship, not sole-Qwen authorship. Qwen's initial RTL compiled but failed nine ordinary checks. A second Qwen iteration applied a Codex-provided template but introduced code fences and a missing `end`, causing compilation to fail. Codex produced the corrected RTL, including explicit chip-select edge handling after reproducing a frame-boundary failure. Codex also authored the independent pin-level comparison testbench supplied to the subsequent workflow. The final Qwen attempt to save the testbench timed out after 360 seconds without producing the file. Codex then saved its already validated template directly. Retained failed iterations and correction records explain these changes; a final successful run does not erase them. The timeout receipt lists a concurrent report-file change made by the Codex report subagent; that inventory change is not evidence of Qwen authorship.

AI records must distinguish native prompts/responses, tool evidence, authored summaries, and reconstructed indexes. The correction record is supporting provenance, not a replacement for the conversations. Historical transcript incompleteness remains a limitation; no missing dialogue is invented or represented as authentic. The report does not claim comprehensive authentic transcript coverage for all prior recovery work.

## Trigger, payload, and interface behavior

The public demonstration word is `32'hC5A02026`. Qualification requires a completed 32-clock ingress frame while chip select is low, followed by a newly sampled START assertion while chip select is high and `ENC_DEC` is 0. The wrapper tracks ingress length and excludes the first 32 selected extraction clocks after START from ingress qualification. Chip-select deassertion clears the ingress counter even when no SCK edge occurs while chip select is high. Reset of the remaining wrapper state is synchronous to SCK.

For a qualifying operation, the wrapper inverts only the first sampled MISO bit of extraction. With the testbench's MSB-first convention, the resulting word must equal the unmodified core's result XOR `32'h80000000`. The other sampled output bits, BUSY, and LED must match the independent reference. The fault state clears after the 32 extraction clocks or a sampled reset. Partial extraction cancellation is demonstrated with reset; arbitrary partial-read abort and resume behavior is not established.

To reproduce the positive case in simulation: reset, shift the public word in MSB-first over 32 selected clocks, deassert chip select, select mode 0, assert START for one sampled rising edge, deassert START, supply seven completion clocks, then select and sample 32 output bits one nanosecond after their rising edges. Compare against an unmodified core receiving identical pins. The expected word difference is exactly `80000000`. Changing one input bit or using mode 1 is tested as a negative case.

The wrapper is deliberately documented and readily inspectable. No secrecy, obfuscation, resource-minimization result, or detector-evasion claim is made. Its chip-select-sensitive counter and digital output timing have not been synthesized or validated on hardware. These instructions describe a simulation mechanism, not a validated board exploit.

## Fresh template preflight evidence

`evidence/development_runs/final_template_preflight/RESULT.json` records successful Icarus compilation and simulation of the corrected template with the supplied baseline, wrapper, and primitive model. This is explicitly a **template preflight**, not the final packaged-artifact run. The parent packaging process records final reproduction commands, tool versions, artifact identities, and package-run results separately.

| Preflight measure | Observed result |
| --- | ---: |
| Checks / failures | 39,718 / 0 |
| Complete extracted words | 120 |
| Ordinary / faulted extractions | 114 / 6 |
| Original-pair known-answer operations | 10 |
| Expected / observed sampled bit inversions | 7 / 7 |

The seventh inversion occurs in a deliberately interrupted extraction followed by reset; it is not a seventh complete faulted read. The check count includes repeated per-clock assertions and must not be interpreted as 39,718 independent test vectors. The ten known-answer operations repeat the original supplied pair; they do not introduce ten independent cipher oracles.

The testbench compares separate modified and unmodified core instances through their public pins. Expected faults come from test-case inputs, not the modified wrapper's internal trigger state. Coverage includes all four adjacent mode pairs, 64 deterministic ordinary operations, all 32 one-bit neighbors of the public word, the other mode, consecutive triggers, subsequent normal operation, malformed ingress lengths, readout that carries the public word, selected pauses, held START, and reset cancellation. The START-while-selected case checks equality during ingress and then resets; it does not establish a complete valid transaction for that condition.

The ordinary runner uses fixed 1 MHz clocks, a one-nanosecond sample delay, the retained completion schedule, and no ordinary-run pauses; it is not a frequency or sampling sweep. The demonstration adds specific pause cases. Passing finite digital simulations supports only these tested behaviors and primitive-model assumptions. It does not establish universal equivalence, independent cipher correctness, physical timing, synthesis fitness, or a security guarantee.

