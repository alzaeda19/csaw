# Baseline control-equation analysis

Source: `/Users/al-zayedal-hassan/Documents/Codex/2026-11-10/referenced-chatgpt-conversation-this-is-an/work/csaw-github/fresh-clone/submission/rtl/baseline.v`

SHA256: `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765` (verified before and after analysis).

Method: static Boolean simplification, exhaustive local truth tables, and tabulation of proven one-edge transition equations. No RTL edits, HDL execution, synthesis, hardware access, ROM-content extraction or cipher/key interpretation. The earlier allowed static inventory was used to identify the control cones; every reported equation was checked against the unchanged baseline source itself. The parser excludes every `.INIT_` line.

## Names and exact register identities

All six registers below update on the rising edge of `io_9_31_1`. Define `R = io_13_31_1` (reset released), `S = io_18_31_1` (START), `C = io_17_31_0` (CS_N), `A = (n842,n840)`, `B = (n844,n846)` with high bit first, `Q = n588`, and `D = n972`. Every right-hand side uses the pre-edge state.

| Register | Initial value, source line | Enable | Reset condition | D expression | FF source line |
|---|---:|---|---|---|---:|
| `n840` (A low) | 0, 27112 | `n681` | `n2` | `!n840` (43960) | 45364 |
| `n842` (A high) | 0, 27142 | `n681` | `n680` | `n840 XOR n842` (43773) | 45176 |
| `n846` (B low) | 0, 27242 | `n3` | `n2` | `!n846` (43490) | 44893 |
| `n844` (B high) | 0, 27213 | `n3` | `n845` | `n844 XOR n846` (43883) | 45287 |
| `n588` (Q) | 0, 17236 | `n681` | `n2` | 1 (43276, 44787, 43384) | 44679 |
| `n972` (D) | 0, 30111 | always | `n2` | BUSY (43764) | 45167 |

All resets in this table are synchronous, within the enabled rising-edge block, and clear the register to zero.

Define `a = n840 | n842` and `b = n844 | n846`. The enable/reset identities are:

```
n2   = ~R
n681 = ~R | S | a
n3   = ~R | S | b
n680 = ~R | (S & ~a)
n845 = ~R | (S & ~b)
```

Sources: `n2` 44301/45705; `n681` 43022/44425; `n3` 43626/45029; `n680` 44283/45687 with `n485 = R&a` at 43410/44813; `n845` 44237/45641 with `n383 = R&b` at 43923/45327.

## Four total next-state equations

Including hold, enable, and reset behavior, the four source equations reduce to:

```
n840' = R & ~n840 & (S | n842)
n842' = R & (n842 XOR n840)
n846' = R & ~n846 & (S | n844)
n844' = R & (n844 XOR n846)
```

For either pair `(h,l)`, `h'=R&(h XOR l)` and `l'=R&~l&(S|h)`. The special high-bit start/reset term causes no extra transition under released reset: it only clears an already-zero XOR when the pair is idle.

| R | Current pair | Next with S=0 | Next with S=1 |
|---:|---|---|---|
| 0 | any | 00 | 00 |
| 1 | 00 | 00 | 01 |
| 1 | 01 | 10 | 10 |
| 1 | 10 | 11 | 11 |
| 1 | 11 | 00 | 00 |

Consequences proved by the equations:

- Both pairs initialize to `00` and have identical transition functions; `A=B` is therefore an invariant for every sampled R/S sequence from initialization or a reset edge.
- START is a sampled level, not an edge detector. A high START sampled in idle launches a four-edge sequence. START during an active phase does not restart it. START held high causes another sequence to begin on the next edge after returning to `00`.
- R low forces both pairs to `00` on the next rising edge regardless of START or CS. CS does not enter either counter's transition function.

## RAM clock enable, qualifier, BUSY and result loading

```
n749 = R & (S | a)                       // actual RAM read clock enable
BUSY = R & (S | a | b)
n970 = ~BUSY
Q'   = R & (Q | S | a)
D'   = BUSY
n1   = ~C | ~R | (D & ~BUSY)             // serial/result bank enable
```

`BUSY` is `io_8_31_1`, mirrored to `io_19_31_0` at line 30051. Its combinational assignment is 43123/44526. `n749` is 44093/45497. `n970` is 42938/44341. `n1` is 43089/44492. The four RAMs use `n749` as `.RCLKE` at 42795, 42829, 42863, and 42897 and the same rising-edge clock at the next line of each pair. On reachable states (`A=B`), `n749=BUSY` exactly.

`n588` is a sticky memory-output qualifier, **not** the RAM clock enable. It clears on a reset edge, becomes one on the first enabled A-counter edge, and holds one thereafter until reset. Its 32 direct combinational consumers are exactly gates of the form `n588 & RAM_output_bit`; all 32 local truth tables were checked. The gate list with source lines is in `CONTROL_FINDINGS.json:qualification_gates`. The first operation after reset begins with Q=0; later operations may begin with Q=1.

`n972` unconditionally samples pre-edge BUSY (with synchronous reset). R low immediately makes the combinational BUSY output zero; D clears on the next clock. `n1` enables serial shifting when C=0, reset clearing when R=0, or one parallel-result load when C=1 and delayed BUSY is one while current BUSY is zero.

## Normal one-launch phase schedule

Assume reset released, one launch edge with S=1, S=0 afterwards, and C=1 through the result-load edge. The values in the enable columns are sampled **before** the indicated edge. The launch row assumes the first operation after reset; Q may already be one for later operations.

| Edge | A=B before | S | `n3` | RAM `n749` | `n1` | A=B after | Q after | D after | BUSY after, S lowered |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| Launch 1 | 00 | 1 | 1 | 1 | 0 | 01 | 1 | 1 | 1 |
| Run 2 | 01 | 0 | 1 | 1 | 0 | 10 | 1 | 1 | 1 |
| Run 3 | 10 | 0 | 1 | 1 | 0 | 11 | 1 | 1 | 1 |
| Completion 4 | 11 | 0 | 1 | 1 | 0 | 00 | 1 | 1 | 0 |
| Result load 5 | 00 | 0 | 0 | 0 | 1 | 00 | 1 | 0 | 0 |
| Settled idle 6 | 00 | 0 | 0 | 0 | 0 | 00 | 1 | 0 | 0 |

BUSY is already high before the launch edge because START enters its combinational equation. After completion edge 4, BUSY falls and `n1` rises while D remains one. The bank's parallel loading therefore occurs on the **following** clock, edge 5, with CS high. That edge also clears D and removes the enable pulse. Beginning a CS-low read before that edge selects shifting instead of the parallel result load. This table describes control timing; it does not infer the datapath result or cipher identity.

The working-bank enable `n3` and RAM enable `n749` are active for the same four sampled edges in this normal schedule. The four control bits establish two copies of a four-phase sequence; they do not alone establish a cipher round count.

## Verification and artifacts

`analyze_control.py` exhaustively evaluates the original control-source expressions for all 512 assignments of the four phase bits, Q, D, R, S, and C. It checks 9,216 control and next-state identities plus 128 qualifier-gate identities: **9,344 passed**. This includes unequal A/B states for the raw identities; the reachable-state equality is proved inductively rather than assumed by the exhaustive checks.

- `CONTROL_FINDINGS.json`: machine-readable equations, phase table, source references and qualifier gates.
- `CONTROL_TRUTH_TABLE.json`: all 512 input assignments and original-expression output/next-state results.
- `CONTROL_SOURCE_EXCERPTS.txt`: control-only baseline source excerpts with original line numbers.
- `analyze_control.py`: reproducible static-analysis code.
- `EXECUTION_LOG.json`, `run.stdout.txt`, `run.stderr.txt`: exact analysis command, return code and outputs. The stderr file is empty and the return code is zero.
- `COMMANDS.md`: preliminary read-only command record and analysis scope.
- `HASHES.sha256`: hashes of final analysis artifacts; `source_identity.json` and `INPUT_IDENTITIES.json` record source hashes.

Every artifact is confined to this `control_peer` directory. No baseline or repository file was changed.
