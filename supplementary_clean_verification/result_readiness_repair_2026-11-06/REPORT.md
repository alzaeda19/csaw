# Intentional model-level result-readiness repair

The separate derivative `derivative/recovered_readiness_repaired.v` captures the processed word into the serial bank on the same SCK edge that completes the operation. Immediate readout now passes the original known-answer pair without an extra CS-high clock. BUSY timing and its original implementation are unchanged.

**This is an intentional behavior change to an original-derived simulation model. It is not exact recovery, not equivalent to the original bitstream, and not verified physical hardware.** No board was programmed, no bitstream was generated, and no synthesis, resource-fit, place/route, analog timing or hardware equivalence claim is made.

## Requirements and source basis

Only the six receipt originals, this clean chat's own artifacts and already-pinned generic tools were used. Originals are pinned to target commit `9913ac31aa47a46de9cfb8f928be21ae4e249ad4`; all six were reverified before and after by size, SHA-256 and Git blob ID. No other chat, solution comparison, quarantined work, later revision, published solution or user repository was read.

The original interface specifies unified SCK up to 1 MHz (line 10), synchronous reset (17), CS-controlled serial shifting (20), four operation clocks (47), no SPI while BUSY (48), and parallel loading when BUSY falls (49). Extraction follows in lines 53–55. The supplied host provides the only independent known-answer pair, `59C359C3` -> `9CD84392`, and its reverse (host lines 33–34, 85–91, 130–137). Its actual execution loop provides seven clocks after the launch edge (74/120), even though its nearby comment refers to three additional/four total clocks.

The repair targets the immediate BUSY-fall requirement, rather than using the host's spare clocks to mask the discrepancy. Four clocks are retained as launch L0 plus L1–L3, consistent with the host's four-total comment and the established recovered timing. A strict four-*additional*-clocks interpretation still fails its status checks and is retained separately. The interface wording does not itself resolve every edge-count convention; no completion indication was delayed to satisfy an alternative count.

Source identities are in `records/source_identities.json` and `records/reference_identities.json`. Exact raw recovery SHA-256 is `8203748cf74b6d969f8f42e07a5ce21407bfa640e5f9c8f6ab9c1886820ae902`. The simulation baseline is the existing declaration-only Icarus compatibility variant, SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`. The functional adapter is unchanged and does not establish physical board pin mapping. Generic sources remain IceStorm `00da9c3e6ceff056248e3451dd6fd3210d6ceec9` and Yosys `5e740962d0c7b8c21b6701fe7a70a5e7ebe28661`; actual Python/Icarus/runtime versions are recorded in run snapshots.

## What changed

The prior clean diagnosis established that a registered previous-BUSY detector produces a bank load pulse only after the completion edge. The original synchronous bank consumes it on the following edge, while CS-low on that edge instead selects shifting of the old input. Waiting without a clock does not repair this.

The derivative adds a combinational one-step lookahead of the *existing* recovered state transitions and the CS-high parallel-result cone. An enabled/reset FF is evaluated using its original current-frame RHS, with no recursive substitution into that RHS. The completion predicate is reset released, CS high, current BUSY high, and predicted post-edge BUSY low. On that edge, the 32 serial registers capture the predicted post-edge parallel word, with original reset priority. Otherwise their original enable and data behavior remains.

The cone includes synchronous RAM read results. The generator accepts only the four verified read-only mode-1 RAM instances: their original write clock/enable resolve to constant zero. It uses the unchanged original INIT contents and the pinned primitive's exact read address/mask/enable/hold semantics to compute the next read value combinationally. No cipher algorithm, key, expected-result constant or lookup table was guessed. The original RAM instances remain unchanged. This additional combinational read representation may have substantial hardware cost; none has been measured or validated.

`analysis/repair_derivation.json` records the parallel expressions, original FF forwarding, four RAM descriptors and all cloned aliases. The implementation changes only the 32 original serial-bank update statements and adds the lookahead declarations. The other **39 original FF updates**, original combinational statements, engine/status control, MISO staging and original RAM instances remain byte-for-byte intact. The legacy late load pulse remains; an idle CS-high clock may reload the same result, but it is no longer required for readiness.

`readiness_repair.diff` is the reviewable patch. `analysis/review.py` reverses exactly those changes and reconstructs the entire baseline byte-for-byte. It also reapplies the patch to a fresh baseline copy and verifies the derivative SHA-256 `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`. For the shared boundary schedule, **1,058 pre/post status trace events match exactly** between baseline and derivative: completion has not been delayed.

## Test results and classifications

| Test | Unchanged baseline | Repaired derivative |
|---|---|---|
|Strict completion/read-boundary bench|1,122 checks, **14 failures**|Same bench: **1,122 checks, zero failures**|
|Original pair, immediate extraction at L3 completion|Two original known-answer failures|Both modes pass|
|Modeled original host sequence, seven additional clocks|Pass|Pass|
|Boundary checks at 1 MHz, 1 ps and late-high sampling|Not newly rerun at these two offsets|**1,122 checks pass at each offset**|
|106-word normal invariants, immediate/host at 50 kHz|Host differential run passes|**1,720 checks pass per run**|
|106-word immediate invariants at 1 MHz with stopped-clock pauses|Not newly rerun|**2,152 checks pass**|
|106-word host invariants at 1 MHz|Not newly rerun|**1,720 checks pass**|
|Four mode-1 ROM lookaheads vs unchanged pinned primitive|Primitive is the component reference|**2,056 comparisons pass**|
|Result differential across 432 operations|Host sequence is the model reference|**864 comparisons pass**: immediate and host results match baseline host results|

The boundary bench directly checks the serial bank at completion against the original expected value, before any extra clock; immediately reads 32 bits; tests a stopped-clock hold and CS-only transitions; preserves the host's seven-additional-clock sequence; performs consecutive encrypt/decrypt operations without reset; and checks reset while processing followed by a successful fresh operation. LED/BUSY consistency and post-update MISO stability are checked throughout. The same unchanged boundary bench produced the baseline's failures and the repaired success. Waveforms and exact pre/post Q/D/status traces are retained.

The existing normal bench was copied, with its expanded-suite hardcoded seven extra clocks parameterized to the requested `extras`. Expectations, known-answer values and invariant checks are unchanged. A later telemetry-only addition prints operation results for differential comparisons. Both changes are shown in `records/final_bench_changes.diff`; every earlier run retains its exact bench snapshot. The 106-word corpus contains the original values, edge patterns, walking bits and deterministic generated words. Beyond the original pair, readback, inverse operations, determinism and differential equality are **model/protocol invariants, not independent cipher known answers**.

The differential study compares the unchanged baseline with seven additional clocks, repaired immediate extraction with three additional clocks, and repaired host extraction with seven. All 432 operation-result tuples in each run match; this strengthens the evidence that the repair changes readiness rather than the tested data transformation. It is not an equivalence proof or a new external oracle.

The ROM component bench checks all 512 mode-1 read addresses for all four tables and disabled-RE/disabled-RCLKE hold behavior. It compares predicted values with the pinned primitive after its edge update. Unknown-state behavior and all possible control transitions are not exhaustively proved.

### Preserved failures, blocked cases and limits

- `runs/baseline_boundary` preserves the 14 original-model readiness failures. `final_baseline_immediate` preserves both known-answer failures. Baseline host-sequence success remains distinct from strict boundary failure.
- Extraction after only two additional clocks remains **blocked**, with two requested reads not executed. The runner exits 5. The inner simulator's exit is 0; older result JSON's `returncode` is that raw simulator code, not the runner's classification. The command/matrix records preserve the runner's exit and blocked count, so this is not reported as a successful extraction.
- Pre-edge sampling retains three failed checks; post-update and late-high sampling pass. MISO remains registered on SCK rising exactly as before. This repair does not resolve physical mode-0 setup/hold behavior or actual firmware sampling. No standard-SPI electrical compliance is claimed.
- The alternative four-additional-clock status policy retains two failures. It is not used to retime BUSY or redefine the repaired readiness boundary.
- No new tests cover arbitrary START retriggering while BUSY, invalid SPI during BUSY, all X states, exhaustive state/input sequences, physical clock-buffer behavior or every electrical/reset corner. Reset and repetition conclusions are limited to the recorded cases.

All 13 test-matrix outcome classifications reproduce, including expected baseline failures and blocked/negative interpretations. These classifications are not a claim that every recorded command exits successfully. No final normal-operation repair test has an unexpected failure.

## Failed development attempts retained

The initial generator stopped on a missed leading-comment alias, then on an unsupported synchronous RAM output; neither failure generated a replacement guess. Adding explicit pinned RAM semantics exposed an overly conservative assertion that disallowed any bank-state reference. It was replaced with the appropriate time-frame constraint: forwarded FF RHS are original current-frame expressions, never the repaired RHS. Such references therefore do not form a combinational feedback cycle through newly generated wires.

The first generated derivative failed Icarus elaboration because its new control declarations followed procedural use. Its full source, patch, derivation and compile errors remain as `derivative/recovered_readiness_attempt_01.v`, `records/readiness_attempt_01.diff`, `analysis/repair_derivation_attempt_01.json`, and `runs/repaired_boundary_02`. The final version only fixes declaration order for that attempt. A premature runner invocation with no generated candidate also failed and remains as a partial run. One tool call used a nonexistent working-directory spelling and was rejected before execution; that native tool error is disclosed in the AI log. No failed attempt or run was overwritten.

## Preservation, logs and reproduction

All six originals and **11,933 files across eleven earlier artifact trees** remain unchanged, including every original/baseline adapter, pinned tool, earlier isolated version, test, waveform and failure. `records/preservation_audit.json` records exact membership/byte checks. `OUTPUT_HASHES.json` inventories the new folder, excluding itself. The exact accessible task message is in `records/CURRENT_TASK_MESSAGE.txt`; available responses and transcript/model/timing limits are in `AI_RECORD.md`.

From `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06`, use fresh labels:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 result_readiness_repair_2026-11-06/run.py --candidate baseline --label reproduce_baseline_01
PYTHONDONTWRITEBYTECODE=1 python3 result_readiness_repair_2026-11-06/run.py --candidate repaired --label reproduce_repaired_01
PYTHONDONTWRITEBYTECODE=1 python3 result_readiness_repair_2026-11-06/analysis/test_matrix.py reproduce_01
PYTHONDONTWRITEBYTECODE=1 python3 result_readiness_repair_2026-11-06/analysis/rom_test.py reproduce_rom_01
PYTHONDONTWRITEBYTECODE=1 python3 result_readiness_repair_2026-11-06/analysis/differential.py reproduce_diff_01
```

The baseline boundary command is expected to exit 1; the repaired command and study orchestrators should exit 0. Existing labels intentionally fail directory creation. Do not rerun generation scripts over existing derivative files; the final generator refuses to overwrite its output. All run sources, versions, commands, stdout/stderr and waveforms are retained beneath `runs/`, with outer records under `records/commands/`. No board, network or new package is needed for these tests.
