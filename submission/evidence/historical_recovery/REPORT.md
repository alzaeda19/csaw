# Baseline recovery and limited normal-operation verification

A structural Verilog simulation candidate was recovered directly from the receipt-pinned binary. It compiles after a declaration-only compatibility edit and uses the official Yosys RAM primitive simulation model. The unchanged protocol testbench's pre-update sampling fails all three data checks. A separately retained post-rising-edge sampling variant passes the original readback, encryption and decryption values, with BUSY and LED checks passing. This is limited functional evidence for an original-derived candidate, not complete target correctness, physical pin-map confirmation or cycle-accurate hardware validation.

## Original evidence and transformation chain

Target repository commit: `9913ac31aa47a46de9cfb8f928be21ae4e249ad4` from the existing SOURCE_RECEIPT.json. All six files were reverified before analysis. Binary: `../original_materials/qualifier/ice40_bitstream.bin`, 104090 bytes, SHA-256 `5fa5fda9768c36808780398d8e24d125d860aacc62b61af8b4c5124dd759ddbe`, Git blob `b309965e3c1519d3e54d5f87b2b45f2e0431ecb2`.

1. Official IceStorm source at commit `00da9c3e6ceff056248e3451dd6fd3210d6ceec9` was cloned into tooling/icestorm and only its icepack/iceunpack build was run locally. No system installation or board access occurred. Make/compiler output, including a duplicate-library linker warning, is retained.
2. `iceunpack` produced `raw/original.asc` (.device 5k at line 2). `icepack` repacked this ASC to a byte-identical binary. This confirms an exact pack/unpack round trip for these bytes; it does not prove Verilog translation equivalence.
3. Unmodified `icebox_vlog.py raw/original.asc` stdout was copied byte-for-byte to `raw/recovered_default.v`, 1213306 bytes, SHA-256 `8203748cf74b6d969f8f42e07a5ce21407bfa640e5f9c8f6ab9c1886820ae902`. An independent repeat produced identical output. It has 45711 lines, four SB_RAM40_4K instances and 71 native procedural-register declarations/always blocks; observed native sequential edges are posedge io_9_31_1. No cipher was identified or recreated.
4. Icarus rejects the raw tool output because output io_16_31_1 is implicitly declared as a net in the ANSI header (line 3) and redeclared as a reg (line 38460). `adapters/recovered_iverilog.v` changes only that header to output reg and converts the later initialized declaration to an equivalent initial assignment. All logic and tool-generated initialization values are retained. `records/declaration_compatibility.diff` and `records/derive_candidate.py` show the exact changes; raw output is unchanged.
5. The official Yosys source checkout is pinned to `5e740962d0c7b8c21b6701fe7a70a5e7ebe28661`; only `techlibs/ice40/cells_sim.v` is used as a generic primitive model, SHA-256 `b5b2bcd86c0d6eea269015aaebff1d5fb66e7ec3f7eded0bde07406e5ac99527`. Yosys itself was not built or run. RAM contents come from raw bitstream-derived INIT parameters (raw lines 42769–42784 and the other three instance blocks), not from invented target tables. The model's INIT_FILE default is empty (model line 1524); the target has no INIT_FILE override. Thus its optional readmemh branch (1607–1629) is not used.
6. `adapters/protocol_dut.sv` performs only port connections. No data corrections, extra target clocks, expected-output substitution, cipher/key implementation or fixture is used.

Every executable tool command after the command recorder was established has exact argv/cwd/start/finish/exit/stdout/stderr and output hashes in records/commands/. Build artifacts, complete tool source checkouts, failed attempts, compiled simulations, waveforms and source snapshots are retained. `records/derivation_hashes.json` records the principal candidate/model/harness identities; OUTPUT_HASHES.json covers the final artifact tree. See AI_RECORD.md for transcript limits.

## Functional interface mapping and its limits

References in this table are to **raw/recovered_default.v**, so they stay stable across adapters. Mapping is inferred from recovered connectivity and the original interface/host, then tested against the unchanged original vector pair. It is not a recovered board schematic or original PCF.

| Protocol role | Recovered port | Direct evidence / inference |
|---|---|---|
| SCK | io_9_31_1 | Raw 44315 and other 70 native always blocks use its rising edge; RAM RCLK connections 42796,42830,42864,42898. Consistent with original interface lines 10,16 (unified SCK). |
| RST_N | io_13_31_1 | Raw 44301 inverts it to n2843; 45705 aliases n2=n2843; synchronous FF reset terms use n2 (e.g.44315). Original interface 17,34 specifies active-low synchronous reset. |
| MOSI | io_16_31_0 | Raw 43628: with io_17_31_0 low, n2169 equals this input regardless of n630; raw 45031 clocks that term into n628 under shift enable. Original interface 18,40–41 specifies serial input during CS-low ingestion. |
| NORM_CS_N | io_17_31_0 | Raw 43628 selects serial input when low; other serial-bank muxes e.g.42912,42928 use the same selector. Raw 43089 and44492 derive n1 clock-enable from it, reset and n972 (which is clocked from BUSY, raw45167). CS-low input/readback checks support this role. |
| START | io_18_31_1 | Raw 43022,43626,44093,44237,44283 feed counter/control enables and BUSY-related state, rather than serial payload. Pulsing this input yields observed BUSY-high and completion in both directions. Original interface21,46; host61–78,113–124. |
| ENC_DEC | io_19_31_1 | Enters data-selection terms, e.g.43238 and43667, not the native clock/reset path. Original mode0 encrypt/mode1 decrypt sequence yields the supplied pair in the post-edge experiment. Original interface22,39; host59,96. |
| MISO | io_16_31_1 | Sole independent output apart from the duplicated status pair; raw45673 registers n2811 on SCK rising edge, with n2811=n800 at44269. Original host comparisons and the sampling experiment support the serial-output role. |
| BUSY / ICE_LED | io_8_31_1 / io_19_31_0 | Raw30051 assigns the latter directly to the former; raw43123/44526 drive the shared status. Interface23–24 says LED mirrors BUSY. The adapter chooses the former as BUSY. Swapping these equal outputs is functionally indistinguishable here. |

The originals supply RP2040 numbers (host5–14), but no direct RP2040-to-FPGA-package/tile mapping or package constraints. Package pin numbers were not guessed and no external board schematic link was followed. The above is a functional-role adapter, with physical wiring unverified. The duplicated outputs' physical BUSY-versus-LED identities cannot be resolved from their equal logic.

## Existing harness versus separately adapted sampling

The original harness source and records remain unchanged. `raw/harness_original/` retains the three source files used. `harness/` relocates its runner with the testbench byte-identical. Runner edits only relocate the restart-root path and permit the exact path+SHA-256 of the trusted official primitive library past its readmem-text guard; no test oracle/check/fixture fallback was altered. Exact diff: records/runner_relocation.diff. This hash-specific allowance admits only the known library; the recovered design has no external-memory-file dependency.

The first real-candidate run returns 4/SIMULATION_FAILED:

| Data check | Unchanged harness observed | Original expected |
|---|---|---|
| N04 readback | 2CE1ACE1 | 59C359C3 |
| N08 encryption | CE6C21C9 | 9CD84392 |
| N11 decryption | 2CE1ACE1 | 59C359C3 |

N05 encryption BUSY-high, N07 encryption complete, N10 decryption complete and N12 sampled LED mirror all pass. The data pattern is a one-bit-late stream (with the preceding output bit at the top), consistent with raw45673 registering MISO at the same edge. This falsifies the initial harness's pre-update-sampling assumption **for this zero-delay recovered model**. The original fixture had combinational MISO and did not expose this mismatch. It is not evidence that the binary implements a wrong cipher.

`harness_postedge/` is a separate diagnostic copy. It samples MISO one ns after SCK rises, after native nonblocking register updates, rather than before them. Clock stimulus, vectors, data comparisons and target are unchanged. Its diff also fixes trace time formatting: `%0t` uses global simulator precision (ps when cells_sim is included), despite the old label saying ns; `%0d` now reports the TB's ns-valued $time. This is trace-format correction, not timing stimulus change.

Post-edge results:

| Check group | Observed result |
|---|---|
| N01 | All six original size/SHA-256/blob checks PASS |
| N02/N03/N09 | Driver configuration passes; reset/decryption stimulus applied (not exhaustive reset behavior proof) |
| N04 | 59C359C3 returned, PASS |
| N05/N07/N10 | BUSY high after encryption launch and low after seven extra clocks in both modes, PASS |
| N08 | Encrypt 59C359C3 → 9CD84392, PASS |
| N11 | Decrypt 9CD84392 → 59C359C3, PASS |
| N12 | LED equals BUSY at checked samples, PASS |
| N06 default | Documentary timing UNRESOLVED |
| N06 launch-inclusive-4 policy | PASS: first sampled BUSY fall on additional pulse3 in both modes |
| N06 after-launch-4 policy | FAIL: expected additional pulse4, observed3; exit4 retained |
| N13 | Limited checks only; full target correctness UNESTABLISHED |

Original host loop supplies seven additional pulses even though its comments/interface mention four cycles (host72–78,118–124; interface47). Observation favors the launch-inclusive interpretation for this candidate. It does not rewrite the source requirement or prove all timing cases. Post-edge sampling is not claimed as conventional SPI setup/hold conformance or as a measured board SoftSPI sampling point. Original documents lack precise sampling delay; no board program was run. Original unchanged-harness conformance remains **failed**, and the separate adapted experiment must be named when citing passes.

## Tool diagnostics and remaining unknowns

- Raw generation and default recovery succeed. Optional exactly-one-driver check `icebox_vlog -D` succeeds with no failed-driver report; stripping its added driver-count comments gives byte-identical default output.
- Optional input-enable check `-R` aborts at the assertion in icebox_vlog.py256, for cell (9,31,1), the recovered SCK pad. A diagnostic-only copy adds assertion context; the tool source and recovered design were not patched to force this check to pass. This leaves an unresolved input-buffer/configuration validation issue; the evidence here does not determine whether the check/database is incomplete for this usage or the configuration has an input-enable concern. A simulated clock on the recovered model is not proof that this optional check is satisfied in hardware.
- The model is a tool-derived structural simulation, not recovered authored RTL, a named algorithm, a recovered key, a formal equivalence proof or a reimplemented cipher. Primitive support is a tool model assumption; no analog IO/timing model, synthesis/place-and-route equivalence or physical board execution was performed.
- Only the original single plaintext/ciphertext pair is available as an independent value oracle. Arbitrary inputs, broader algorithm correctness, key handling, out-of-sequence operations, reset priority, continuous LED behavior and physical timing remain untested (intake U02–U08). No outputs were hard-coded into the candidate.
- The first serial/control inspection command accidentally overescaped a regex and printed no matches; a corrected command is retained. One run-summary command matched a derivation log as if it were JSON and failed; records/summarize_runs.py corrected the selection. Neither failure changed target evidence. Raw-compile, optional-check and strict-policy failures are retained.

## Reproduce

From the restart root, use the archived tools and sources offline:

```sh
python3 baseline_recovery_2026-11-06/reproduce.py
python3 baseline_recovery_2026-11-06/records/audit_preservation.py
```

The reproduction script creates a fresh experiments/reproduce_<UTC>/ directory, verifies original hashes and tool commits, unpacks/repacks, regenerates raw Verilog, confirms equality apart from the source-path comment, reapplies only the declaration compatibility edit, connects the adapter, and runs both harness variants plus both explicit timing policies. It expects the original-sampling data failure and after-launch policy failure, and verifies the exact check outcomes. It never invokes a fixture. Exact compiler/runtime commands and versions are inside each appended harness run; tool commands and output manifests are inside the fresh experiment. The script's success means the documented mixed outcomes were reproduced, not that all protocol requirements passed.

Tooling-only references: [official IceStorm overview](https://prjicestorm.readthedocs.io/en/latest/overview.html), especially installation and IcePack/IceBox sections; [pinned IceStorm source](https://github.com/YosysHQ/icestorm/tree/00da9c3e6ceff056248e3451dd6fd3210d6ceec9); [pinned Yosys primitive model](https://github.com/YosysHQ/yosys/blob/5e740962d0c7b8c21b6701fe7a70a5e7ebe28661/techlibs/ice40/cells_sim.v). These support generic tooling semantics only. No later target repository content, solution, fork, walkthrough, other chat or existing project repository was accessed.
