# Reset-to-transaction equivalence

The repaired RTL and its synthesized netlist pass bounded equivalence through one complete transaction in both modes, for every stable 32-bit payload, under the schedule below. Initial RAM read states remain independent. This is a protocol-constrained result; unrestricted equivalence after reset remains unproved.

| Check | Result | Evidence |
|---|---|---|
| Encryption, arbitrary 32-bit payload | PASS, 72 solver states | [proof](formal/transaction_encrypt/bmc.stdout) |
| Decryption, arbitrary 32-bit payload | PASS, 72 solver states | [proof](formal/transaction_decrypt/bmc.stdout) |
| Final-read reachability, encryption/decryption | PASS, cover at state 70; complete traces audited | [audit](records/trace_audit.json), [encryption](formal/compact_cover_encrypt/), [decryption](formal/compact_cover_decrypt/) |
| Unrestricted inputs following initial reset | TIMEOUT, 180 seconds; no completed proof | [log](formal/unrestricted72/bmc.stdout), [result](formal/unrestricted72/result.json) |
| Initial full diagnostic cover exports | Reached state 70, then each timed out exporting at 120 seconds; partial traces retained | [encryption](formal/cover_encrypt/), [decryption](formal/cover_decrypt/) |

## Schedule and sampling

State 0 precedes the first modeled SCK edge. Each transition represents one positive SCK edge. Controls are combinational functions of the current cycle counter.

| Edge/current cycle | Controls and operation | Resulting observation |
|---|---|---|
| 0 | RST_N=0, CS high, START=0 | Synchronous reset |
| 1 | Reset released, idle | Idle |
| 2–33 | CS low; MSB-first symbolic payload | All 32 input bits loaded at state 34 |
| 34 | CS high, START=1 | Launch L0 |
| 35–37 | CS high, START=0 | Three additional compute edges; completion L3 |
| 38–69 | CS low, 32 read clocks | MISO read observations at states 39–70 |
| State 70 | No further DUT edge needed | Final word compared after the final read edge |

There are 70 DUT edges through the final read. The 72-state solver bound checks states 0–71; state 71 is beyond the transaction and is not counted as transaction evidence. Primary-output equality is asserted at states 1–70, excluding the pre-reset state. BUSY is asserted high at states 35–37 and low at states 38–70. Three output equalities, two BUSY phase assertions, a sample-count assertion, and final-word equality give seven assertions.

The observer captures 31 prior read bits at cycles 39–69 and combines them with current MISO at state 70. None of its initial zero bits survives this final 32-bit word. The cycle counter, sample counter, and observer registers have explicit checker initialization. These do not initialize DUT RAM state. The clock is an abstract formal step, not a frequency or physical timing model.

## Exact proof restrictions

Each proof fixes mode throughout the transaction (0 encryption, 1 decryption), one reset edge, one idle edge, exactly 32 load edges, one launch, three further processing edges, and exactly 32 read edges. CS and START follow the table. MOSI is the symbolic payload during loading and repeats that payload during reads, matching the original host's dummy transfer style; elsewhere it is zero. The payload is one arbitrary stable 32-bit anyconst, universally quantified by the assertion check. These generated controls constrain the problem even though there are zero assumption cells.

The full uncoupled models from this chat's earlier synthesis verification are copied into [models](models/). Fixed ROM contents derive from the original bitstream recovery. Each side retains 64 unspecified RAM read-state bits, 128 total, with disjoint state identities and no defined initialization on any alias. No pairing, zeroing, output-equality assumption, shared-state lemma, or functional blackbox was used. All functional primitive logic is expanded; preparation flattens and lowers formal properties without a functional cut. See [independence audit](records/model_independence_audit.json), [generator](analysis/transaction.py), and each prepared JSON and SMT2 model.

The compared candidate is the intentionally repaired model from this chat, not an assertion that the original bitstream had the repaired behavior. Repaired RTL SHA256: `bed2bda6d9521812555e5242571f7fb0c338a9cc6d3676b2459794767ce0bd04`. Synthesized mapped JSON SHA256: `b9274fdac6870c7b04b67d73ae0206dab97d7f1d9da22793071aef823658e2d7`. [Source identities](records/source_identities.json) records copies and origins. Tools are the previously pinned generic OSS CAD Suite (Yosys 0.70+344, Bitwuzla 0.9.1); no new tool download was needed.

## Reachability and limitations

Separate existential cover checks reach the actual final-read observation. Initial full-wire dumps timed out after reaching that goal. Compact covers expose only read-only observation ports on the same prepared models; their instrumentation checks verify unchanged cells, state initialization, properties, and existing ports. Complete compact VCD and Yosys witness files are retained. The [trace auditor](analysis/audit_trace.py) checks the control schedule, loaded serial banks, processing BUSY interval, all 32 read observations, and reconstructed final words. Both witnesses use payload zero, with observed outputs 08abd043 and c42c8e6a respectively. These are derived witness observations, not independent cipher known answers. Their existential payload does not restrict the separate universal assertion proofs.

The broader retry uses the earlier independent-state reset-only model unchanged: initial reset/idle, then unrestricted controls. It timed out while checking step 22. Progress messages are not a completed bound certificate. The earlier Z3 timeout is preserved in the prior artifact tree. No design counterexample was produced by these timeout runs.

This establishes one bounded transaction under the recorded protocol. It does not establish unrestricted or unbounded equivalence, repeated transactions, arbitrary mode/control changes, four-state simulation equivalence, cipher correctness, board pin mapping, or physical timing. No new board or MicroPython execution occurred. No additional simulation was run for this task.

## Preservation and reproduction

All six original receipt files and 34625 prior artifacts across 15 earlier trees are unchanged, including earlier failures. The user repository was not accessed. No other chat, solution comparison, later challenge revision, or published solution was consulted. See [preservation audit](records/preservation_audit.json), [task message](records/CURRENT_TASK_MESSAGE.txt), [AI record](AI_RECORD.md), and [command records](records/commands/).

From `/Users/al-zayedal-hassan/Documents/CSAW_2026_Restart_2026-11-06`, use fresh labels:

```sh
python3 reset_transaction_equivalence_2026-11-06/analysis/transaction.py --label reproduce_encrypt_01 --mode 0
python3 reset_transaction_equivalence_2026-11-06/analysis/transaction.py --label reproduce_decrypt_01 --mode 1
python3 reset_transaction_equivalence_2026-11-06/analysis/compact_cover.py reproduce_cover_encrypt_01 0
python3 reset_transaction_equivalence_2026-11-06/analysis/compact_cover.py reproduce_cover_decrypt_01 1
python3 reset_transaction_equivalence_2026-11-06/analysis/unrestricted.py reproduce_unrestricted_01
```

Compact covers deliberately reference the preserved `transaction_encrypt`/`transaction_decrypt` prepared models. The trace auditor references the recorded compact witnesses. All generators reject existing output labels. Runtime limits and exact arguments are retained in each result/command record. The unrestricted retry has no guaranteed completion.
