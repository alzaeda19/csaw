# Repaired RTL versus synthesized netlist: functional verification

**Simulation agreement passes. A complete two-state state-transition proof passes under explicit matched-state initialization semantics. Unconditional independent-power-up equivalence is not proved.** An independent-reset bounded check passes eight steps; the intended 80-step check times out. Tool failures, untested monitors and negative cases remain distinct.

The target is only the intentional repaired RTL versus its preserved synthesized netlist. This report does not assert equivalence of the repair to the original bitstream, routed/physical equivalence, timing correctness or complete hardware validation. Neither candidate was changed to obtain a pass.

## Evidence summary

| Assessment | Verified result | Evidence |
|---|---|---|
|Matched post-synthesis regression|28 runs reproduce all expected outcomes; **14 RTL/netlist pairs have identical observations**|[Matrix](records/final_simulation_matrix.json)|
|Common completion-boundary bench|**1,115 checks pass** for each implementation; seven unavailable original D monitors explicitly untested per boundary run|[RTL](runs/final_pinned_boundary_default_rtl/result.json), [netlist](runs/final_pinned_boundary_default_gate/result.json)|
|Original unmodified RTL boundary bench|**1,122 checks pass** with each primitive-library version|[Pinned model](runs/full_RTL_pinned/result.json), [synthesis model](runs/full_RTL_synthesis_library/result.json)|
|Full-state next-function proof|**PASS:** 135 current-state bits -> all 135 next-state bits and MISO/BUSY/ICE_LED, for equal defined current state and equal inputs|[Proof log](formal/full_state_transition/yosys.log), [scope/initialization](formal/full_state_transition/coverage.json)|
|Initial-reset BMC, independent unknown RAM read state|**PASS, 8 steps (0–7)**; no state coupling, first reset/idle assumption|[Result](formal/bounded_reset8/result.json), [complete solver output](formal/bounded_reset8/stdout)|
|Reset-only 80-step BMC|**TIMEOUT, not proved**|[Result](formal/bounded_reset80_03/result.json), [progress](formal/bounded_reset80_03/bmc.stdout)|
|EQY partitioned equivalence|**ERROR**, partition construction segfaults; no partition counted as proved|[First attempt](formal/eqy_full_models/result.json), [metadata-clean attempt](formal/eqy_no_scope_metadata/result.json)|
|Standard matched-cell equivalence flow|**TIMEOUT** before final status/certificate|[Result](formal/builtin_full_models/result.json), [log](formal/builtin_full_models/yosys.log)|

There is no observed real candidate discrepancy in the completed tests. Error/timeouts are not proof of equivalence or evidence of a design mismatch. The complete machine-readable record is [final_verification_summary.json](records/final_verification_summary.json).

## Candidate and source boundary

The six original materials were reverified before/after against the receipt pinned to target commit `9913ac31aa47a46de9cfb8f928be21ae4e249ad4`. Only those originals, this clean chat's own permitted artifacts and already-pinned generic tools were used. No other chat, solution comparison, quarantined work, later target revision, published solution or user project repository was accessed. `/Users/al-zayedal-hassan/Documents/llm4chipdesign-hw` was not accessed or changed.

- Repaired RTL SHA-256: `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`.
- Synthesized mapped JSON SHA-256: `b9274fdac6870c7b04b67d73ae0206dab97d7f1d9da22793071aef823658e2d7`.
- The original synthesis output is the previous `synthesize_repaired_02/mapped_clean.json`. Its prior debug-only `$scopeinfo` cleanup is unchanged; no new synthesis or optimization was substituted for the assessed artifact.

The mapped JSON was exported mechanically using `write_verilog -noattr -noexpr`. No HDL behavior was edited. The simulation and formal candidate is this post-synthesis logical netlist, not the subsequently routed physical JSON. Exact source/copy/export/model hashes are in [source_identities.json](records/source_identities.json), [netlist_export.json](records/netlist_export.json) and the final summary. Source, netlist, primitive and proof-model copies remain unchanged.

## Identical stimulus and observation applicability

All comparison pairs use the same copied bench, timing, corpus and plusargs. The gate variant changes only passive hierarchical bindings to the escaped names of the same mapped state nets. All 32 original serial-bank Q bits remain available and are actually observed; none is replaced with a reference value.

ABC mapping removed original combinational D nets and the old `n1` enable diagnostic. Their absence is not hidden:

- The seven `ready_D` assertions in the original boundary bench are explicitly **UNTESTED** on both candidates in the common comparison bench, not counted as passing. Their original expectations remain in the untouched RTL-only bench, which passes all 1,122 checks with both libraries.
- The common bench retains all direct serial-bank Q readiness, immediate known-answer readout, cycle-count, reset, repeated-operation and status/MISO checks. It passes 1,115 checks on both implementations.
- The unavailable enable signal in the normal bench is explicitly X on both sides for diagnostic printing only. It was never used as a functional assertion. No output, expected value, delay or stimulus was changed to obtain equality.
- Original-D trace fields are omitted from the paired diagnostic trace because the synthesized observation point no longer exists. The gate's actual D equation is instead covered by the full-state next-function proof; it is not relabeled as the old unsynthesized D net.

Exact adaptations are preserved in [boundary diff](records/adapt_boundary_tb.sv.diff), [normal diff](records/adapt_normal_tb.sv.diff) and [observer diff](records/adapt_observe.svh.diff). Earlier harness sources remain immutable. The 14 pairs contain **24,194 identical structured observation records**, including checks, status/state traces and operation results. The count includes repeated diagnostic records; it is not an independent-vector count.

## Functional regression outcomes

With the pinned simulation library, each row is run against RTL and netlist:

| Case | Outcome on each |
|---|---|
|Default completion boundary|1,115 pass; 7 D monitors untested|
|1 MHz boundary, 1 ps post-edge sample|1,115 pass; 7 D monitors untested|
|1 MHz boundary, late-high sample|1,115 pass; 7 D monitors untested|
|Original pair immediate extraction|7 checks pass|
|Modeled original host, seven additional clocks|7 checks pass|
|106-word immediate expanded suite at 50 kHz|1,720 checks pass|
|106-word host expanded suite at 1 MHz|1,720 checks pass|
|106-word immediate suite at 1 MHz with clock-stopped pauses|2,152 checks pass|
|Premature extraction, two additional clocks|Two reads blocked; runner exits 5; no data success counted|
|Pre-edge sampling interpretation|Three expected failures retained|
|Four-additional-clock timing interpretation|Two expected failures retained|

The synthesis-version primitive library additionally runs the default boundary, host sequence and 106-word immediate suite at 1 MHz on both candidates: 1,115, 7 and 1,720 checks pass respectively. All 14 paired traces agree within their stated observation scope. The six nonzero outcomes in the matrix are expected blocked/negative cases, not unexpected regressions. Inner simulator return 0 for a blocked case is not called a pass: the runner separately records exit 5 and the unexecuted reads.

The boundary bench includes original known values, immediate result availability without a new idle clock, reset while processing, reset followed by a fresh operation, repeated operations without reset, stopped-clock holds and LED/BUSY consistency. The corpus and arbitrary-word inverse/determinism checks are original-derived model invariants, not new independent cipher oracles. “Host sequence” means the preserved logical clock/protocol sequence; supplied board MicroPython was never executed.

## Primitive versions and initialization

Both simulations compile real behavioral primitives, without a BLACKBOX simulation define:

1. The earlier pinned Yosys simulation library at commit `5e740962d0c7b8c21b6701fe7a70a5e7ebe28661`, SHA-256 `b5b2bcd86c0d6eea269015aaebff1d5fb66e7ec3f7eded0bde07406e5ac99527`.
2. The distinct library shipped in the preserved official OSS CAD Suite `2026-11-06` used for synthesis. Its exact hash is recorded, rather than pretending the versions are identical.

The RTL initializes 71 one-bit registers to zero. Primitive FF models likewise initialize their outputs to zero. All **16,384 original INIT bits** across the four `SB_RAM40_4K` instances match the synthesized parameter values exactly. RAM write clock and write-clock-enable are constant inactive (WE itself may be high); contents are fixed ROM data. The RAM read-data registers are not initialized by the model. They begin X in simulation and as nondeterministic state in formal models; they are not silently zero-filled. Reset-driven simulations and post-update sampling are explicit.

Full generic RAM/LUT/FF behavior is expanded for formal analysis. There are no blackboxed or external primitive cells in the bounded miter. The completed transition proof imports only supported combinational cells and does not use an “ignore unknown cells” option. Unused-library tri-state/memory warnings are retained; they are not counted as active blackboxed behavior.

## Completed formal scope

### All-state transition proof and its sequential implication

The proof checks every storage element in the expanded verification models: **75 positive-SCK FF cells carrying 135 bits**—71 one-bit target registers and four 16-bit RAM read registers. Automated coverage establishes that no storage Q bit is omitted and no non-state signal is silently treated as storage.

A verification-only abstraction replaces FF Q outputs with a shared, arbitrary, defined current-state vector, and exports every original FF D equation as the next-state vector. It removes only the FF instances and output-free debug metadata from these analysis copies. All LUT/ROM/control equations remain expanded. There is no primary-output equality assumption, no blackboxed ROM and no substituted expected result. The registered MISO output is included in the state relation, and its next-state equation is proved along with the other 134 bits.

SAT proves that for **all binary current states and all equal binary primary inputs**, every next-state bit and all three output functions match. The clock-coverage check confirms that all 75 storage cells use the same positive SCK. [state_coverage.py output](records/commands/) and [coverage.json](formal/full_state_transition/coverage.json) retain the mapping and initialization patterns. The solver reports `SUCCESS` on the complete miter, with no counterexample.

The defined initialization patterns match: 71 zeros on each side. For the 64 unspecified RAM read-state bits, the sequential interpretation requires **the same arbitrary initial values on the two sides**. They are paired, not fixed to zero. Under that explicit initial-state relation, the all-state next-function equality establishes an inductive, unbounded **two-state relational sequential equivalence**. This is a complete proof within that scope, not merely an eight-cycle test.

It is not proof of equality between two independently chosen unspecified power-up read states, four-state X/Z simulation equivalence, physical clocks or hardware. Those limitations must accompany any “equivalence proved” statement.

### Independent initialization bounded check

A separate miter keeps independent unspecified RAM read states, compares only MISO/BUSY/ICE_LED, assumes the first synchronous step has reset asserted, START low and CS high, and leaves subsequent inputs unrestricted. `--presat` checks assumption satisfiability. All three assertions are present; no outputs are assumed equal.

The **8-step check (steps 0–7) passes**. The 80-step attempt times out after 180 seconds while checking step 12; it does not report a completed bound and is not counted as a 12- or 80-step proof. Eight steps cannot cover a complete 32-bit write/compute/read transaction. The longer transaction evidence is simulation, and the unbounded formal result remains the explicitly state-related proof above.

## Failed and incomplete proof attempts

Both EQY attempts parse full models but crash in partition construction (child exit 139), including a retry removing only scope metadata. **Zero partition proofs are credited.** A standard `equiv_simple`/`equiv_induct` flow times out after 180 seconds before final status; intermediate “success” lines are not promoted to a complete proof. No candidate counterexample is inferred from these tool limitations.

The first bounded-miter preparation omitted harness process lowering and failed JSON export. The next attempt failed because edge-triggered formal checks needed clock conversion before lowering. The separate corrected preparation applies process/clock-property lowering, retaining all original core logic and the single-positive-clock assumption; its coverage report verifies the three assertions and absence of external primitives. All scripts, failed outputs, partial results and timeouts remain untouched.

The available toolchain is the previously verified official bundle: Yosys `0.70+344` (`2f2307ad6`), EQY `v0.70-2-g3301516`, Z3 `4.15.5`; actual Icarus/runtime versions are saved per simulation. No new tool download or target-content fetch was needed. Formal executables run with bytecode disabled and assessment-local state; the earlier tool bundle remains unchanged.

## Preservation, gaps and reproduction

All six originals, the repaired RTL, recovered baseline, mapped netlist, previous synthesis/route reports, tool copies, tests, logs and failures remain unchanged. The audit covers **33,748 artifacts across fourteen earlier trees**. See [preservation audit](records/preservation_audit.json). AI/native transcript/model limitations and the exact accessible task message are [AI_RECORD.md](AI_RECORD.md) and [CURRENT_TASK_MESSAGE.txt](records/CURRENT_TASK_MESSAGE.txt).

No board programming, attack implementation, physical timing test or comparison with another chat occurred. No equivalence to the original bitstream is claimed. Synthesis/layout timing conclusions remain those of the preceding assessment, not additional results of this functional task.

From `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06`, use fresh labels:

```sh
python3 post_synthesis_verification_2026-11-06/analysis/simulation_matrix.py reproduce_sim_01
python3 post_synthesis_verification_2026-11-06/analysis/transition_proof.py reproduce_transition_01
python3 post_synthesis_verification_2026-11-06/analysis/bmc8.py reproduce_reset8_01
```

The transition proof intentionally uses the preserved prepared models from `formal/builtin_full_models/`; the bounded command uses the preserved SMT model in `formal/bounded_reset80_03/`. Their hashes and full preparation scripts are retained. EQY/builtin preparation failures can be rerun with the corresponding scripts and fresh labels; a repeat may exhibit different solver runtimes, so timeouts are observed outcomes, not guaranteed reproductions. Existing labels fail directory creation. Every completed run preserves exact sources/constraints, versions, commands, outputs and waveforms where produced.
