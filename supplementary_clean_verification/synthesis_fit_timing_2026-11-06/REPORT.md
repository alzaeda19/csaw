# Synthesis, device-resource and timing assessment

The unchanged repaired derivative **elaborates, synthesizes and maps to iCE40 primitives**. It fits UP5K core resources and completes place/route in the explicitly conditional SG48/automatic-I/O scenario tested. Its internal clock-path timing estimate meets the original 1 MHz target in that scenario. **Original-board fit, externally constrained timing and physical hardware validation remain unestablished.** No target RTL was redesigned to obtain these results.

## Verified stage summary

| Stage | Baseline | Repaired derivative | Qualification |
|---|---|---|---|
|Read/elaboration, process lowering, structural/latch checks|PASS|PASS|Same unchanged candidate/adapter sources; library-only JSON compatibility handling described below|
|UP-family synthesis and technology mapping|PASS|PASS|Yosys `synth_ice40 -device u`; mapped-cell/latch checks pass|
|UP5K packed resource capacity|PASS|PASS|1,443 vs 2,920 logic cells, of 5,280|
|Place/route|CONDITIONAL PASS|CONDITIONAL PASS|UP5K, hypothetical SG48, automatic I/O, seed 1|
|Internal clock-path estimate at 1 MHz|CONDITIONAL PASS|CONDITIONAL PASS|35.82 vs 29.25 MHz estimated Fmax, same backend conditions|
|Original-board package/pin fit|BLOCKED|BLOCKED|No original FPGA package or board pin mapping supplied|
|External input/output timing closure|BLOCKED / UNCONSTRAINED|BLOCKED / UNCONSTRAINED|No justified external delays, clock uncertainty or board timing constraints|
|Physical board, sign-off timing, synthesis equivalence|NOT RUN|NOT RUN|No programming, hardware test or equivalence proof performed|

The baseline comparison distinguishes repair overhead from common tooling issues. Synthesis/route success does not repair the baseline's previously demonstrated functional-readiness discrepancy. The derivative remains an intentional behavioral change, not exact recovery or original-bitstream equivalence.

## Evidence and constraints

The six original materials remain pinned to `9913ac31aa47a46de9cfb8f928be21ae4e249ad4` and were reverified before/after by size, SHA-256 and Git blob ID. Only those originals, this chat's own permitted artifacts and generic tool sources were used. No other chat, solution comparison, later challenge revision, quarantined work or user repository was accessed. This task did not contact or read the separate presentation chat.

Original `qualifier/README.md:2` identifies **iCE40-UP5K**. Original `ice40_cryptographic_IP.md:10,16` supplies the unified SCK maximum **1 MHz**, so nextpnr `--freq 1` supplies a justified internal period target of 1,000 ns. Clock domain `SCK$SB_IO_IN_$glb_clk` is actually identified by the backend.

The original host's numbers are **RP2040 GPIOs**, not FPGA package pins. The six originals do not provide an FPGA package, PCF, original FPGA-to-board pin map, I/O bank voltage/standard, input arrival times, output capture requirements or external clock uncertainty. Recovered tile-coordinate signal names are not substituted for package-pin evidence.

For an additional conditional check only, the backend was explicitly given `--up5k --package sg48 --freq 1 --seed 1`, with **no PCF**. It warns: `No PCF file specified; IO pins will be placed automatically`. The SG48 choice is a hypothetical supported tool scenario, not an identification of the actual board package. Automatic pad assignments in the generated physical JSON are retained as tool outputs and are not asserted to match original wiring. No invented board PCF or physical pin constraints were supplied. No other package or seed was tested.

Exact conditions are in `constraints/ASSESSMENT_CONDITIONS.json`; path qualification is in `constraints/TIMING_COVERAGE.json`. Full reports include the unqualified asynchronous paths; none is labeled passing.

## Resources and repair overhead

| Resource/unit | Baseline | Repaired | Change |
|---|---:|---:|---:|
|Mapped 4-input LUT primitives (`SB_LUT4`)|1,438|2,903|+1,465|
|Mapped one-bit flip-flop primitives, all variants|71|71|0|
|Mapped latch primitives|0|0|0|
|Packed UP5K logic cells (`ICESTORM_LC`), capacity 5,280|1,443 (27.33%)|2,920 (55.30%)|+1,477|
|Dedicated 4-Kibit EBR blocks, capacity 30|4|4|0|
|SG48-scenario I/O cells, capacity 39|9|9|0|
|Global buffers, capacity 8|3|2|-1|
|DSP / SPRAM blocks|0 / 0|0 / 0|0|

Logic-cell counts are packed units that can share a LUT and FF; do not add the LUT and FF rows to obtain occupancy. Baseline packing pairs 68 LUT/FF cells plus 3 standalone FF cells; repaired packing pairs 56 plus 15 standalone FF cells, with packer constants also counted in LC utilization. EBR occupancy is 4/30 = 13.33%, or 16,384 allocated bits of 122,880 dedicated EBR bits. Zero generic `num_memories` in the mapped Yosys statistics does not mean no RAM: four `SB_RAM40_4K` primitives remain.

The repair roughly doubles packed LC use (2.02x); its extra combinational ROM/readiness lookahead maps principally to LUTs rather than extra registers or EBR blocks. This is measured implementation overhead in this flow, not a guessed gate count. No resource overuse was reported in the tested runs. The tool reports 2,360 unused LCs for the repaired packed design, but this is not a guarantee for arbitrary package constraints or future modifications.

## Timing actually established

Final **post-route** estimates from `runs/route_*/report.json`, not the earlier placement estimates:

| Reported path class | Baseline | Repaired | Status |
|---|---:|---:|---|
|Clocked register-to-register critical path|27.914 ns|34.183 ns|Constrained to the 1,000 ns internal period|
|Estimated internal Fmax|35.8243 MHz|29.2543 MHz|Both meet 1 MHz in the conditional scenario|
|Asynchronous input to clocked endpoint|29.740 ns|34.380 ns|Delay estimate only; external arrival/setup contract absent|
|Clocked endpoint to asynchronous output|15.091 ns|14.548 ns|Delay estimate only; external capture/output constraint absent|
|Asynchronous input to asynchronous output|17.565 ns|14.745 ns|Delay estimate only; no external timing contract|

The internal clock-path calculation uses the backend's default UP5K delay model, idealized clock constraint and this single placement/routing seed. It is **not** vendor sign-off across voltage/temperature/speed-grade corners, minimum-delay/hold closure, jitter/uncertainty analysis or a measured maximum operating frequency. The original 1 MHz operating limit is not increased by these estimates.

The constant `$PACKER_GND_NET_$glb_clk` is reported as having no interior paths; it is not an additional qualified data clock. All external/asynchronous classes remain unconstrained, even though the tool prints finite delays or a positive slack histogram. These values cannot establish mode-0 MISO setup/hold, board propagation, external reset/control arrival or actual host sampling. Missing physical mappings also prevent carrying the automatic I/O route estimates over to the board.

## Tool acquisition and reproducibility

Yosys and nextpnr were not available on PATH; the older pinned Yosys source tree was preserved, not built in place. The official generic OSS CAD Suite ARM64 release `2026-11-06` was downloaded into this assessment and its SHA-256 was checked against the official release asset digest:

- Archive: `oss-cad-suite-darwin-arm64-20261106.tgz`, 525,491,059 bytes.
- SHA-256: `a3aa9a096eba850f664472d5989203e9bd20613d967b6ad0fd275126db0656b6`.
- Yosys: `0.70+344`, git identifier `2f2307ad6`.
- nextpnr: `0.11.1-88-g937c770c`.
- Official release: https://github.com/YosysHQ/oss-cad-suite-build/releases/tag/2026-11-06

The original metadata response, archive, complete bundle and identities are retained in `tooling/` and `records/tool_bundle_identity.json`. This generic tool acquisition is not additional target-design evidence. Actual used executable/library hashes are in `records/used_tool_identities.json`; actual version outputs are retained in command records. The bundle's synthesis library is identified separately from the earlier pinned simulation library; no post-synthesis functional/equivalence proof is claimed.

## Compatibility handling, warnings and preserved failures

No HDL compatibility patch or new target wrapper was necessary. The prior unchanged functional-role adapter is used for both candidates; it does not identify physical pins.

The first elaboration flows completed parsing, process lowering and checks but failed while serializing unused library whitebox processes to JSON. A separate flow version applies the library-whitebox blackboxing used by the synthesis flow before JSON export. This changes only library representation for the elaboration artifact; it is not a target repair.

The first mapped-cell assertions failed on one new-Yosys `$scopeinfo` debug-metadata cell in each design. The standard synthesis itself had completed and produced mapped JSON. The separate corrected flow removes only that metadata cell, then retains strict mapped/latch/driver checks and writes `mapped_clean.json`. `records/metadata_cleanup_verification.json` proves that **all hardware cell definitions, ports and nets are otherwise identical** between raw and cleaned JSON. `records/tool_flow_compatibility.diff` preserves the exact flow adjustment. The failed first runs, partial JSON, logs and warnings remain untouched.

Yosys's ABC `The network is combinational` warning is retained; ABC is mapping the combinational network between preserved FF primitives. Final strict structural checks report no problems, and the mapped designs contain 71 FFs and zero latches. No combinational-loop or undriven-signal problem was reported. This is structural checking, not formal equivalence.

The original bundled nextpnr launcher attempted home-directory cache/config setup during initial version/help calls and printed a permission error. All subsequent runs use the untouched same binary through `tooling/launch_nextpnr.py`, which confines XDG state to this assessment without changing HOME. The wrapper and launcher's contents are preserved; this is an environment adaptation only. No target repository action occurred. The version/help warnings and an unavailable Yosys `read_sdc` help query are retained; clock constraints were applied with nextpnr's supported `--freq`, not an invented Yosys SDC pass.

No ignored timing failures, force flags, loop exemptions, relaxed latch checks or target RTL edits were used to obtain success. No programming tool was run, and no board-programming bitstream was generated.

## Sources, preservation and next steps

The candidate hashes remain:

- Baseline: `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`.
- Repaired derivative: `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`.

`records/source_identities.json` records candidate/adapter origin and snapshot hashes. All six originals and all earlier source/tool/test/run trees are checked by `records/preservation_audit.json`. Exact task text and AI/native transcript limits are in `records/CURRENT_TASK_MESSAGE.txt` and `AI_RECORD.md`. Nothing was fetched from later challenge content or other chats.

To establish original-board conclusions, the missing original package and verified FPGA-to-board pin mapping, I/O electrical standard and externally justified timing budgets would be required. They must not be reconstructed from RP2040 GPIO numbers or automatically chosen pads. Physical-board validation and synthesis equivalence would be separate work, not implied by this report.

## Reproduce

From `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06`, use fresh labels:

```sh
python3 synthesis_fit_timing_2026-11-06/analysis/synthesize_02.py --candidate repaired --stage elaborate --label reproduce_elaborate_repaired_01
python3 synthesis_fit_timing_2026-11-06/analysis/synthesize_02.py --candidate repaired --stage synthesize --label reproduce_synthesize_repaired_01
python3 synthesis_fit_timing_2026-11-06/analysis/place_route.py --candidate repaired --label reproduce_route_repaired_01
```

The routing script deliberately uses the preserved `runs/synthesize_repaired_02/mapped_clean.json`, whose hash is recorded in every route result. It is not automatically redirected to the newly labeled synthesis run. For baseline, substitute `--candidate baseline`; `--pack-only` performs the capacity/packing stage. Every command writes a fresh directory with exact constraints, source identities, output and process timing; existing labels fail rather than overwrite a run. Generated physical JSON is a conditional tool artifact, not a board pin map. Presentation-ready verified conclusions are also provided in `PROGRESS_BRIEF.md`.
