# AI/task and execution record limits

The exact accessible task message is saved in `records/CURRENT_TASK_MESSAGE.txt`, before further compaction. No requesting/source chat, other chat, solution comparison, quarantined prior work, published solution, later target revision or user repository was opened. Only the six original materials, this same clean chat's permitted artifacts and already-pinned generic tools were used. Earlier compacted context/log gaps remain gaps; earlier records were not reconstructed or rewritten.

The system identifies this assistant generically as Codex/GPT-6. Exact serving-model identity, weights, inference parameters, hidden context and native unabridged transcript export are unavailable. No such metadata is fabricated. No subagents, browsing, installation, board programming, supplied MicroPython execution or attack implementation was used.

Available visible responses copied verbatim:

> I’ll strengthen the disabled-read test in a fresh experiment, first confirming that each hold stimulus distinguishes the retained value from a new read. Then I’ll rerun the readiness and differential suites against unchanged candidate copies, preserving the earlier tests and failures.

> The gap is specifically in the earlier RE-disabled case: it kept address 511 after reading address 511, so an erroneous new read would return the same value. The RCLKE-disabled case changed to address 0, whose value differs in all four ROMs, and does detect an always-read control.
>
> The new test will use demonstrably different address/data pairs for every ROM and each disabled-control combination.

> The strengthened test passes all 67,584 checks. For every held address in each ROM, its saved stimulus proves that the proposed new address returns different data.
>
> It also catches all eight synthetic sensitivity controls: ignoring RE or RCLKE in any one of the four ROM forecasts produces the expected failures. The earlier test still misses the ignore-RE control, confirming the coverage gap.

> The readiness and differential reruns reproduce the expected outcomes: the repaired boundary passes 1,122 checks, the baseline retains 14 failures, and all 864 differential comparisons pass. Blocked reads and the earlier negative sampling/counting cases remain distinct.
>
> No candidate hash changed. The preservation audit also confirms that all six originals and 12,472 files across twelve earlier artifact trees are unchanged.

The intended final response is preserved in `records/assistant_final.txt`. These copied visible messages are not represented as a complete native transcript.

Initial setup/source reads and file-authoring tool envelopes were direct tool calls rather than independently exported native envelopes. Their available record is the platform conversation; this folder does not claim full raw-envelope capture. Source files, derived scripts and diffs are implementation artifacts, not raw model responses. Exact accessible task text was preserved without consulting its source chat.

`records/commands/` preserves recorded outer argv, working directory, UTC start/finish, binary-safe stdout/stderr, return codes and output hashes. Candidate run folders retain exact source snapshots, compiler/runtime version output, command timing/argv, full outputs and VCDs using the unchanged copied runner. Strong-ROM runs retain the full generated bench, proof tables, version outputs, compile/simulate argv/cwd/times, complete outputs and waveform. Version subprocess timings inside the strong test were not measured separately; their execution is bounded by the outer record. Python/platform metadata is in `records/environment.json`. No physical timing measurement is implied by simulation or process timestamps.

The earlier ROM test was copied unchanged and reproduced. Synthetic always-read and ignore-RE forecast variants were created only in this new experiment. The former produces four expected failures; the latter incorrectly passes the old test. A separate explicit legacy-sensitivity regression records the resulting expected failure. The new test catches each of eight per-ROM omitted-enable controls with 1,024 forecast failures, preserving every failing output/waveform. Those controls do not change the actual derivative or pinned primitive.

The stronger expected values are derived from baseline INIT bits and pinned mode-1 read semantics. Every chosen changed address is checked to differ in value from the held address. The new no-fault forecast uses expressions extracted from the actual copied candidate. Reference primitive and baseline/derivative source bytes remain unchanged. No stronger test exposed a new real candidate failure in the tested scope. These are simulated component/model invariants, not independent cipher known answers or silicon evidence.

All earlier failures are immutable, and fresh regression runs retain baseline boundary failures, blocked extraction, negative pre-edge sampling and the alternative clock-count interpretation. The unchanged runner records its inner simulator return code in result JSON; blocked extraction can have inner code 0 while the runner exits 5. Matrix and outer command records preserve that distinction rather than counting a blocked read as success.

Candidate/source/copy hashes are in `records/copied_identities.json` and `records/final_copied_identities.json`. The six originals and twelve earlier trees are audited in `records/preservation_audit.json`. No candidate, derivative, baseline, primitive, adapter, old bench, old runner or previous artifact was modified. All new material is in this fresh test folder. The earlier repaired derivative remains intentional, not exact recovery or hardware equivalence; synthesis, resource fit, physical timing, X-state coverage and exhaustive protocol/ROM correctness remain unestablished.
