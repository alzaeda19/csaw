# ROM disabled-read coverage correction

Strengthened only the ROM test coverage in a fresh experiment folder. **No candidate, baseline, primitive, adapter, readiness bench, normal-operation bench or existing runner was changed.** All copied inputs match their recorded earlier hashes. The stronger tests expose no new failure in the unchanged repaired derivative's exercised ROM forwarding.

## Confirmed gap and retained evidence

The earlier ROM test scanned addresses 0–511, leaving address 511/value zero loaded. Its RE-disabled check then used address 511 again. Retaining the old word and incorrectly reading a new word therefore both returned zero, for all four ROMs. That check could not detect ignored RE.

The subsequent RCLKE-disabled check changed to address 0, whose 16-bit mode-1 primitive output is `0x0541` for each original ROM. It was discriminating against the held zero. This work does not incorrectly describe the entire earlier disabled-read test as ineffective.

Fresh reproductions preserve the distinction:

| Test/control | Actual result |
|---|---|
|Unchanged earlier test|2,056 checks pass|
|Earlier test with synthetic forecast ignoring RE only|Still 2,056 checks pass: the gap is reproduced|
|Explicit regression requiring that control to be rejected|Fails, retained as `red_legacy_sensitivity`|
|Earlier test with synthetic forecast always reading|Four failures, caught by its RCLKE-disabled check|

`records/legacy_gap_analysis.json` records the exact old addresses, original-derived data values and discrimination flags for each ROM. The old scripts, results and reports remain unchanged; their earlier limited checks are not relabeled as this new stronger evidence.

## Stronger test and source-derived expectations

`analysis/strong_rom_test.py` rereads the four original RAM instances in the preserved baseline, verifies their INIT contents against the existing derivation descriptors, and derives all 512 mode-1 read values per ROM. The pinned `SB_RAM40_4K` model defines initialization packing, address masking, output bit packing and `RE && RCLKE` synchronous read/hold behavior. Expected values are calculated from those original INIT bits using those semantics; no guessed or substituted data is used.

For every possible held logical address A in each ROM, the generator deterministically selects the first address B whose decoded output differs from A. `runs/strong_ROM/stimulus_proof.json` records all **2,048 address/data pairs** and proves every A/B pair differs. Each original ROM has 256 distinct read output values. These are primitive-port values with mode-1 output packing, not newly inferred cipher known answers.

Each pair is exercised under all three disabled combinations: `(RE,RCLKE)=(0,1),(1,0),(0,0)`. Every scenario:

1. Reads A with both enables high and checks the forecast and pinned primitive against the independently decoded A value.
2. Changes the address to the demonstrably different B and disables reads.
3. Checks that the primitive has not changed without an edge; checks forecast and primitive retain A over two disabled rising edges.
4. Reasserts both enables, verifies the primitive still holds A before the next edge, then checks forecast and resumed primitive read against B at that edge.

That is **6,144 discriminating per-ROM hold/resume scenarios**, comprising **67,584 assertions**, all passing. The count includes forecasts, primitive outputs, no-edge behavior and stimulus-discrimination assertions; it is not 67,584 independent hardware states.

The forecast expressions and ROM INIT/word declarations are extracted from the **actual unchanged repaired candidate**, not replaced by an unrelated correct predictor. Only testbench signal bindings adapt its original address/control/current-output names to the standalone component harness. The reference primitive remains the unchanged pinned `cells_sim.v`. `rom_test_coverage.diff` shows the prior versus strengthened test source.

## Sensitivity controls kept separate

Eight explicitly synthetic controls ignore RE or RCLKE in just one selected ROM forecast: two fault types times four ROMs. Neither the real candidate file nor the pinned reference primitive is modified. Each synthetic control is identified by `fault`, `fault_rom`, and `synthetic_control_only` in its result.

All eight are rejected: each produces **1,024 forecast failures**, all in the deliberately selected ROM, with no primitive-output failure. `records/final_sensitivity_sensitivity.json` records the expected exit 1 and exact failing count per control. The sensitivity orchestrator exits 0 only because these failures are required and observed. These controls demonstrate detection of the specific omitted-enable faults; they are not an exhaustive fault model.

## Fresh readiness and normal-operation regressions

All runs use unchanged recorded candidates and fresh output directories:

| Regression | Actual result |
|---|---|
|Unchanged baseline strict boundary control|1,122 checks, **14 retained failures**|
|Same repaired boundary bench|**1,122 checks pass**|
|Original known-answer immediate read|Baseline: two failures; repaired: passes|
|Modeled original host clock sequence|Baseline and repaired pass|
|Repaired boundary at 1 MHz, 1 ps and late-high sampling|**1,122 checks pass per run**|
|106-word immediate/host invariants at 50 kHz|**1,720 checks pass per run**|
|106-word immediate invariants at 1 MHz with stopped-clock pauses|**2,152 checks pass**|
|106-word host invariants at 1 MHz|**1,720 checks pass**|
|Differential model regression|**864 comparisons pass** across 432 operations: repaired immediate and host results match unchanged-baseline host results|
|Extraction after only two additional clocks|Two reads remain **blocked**, runner exits 5; no data success is claimed|
|Pre-edge sampling interpretation|Three retained failed checks|
|Four-additional-clock timing interpretation|Two retained failed checks|

The unchanged 13-case matrix reproduces every expected outcome. `records/rerun_matrix.json`, `records/rerun_diff_differential.json` and `records/result_ledger.json` retain the classifications and exact results. The runner's result JSON `returncode` is the inner compiler/simulator code; for blocked extraction it is 0 while the runner correctly exits 5. Command/matrix records preserve that distinction. No unexpected readiness or normal-operation regression failure was observed.

The boundary bench retains immediate bank readiness, original known answers, reset during processing, repeated operations, clock-stopped holds, and status/MISO assertions. Arbitrary-word inverse/differential results are model/protocol invariants, not independent cipher oracles. The supplied board MicroPython was not executed; “host sequence” means the preserved modeled logical sequence.

## Identities, preservation and limits

Candidate hashes did not change:

- Compatibility baseline: `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`.
- Intentional repaired derivative: `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`.
- Pinned primitive model: `b5b2bcd86c0d6eea269015aaebff1d5fb66e7ec3f7eded0bde07406e5ac99527`.

Exact source/copy identities and final equality checks are in `records/copied_identities.json` and `records/final_copied_identities.json`. The generic model comes from the already-pinned Yosys commit `5e740962d0c7b8c21b6701fe7a70a5e7ebe28661`; its initialization/read semantics are around `cells_sim.v:1603–1656`. The original six-material receipt remains pinned to target commit `9913ac31aa47a46de9cfb8f928be21ae4e249ad4`.

All six originals were verified before/after by size, SHA-256 and Git blob identity. **12,472 files across twelve earlier artifact trees** retain exact membership and bytes, including the earlier ROM test/results, raw recovery, baseline, derivative, all tool copies and failure logs. The user repository was not accessed. `records/preservation_audit.json` records the audit; `OUTPUT_HASHES.json` inventories the new folder, excluding itself.

Limits: only the four original read-only mode-1 tables and binary RE/RCLKE controls are tested. All 512 logical read addresses are covered, with unused upper address bits fixed zero; not every ordered address pair, disabled-control transition ordering, X/Z case, initial hold before a first read, write behavior or other RAM mode is covered. The simulations are zero-delay functional evidence, not synthesis/resource fit, physical timing, electrical correctness, original-bitstream equivalence or hardware equivalence. The repaired derivative remains an intentional behavior change, not exact recovery. Previous sampling/counting limitations remain.

No stronger test exposed a new candidate implementation failure. Expected sensitivity failures, baseline failures, blocked reads and negative interpretations are explicitly separate from passing behavior. No failure was discarded or rewritten.

## Reproduce and logs

From `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06`, choose fresh labels:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/analysis/strong_rom_test.py reproduce_rom_01
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/analysis/sensitivity_tests.py reproduce_sensitivity_01
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/run.py --candidate baseline --label reproduce_baseline_01
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/run.py --candidate repaired --label reproduce_repaired_01
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/analysis/test_matrix.py reproduce_matrix_01
PYTHONDONTWRITEBYTECODE=1 python3 rom_disabled_read_coverage_2026-11-06/analysis/differential.py reproduce_diff_01
```

Baseline boundary is expected to exit 1. The study orchestrators exit 0 only when their required mixed outcomes occur. A direct synthetic fault control (`strong_rom_test.py FRESH_LABEL ignore_re 0`) is expected to exit 1. Existing labels intentionally fail directory creation. These commands require the already-present local Python/Icarus tools and no board or network.

Exact accessible task text is in `records/CURRENT_TASK_MESSAGE.txt`; available response copies and native transcript/model/timing limitations are in `AI_RECORD.md`. Run folders preserve generated benches, complete outputs, versions and waveforms; outer commands and output hashes are under `records/commands/`.
