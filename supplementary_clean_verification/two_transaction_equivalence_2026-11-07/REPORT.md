# Two consecutive transactions without reset

The unchanged repaired RTL and its preserved synthesized netlist pass bounded equivalence through two consecutive complete transactions in all four mode combinations. Each assertion proof quantifies every pair of independent 32-bit payloads (2^64 pairs per row), with initially unspecified RAM read states independent between implementations. All DUT state carries through the intertransaction interval; only the initial reset is asserted.

| Mode pair | Universal assertion proof, 141 states | Separate existential reachability and audited traces |
|---|---|---|
| Encryption → encryption (`00`) | [PASS](formal/pair_00_v2/bmc.stdout), 183.68 s | [PASS](formal/cover_00_final_01/cover.stdout), 65.72 s |
| Encryption → decryption (`01`) | [PASS](formal/pair_01_v2/bmc.stdout), 196.22 s | [PASS](formal/cover_01_final_01/cover.stdout), 66.89 s |
| Decryption → encryption (`10`) | [PASS](formal/pair_10_retry_01/bmc.stdout), 295.16 s | [PASS](formal/cover_10_final_01/cover.stdout), 69.13 s |
| Decryption → decryption (`11`) | [PASS](formal/pair_11_retry_01/bmc.stdout), 303.79 s | [PASS](formal/cover_11_final_01/cover.stdout), 65.31 s |

Both complete read words are compared at states 70 and 139, with 32 observed bits each. The separate [trace audit](records/trace_audit.json) confirms both full input loads, launches, BUSY processing intervals, sample counts, and complete result reads for each witness. The [machine-readable matrix](records/result_matrix.json) records exact coverage. These are two-state, protocol-constrained bounded results. Unrestricted and unbounded equivalence remain unproved.

## Source-derived schedule and retained state

The original [IP guideline](../original_materials/qualifier/ice40_cryptographic_IP.md) requires synchronous active-low reset, mode selection before input ingestion, 32 load clocks with CS low, START for at least a clock, four processing clocks, no SPI while BUSY, and 32 read clocks followed by CS high. It does not require resetting between operations. The original [host example](../original_materials/qualifier/spi_ice40_crypto_ip_test.py) resets before decryption and therefore does not itself demonstrate this requested sequence. Its loop supplies seven extra clocks despite a four-total-clock comment. This assessment explicitly selects the guideline's four-total-clock schedule; it does not silently claim to reproduce that seven-clock loop.

| Edge/current cycle | Operation and controls | Observation |
|---|---|---|
| 0 | RST_N low, CS high, START low | One synchronous initial reset |
| 1 | Reset released; idle | Initial idle clock |
| 2–33 | CS low, payload1 MSB first | 32-bit load1 complete at state 34 |
| 34 | CS high, START high | Launch1 L0; BUSY already responds combinationally to START |
| 35–37 | CS high, START low | Three further compute clocks, completion at L3 |
| 38–69 | CS low, payload1 echoed on MOSI | 32 read1 clocks; MISO observations at states 39–70 |
| State 70 / edge 70 | Final read1 check; CS high, START low; select mode2 | Exactly one intertransaction idle clock |
| 71–102 | CS low, payload2 MSB first | 32-bit load2 complete at state 103 |
| 103 | CS high, START high | Launch2 L0; combinational BUSY high |
| 104–106 | CS high, START low | Three further compute clocks |
| 107–138 | CS low, payload2 echoed on MOSI | 32 read2 clocks; MISO observations at states 108–139 |
| State 139 | Final read2 check; CS high | No extra DUT edge needed to complete observation |

Mode changes at state 70 after the first read has completed, while CS is high and START low, before edge 70 and the second input load. It remains fixed during each operation. This is a permitted choice consistent with setting mode before ingestion, not proof about every possible mode-change point. There is one initial idle clock and exactly one intertransaction idle clock; no hidden flush clocks, reinitialization, or intervening reset. MOSI is zero outside the four SPI frames. Each read echoes its own payload as dummy MOSI, following the original host's transfer style. Payload2 is an independent anyconst32 and has no dependency on payload1 or a result. Both payloads are stable symbolic words; the cover solver's chosen values do not restrict assertion proofs.

## Bound, observers, and obligations

State 0 is before the first modeled positive SCK edge. The final check is after 139 DUT edges, at state 139. The 141-state bound includes states 0–140; state 140 is beyond the transaction guard, not additional transaction evidence. SCK is an abstract global positive-edge step, not a literal VCD frequency or electrical timing claim.

MISO, BUSY and ICE_LED equality are asserted continuously at states 1–139, including the intertransaction interval. State 0 before reset is excluded. BUSY-high expectations cover 34–37 and 103–106; BUSY-low expectations cover 38–102 and 107–139. The primary equivalence assertions also cover the initial load. There are nine assertion cells: three output equalities, two phase-status assertions, and two sample-count plus two complete-word checks.

Each observer registers the first 31 MISO observations (states 39–69 or108–138) and joins them with current MISO at state 70 or139 for a complete 32-bit word. The final assertions require the corresponding registered count 31; the second also verifies that the first count stayed31. All observer initial zero bits have shifted out of the final compared words. Separate observers for both operations exist from the initial state; they never reset or drive DUT state. Covers at states 70 and 139 require the relevant counts, and complete traces explicitly audit all 64 read observations.

Each model retains 135 DUT state bits. The source defines 71 initial zero FF bits per side. Each side's remaining 64 RAM read-state bits are unspecified, with 128 independent bits total across the miter. [Alias-aware audits](records/model_independence_audit_v2.json) verify that those RAM bits are actual disjoint DFF state with no defined initialization anywhere on their aliases. Fixed original ROM contents remain. Only checker cycle/sample/read-observer registers have explicit checker-zero initialization.

There are two independent width 32 anyconst cells, no assumption cells, no functional blackboxes, and no cross-implementation state pairing or equality assumption. Controls are generated from the counter, so zero assumption cells does not mean unrestricted input timing. Both unchanged full primitive-expanded models are included in [models](models/). The proof uses full unrolling, not a paired-state lemma, induction shortcut, assumed output equality, or functional abstraction. Coverage decomposition affects only existential cover-query scheduling/debug visibility, not any assertion proof. The [generator](analysis/two_transaction_v2.py), each harness, prepared JSON and SMT2 retain the exact construction.

## Reachability versus proof

Universal BMC proves the nine assertions for every permitted input/state assignment through the bound. Separate cover jobs are existential executions. Original V2 cover jobs add only read-only observation ports to identical prepared models, reach both goals 70/139, and export complete early trace0 witnesses before timing out on the second export at 600s. These timeouts remain preserved. Final cover decomposition keeps all nine assertions, every functional cell/connection, all initial conditions, ports and wire attributes. It marks debug aliases private and removes only the already-witnessed early cover cell. The final cover remains the original state 139/count predicate. It unrolls every state 0–139 and queries only at 139 (140 states, -t139:140); no state or transition is skipped. The complete final VCD and Yosys witness verify both read observations in one retained-state execution. The saved early trace0 witnesses independently establish the original early cover; the final trace also explicitly audits that state 70 check. Thus neither original reachability obligation is discarded. Instrumentation and the [independent transformation audit](records/final_cover_transformation_audit.json) record the changes. Successful final cover exports pass [the trace auditor](analysis/audit_final_trace.py). The audit reconstructs both 32-bit words and compares them with both ready serial-bank words. It also checks the full control schedule, stable payloads, input-bank loads, initial-load BUSY in those witnesses, retained reset release and correct read counts. Witness output values are derived observations, not independent cipher known answers. No new simulation suite or hardware run was used.

## Preserved failures and checker correction

The initial checker incorrectly included second launch observation103 in a BUSY-low interval, while excluding the first launch34. All four initial BMC jobs reported that phase assertion failing at 103, then timed out exporting full diagnostic traces at 360 seconds. Their counterexample messages, logs and partial traces remain under `formal/pair_00`, `pair_01`, `pair_10`, `pair_11`; they are not relabeled as passes or as merely inconclusive timeouts. Initial cover 00/01 reached both goals, detected the same erroneous assertion in past state 103 and timed out during their second trace export at 300 seconds. See [initial failures](records/initial_failures.json).

Source equations from the unchanged recovered candidate prove that reset released plus START high forces BUSY high combinationally: BUSY=n383|n749, n749=n2635, and n2635=RST_N?(n485|START):n485. Thus state 103 is a launch observation, not a low-BUSY prelaunch observation. [Correction evidence](records/CHECKER_CORRECTION.md) and [exact harness diffs](records/harness_correction_diffs.json) show the only semantic changes: high windows now include34 and 103; the low window ends102. All candidates, protocol controls, state initialization, payload quantification, output equivalence and read/count checks are unchanged. This adds the proper high expectation at both launch observations. Every equivalence check is retained.

The completed certificates report no design counterexample. All four original V2 two-goal cover attempts reached both goals but timed out exporting final traces at 600 seconds; final decomposed cover runs complete with the same 600-second limit and no assertion changes. The two decryption-first V2 attempts timed out at 360 seconds near the final read, without an assertion failure; their incomplete logs remain preserved. Exact-SMT2 retries use the same nine assertions and 141-state bound, omit only the optional per-step presatisfiability query, and allow 600 seconds. Constraint and assertion formulas are unchanged. Separate cover witnesses establish satisfiability and final reachability. Model preparation limit is60 seconds; initial assertion solver limit 360 seconds, retry assertion limit 600 seconds, and separate cover limit 600 seconds. The original two-goal cover limits account for exporting two complete traces. Final cover decomposition uses140 states through139 and changes no assertion bound or assertion property. The cover workers were suspended for about73 seconds to prioritize assertion jobs, then resumed; their 600-second wall limits continued to include suspension time. Signals and UTC times are recorded in [resource controls](records/resource_controls.json). Omitting --presat affects only an extra query, as shown by the [pinned smtbmc source excerpt](records/presat_query_source_excerpt.txt) around lines2028–2047; it does not remove design constraints or assertion checks. Exact timings and arguments are in each result.json and [command record](records/commands/). Two nonexistent-path discovery attempts and a failed inline code-generation parse are summarized honestly in [diagnostics](records/discovery_diagnostic.txt); no statement in that failed Python attempt executed. Their native envelopes are not independently exported.

## Scope and provenance limits

This proves the preserved intentionally repaired model against its preserved mapped netlist, not that the original bitstream already had the repaired readiness behavior, nor cipher correctness. Repaired RTL SHA256 `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`; mapped JSON SHA256 `b9274fdac6870c7b04b67d73ae0206dab97d7f1d9da22793071aef823658e2d7`. [Source/model identities](records/source_identities.json), [tool identities and versions](records/tool_identities.json) and the final output manifest support reproduction. Tools remain the previously pinned local OSS CAD Suite, Yosys0.70+344 (2f2307ad6), Bitwuzla0.9.1; no new tool or challenge material was downloaded.

Unrestricted inputs after reset, unbounded/repeated operations beyond these two transactions, other spacings or mode-change instants, arbitrary SPI behavior, physical timing, package pins, and four-state simulation semantics remain outside this certificate. The earlier unrestricted reset-only timeout remains preserved in [the prior assessment](../reset_transaction_equivalence_2026-11-06/REPORT.md); this task did not rerun or close it. No board programming or attack implementation occurred.

All six originals were reverified against original receipt commit 9913ac31aa47a46de9cfb8f928be21ae4e249ad4, including sizes, SHA256 and Git blob IDs. All 34737 prior artifacts across 16 earlier trees are unchanged; see [preservation audit](records/preservation_audit.json). The user repository was not accessed. Only original materials, this clean chat's preserved derivations and pinned generic local tools were used; no solution comparison or other-chat technical findings were read.

## Reproduction and AI-log boundaries

Run from `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06` with fresh output labels:

```sh
for modes in 00 01 10 11; do
  python3 two_transaction_equivalence_2026-11-07/analysis/two_transaction_v2.py --label reproduce_pair_${modes}_01 --modes "$modes"
  python3 two_transaction_equivalence_2026-11-07/analysis/final_cover.py --label reproduce_cover_${modes}_01 --modes "$modes"
done
for modes in 10 11; do
  python3 two_transaction_equivalence_2026-11-07/analysis/retry_bmc.py --label reproduce_retry_${modes}_01 --modes "$modes"
done
python3 two_transaction_equivalence_2026-11-07/analysis/audit_final_trace.py --prefix reproduce_cover_ --suffix _01 --output trace_reproduction_01.json
```

Each generator rejects existing output directories; the trace auditor rejects an existing output filename. The retry generator deliberately uses the exact preserved V2 SMT2 files. The final-cover generator deliberately uses preserved `cover_MODE_v2/trace_model.json` snapshots (their functional model is the corresponding V2 prepared model plus read-only ports); the newly reproduced assertion jobs are separate regenerated copies of the same harness construction. Recorded original failing jobs remain reproducible with the initial generator under fresh labels. Runtimes are environment-dependent.

[AI_RECORD.md](AI_RECORD.md) is an activity summary, not a transcript. The exact accessible task and accessible progress/final response are saved separately. Solver arguments/timings/outputs/failures are recorded. A complete native envelope export, exact serving-model/build metadata, original native message timestamps/IDs and internal reasoning are unavailable. Some direct setup/search/inline-generation envelopes lack independent raw copies; the incidental diagnostics are explicitly summaries. No missing records or metadata are invented.
