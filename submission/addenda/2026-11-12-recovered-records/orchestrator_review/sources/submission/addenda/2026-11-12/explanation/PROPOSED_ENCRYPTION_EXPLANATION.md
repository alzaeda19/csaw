# Proposed explanation of the original encryption system

This explanation concerns only the unchanged, original-derived `rtl/baseline.v`, SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`. The evidence supports a **multi-cycle, table-assisted 32-bit transform with a shared serial load/readout bank and a separate working bank**. That is an architectural interpretation, not identification of a standard cipher. The [source index](SOURCE_INDEX.md) gives readable references; [EVIDENCE_MAP.json](EVIDENCE_MAP.json) pins every claim to source hashes and lines. Fresh work was static inspection; all simulation and formal results cited here are historical. [E01]

## Interface and data movement

**Specification.** The original interface describes 32-bit encryption (`ENC_DEC=0`) and decryption (`ENC_DEC=1`), synchronous active-low reset, and one SCK domain shared by serial transfer and computation, at no more than 1 MHz. The normal sequence is reset, 32 input clocks with `NORM_CS_N=0`, chip-select high, a START pulse, processing clocks, then 32 output clocks. The original host sends bytes and bits most-significant first. [E02]

**Static observation.** The functional adapter maps SCK to `io_9_31_1`, MOSI to `io_16_31_0`, MISO to `io_16_31_1`, chip-select to `io_17_31_0`, reset to `io_13_31_1`, START to `io_18_31_1`, and mode to `io_19_31_1`. This is a functional mapping, not verified package-pin wiring. The two status outputs are directly equal. [E03]

With chip-select low, Boolean substitution in all 32 serial-register input equations gives one unbroken shift chain: `MOSI → n628 → n390 → … → n917 → n800`. MISO is a further rising-edge register that captures the **previous** `n800`. Consequently, a post-edge sample receives the outgoing bit while the bank shifts in the next MOSI bit. Extraction also overwrites this same bank with incoming bits. Chip-select high selects parallel-result inputs instead; it does not create a separate clock edge or independently clock a latch. The complete chain and each supporting assignment are retained in the [static inventory](STATIC_BASELINE_ANALYSIS.json). [E04]

## Datapath, storage and control

The recovered source contains **1,404 LUT-tagged Boolean assignments, four `SB_RAM40_4K` instances, and 71 explicit rising-SCK registers**. The register structure is:

| Registers | Observable role |
|---|---|
| 32 enabled by `n1` | Serial input/readout bank, with serial or parallel data selection |
| 32 of the 34 enabled by `n3` | Working datapath bank |
| Four: `n840`, `n842`, `n844`, `n846` | Two two-bit counter structures feeding processing controls |
| `n588` | Qualifies the 32 connected memory-output bits through AND-like LUT terms |
| `n972` | Delayed BUSY sample |
| `io_16_31_1` | Registered MISO |

These are counts in the recovered representation, not a fresh synthesis utilization estimate. The memory primitives have additional internal read state in the historical behavioral model. [E05]

Each memory has `READ_MODE=1`, eight nonconstant address connections and eight connected output bits. All four share SCK as read clock, constant-high read enable, and read-clock enable `n749`. Their write clock and write-clock enable resolve to zero, with constant write addresses/data; they therefore act as **fixed initialized lookup storage during normal operation**, rather than writable message buffers. Their initialization payloads were excluded from this analysis, so no table values, key contents or substitution identities are claimed. [E06]

The direction input directly enters 32 LUT equations, including selections such as `n1779 = ENC_DEC ? !n642 : !n793`. This places mode selection inside the datapath. The working bank, lookup outputs and serial bank connect through the intervening Boolean network; the observed structure supports a table-assisted transform. It does **not** establish a particular substitution/permutation network, Feistel structure, round count, key schedule or named algorithm. Four processing clocks must not be relabeled four cipher rounds. Keep the mode stable through an operation, as in the recorded driver. [E07]

## Completion and readout boundary

Static simplification gives the BUSY and `n1` identities below. Those two combinational identities, plus the `n3` identity in the receipt, passed 768 checks across all 256 combinations of eight Boolean inputs. The delayed-BUSY behavior follows directly from its register assignment:

- `BUSY = RST_N && (START || n840 || n842 || n844 || n846)`.
- `n1 = !NORM_CS_N || !RST_N || (n972 && !BUSY)`.
- `n972` captures BUSY on each rising SCK edge when reset is inactive.

Thus BUSY includes a combinational START path; it is not itself an independently registered output. With reset released and chip-select high, the serial bank loads only when delayed BUSY is high and present BUSY is low. If BUSY falls following a rising edge, that condition enables the bank for the **next** rising edge. Keeping chip-select high for that edge selects the parallel result. Starting extraction immediately instead selects serial shifting and misses that load. [E08]

**Historical tested evidence.** The recovery diagnostic observed BUSY fall three additional clocks after launch—four clocks including launch. The supplied host actually issues **seven additional clocks**, despite shorter-cycle comments. Later paired simulations recorded 24/24 supplied known-answer checks per model under that host schedule, but **8/8 immediate-first-BUSY-low reads failed**, returning the input. These outcomes support the distinction between processing status and result availability. Post-edge digital sampling was required in the recovery diagnostic; this is not a measured physical SPI setup/hold guarantee. [E09]

## What the evidence establishes

The independent value oracle remains the supplied pair: `59C359C3 → 9CD84392` in encryption mode and the reverse in decryption mode. Later records report 352 transactions/model and 104,468 compared checkpoints, including consecutive mode changes and clock pauses. Arbitrary-word agreement between two representations is not an independent expected-answer oracle. [E10]

Historical proofs compare this baseline with RTL decoded from a regenerated binary: 135 next-state bits and three outputs under an explicit state relation, plus each mode's complete prescribed host transaction for every stable 32-bit payload. They preserve the baseline's readiness failure. They do not independently prove the cipher, universal encrypt/decrypt inversion, physical silicon behavior, or a new original-binary recovery theorem. [E11]

This is a concrete proposed explanation of the encryption system at the interface, storage, control and datapath level. Algorithm identity, table semantics, key handling and cryptographic strength remain unknown; no key recovery was attempted. Those limits delimit this proposal rather than imply that an exhaustive cipher proof was produced or required. [E12]
