# Reconstructed baseline phases and fixed-key handling

November 12, 2026, America/New_York. Original recovered baseline only; no published solution, modified wrapper, repository edit or hardware operation.

The recovered core implements **four iterations of a custom 32-bit substitution-and-byte-rotation transform**, with a parallel inverse datapath. The substitution is the AES S-box after correcting the bit order at the memory boundary. This is **not the standard AES block cipher**. The effective key handling is a repeated, fixed 32-bit XOR mask embedded in logic inversions; there is no separate runtime key-loading transaction or round-key schedule in the reconstructed normal operation. No numeric mask/key value is emitted.

## Exact normal-operation transform

Number bytes from least significant to most significant. Let `K[j]` denote the symbolic fixed inversion mask associated with byte slot `j`, and `S` the normalized substitution. One forward update and its inverse are:

```text
F(x) = ROL32(SubBytes(x XOR K), 8)
G(x) = InvSubBytes(ROR32(x, 8)) XOR K

F(x)[(j+1) mod 4] = S(x[j] XOR K[j])
G(x)[j] = inverse_S(x[(j+1) mod 4]) XOR K[j]

Encrypt(x) = F(F(F(F(x))))
Decrypt(x) = G(G(G(G(x))))
```

The static source-cone checks establish all of the following:

- The four forward memories use identical effective 256-entry byte tables. The original table digest is `ab40298c12186501c43297c3d81ee4fb8aabbe95246c8cd48bf5c231b07f173f`.
- Effective memory input bits correspond to algorithm-byte bits `[1,2,3,4,5,6,7,0]`; logical output bits read effective table bits `[0,4,2,6,1,5,3,7]`. These are coordinate/packing permutations, separate from the fixed per-slot inversions.
- Removing those bit-order differences gives normalized substitution SHA-256 `c2d8e5eed6cbebd8625fc18f81486a7733c04f9b0129ffbe974c68b90308b4f2`. The coordinator independently calculated the public AES S-box mathematically and compared all 256 entries; its saved receipt is copied in `source_records/SBOX_NORMALIZATION.json`. This audit independently obtained the same normalized digest; it did not run the coordinator's AES-reference code.
- Forward initial-load and feedback mappings are identical byte functions, with the same per-slot fixed inversions. There is no round-number-dependent key selection in those functions.
- The 32 working flip-flops implement four inverse byte functions. Initial and feedback maps agree. Both compositions `G_j(F_j(v))=v` and `F_j(G_j(v))=v` hold for every byte value in every slot.
- There are **4,096 exhaustive byte identities**: four relations, 256 inputs, four slots. Eight additional bijection properties also pass. This count is not thousands of independent cryptographic test vectors.
- The reconstructed four-round word functions reproduce the sole original supplied encryption/decryption pair in both directions. That remains one independent value oracle.

The exact per-net maps are in `DATAPATH_COFACTORS.json`; byte proofs are in `BYTE_INVERSE_CHECKS.json`; the original-host comparison and storage-role checks are in `KEY_HANDLING_CHECKS.json`. Fixed mask values, expanded round keys and secret-key output files are absent.

## Why there are four processing updates

Define `R=RST_N`, `S=START`, `A=(n842,n840)` and `B=(n844,n846)`, with each pair written high bit first. The source's enable/reset/D logic reduces to:

```text
n840' = R & ~n840 & (S | n842)
n842' = R & (n842 XOR n840)
n846' = R & ~n846 & (S | n844)
n844' = R & (n844 XOR n846)

RAM_RCLKE = n749 = R & (S | n840 | n842)
BUSY = R & (S | n840 | n842 | n844 | n846)
n588' = R & (n588 | S | n840 | n842)
n972' = BUSY
serial_bank_enable = n1 = ~CS_N | ~R | (n972 & ~BUSY)
```

The two counters initialize/reset together and remain equal. A normal launch follows:

| Rising edge | Counter state after edge | Processing effect | Readout effect |
|---|---|---|---|
| Before launch | 00 | Current 32-bit input resides in serial bank | No result copy |
| Launch, edge 1 | 01 | First forward and inverse update from serial input | BUSY high |
| Edge 2 | 10 | Second update from each path's own feedback | BUSY high |
| Edge 3 | 11 | Third update | BUSY high |
| Edge 4 | 00 | Fourth update | BUSY falls; delayed BUSY remains high |
| Edge 5, CS high | 00 | Both processing paths hold | Selected result copies into serial bank |

`n588` is a sticky qualifier on all 32 connected ROM-output bits. It is not the memory clock enable. It clears on reset, sets on the first launch, and subsequently holds until reset. All 32 initial ROM-address cofactors are independent of its previous value. Consequently the first operation after reset does not consume unknown old ROM read results through the initial-data selection.

ENC_DEC is a readout selector: mode 0 selects the completed forward ROM path and mode 1 the completed inverse register path. Both processing paths run during a normal operation. The 32 cofactored serial-bank D inputs reduce to direct output wires in each mode. This is stronger than merely observing a mode input; it does not claim arbitrary mid-transaction mode changes conform to the specified protocol.

Independent source-expression verification in `control_peer/` passed **9,344 identities across 512 control combinations**. Its report supplies exact reset, enable, data and counter source lines, plus the complete truth table. START does not restart an already active counter sequence. A continuously asserted START can keep BUSY active and launch another sequence; the normal schedule pulses START once.

## What has been established about key handling

All 71 explicit registers are accounted for: 32 serial input/result bits, 32 inverse-path data bits, four phase bits, the ROM-output qualifier, delayed BUSY and registered MISO. The RAM read pipelines are transient data; the four lookup memories have constant-low WCLK and WCLKE. Their separate WE input is high, which does not enable writing while clock and clock enable remain low.

The fixed byte inversions are present at both initial and feedback inputs. Under a valid launch from idle, the first forward step depends only on the current serial input; the inverse cones likewise use only current serial bytes. Previous well-formed transactions therefore do not act as a separate runtime key-loading phase. The original host contains no key input transaction. The normal-operation reconstruction has a fixed effective `K`, not a key register supplied through the documented interface.

This identifies effective key handling, not the author's original variable names, intended key provenance or source-code representation. Deliberately malformed or interrupted schedules are not being reclassified as a specified key-loading mechanism. The numeric mask remains undisclosed.

Each round rotates whole bytes and applies independent byte bijections. After four rotations, positions are restored. Thus each final byte depends on its corresponding input byte and fixed masks, with no cross-byte mixing in this reconstructed transform. This is a structural consequence, not a claim about cryptographic strength.

## Evidence and limits

- Baseline SHA-256: `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`.
- The previous static inventory was checked against freshly parsed source register records: all 71 definitions and all 32 serial-chain links agree. Scripts re-read and verify the baseline hash before analysis.
- The RAM decoder uses the same READ_MODE=1 semantics as the preserved official primitive-model analysis. The byte identities do not independently validate silicon or tool translation.
- This folder contains static Boolean analysis and a reconstructed word-function check. No HDL simulator, synthesis, placement, timing analysis or hardware was run here. The coordinator owns its separate strict-interpreter and Icarus comparisons; those runs are not counted as this audit's executions.
- Every final local analysis script returned exit 0; exact commands, Python/platform versions and output files are in `EXECUTION_RECEIPT.json`. Failed or superseded attempts, if any, remain in the bounded AI record projection. No published solution or excluded implementation was used.
- These findings refine the earlier architectural proposal. The earlier effective-order table comparison was insufficient to identify the substitution because it omitted the proven bit-order normalization. That limitation is resolved without importing a challenge solution.

## Reproduction outside a Git checkout

Use Python 3 and copy this audit folder to a writable directory outside any repository. Set these optional environment variables to the corresponding unchanged submission files:

```text
CSAW_BASELINE_SOURCE = path to submission/rtl/baseline.v
CSAW_STATIC_INVENTORY = path to submission/addenda/2026-11-12/explanation/STATIC_BASELINE_ANALYSIS.json
CSAW_ORIGINAL_HOST_SOURCE = path to submission/evidence/original_materials/qualifier/spi_ice40_crypto_ip_test.py
```

Then run `python3 check_key_handling_structure.py` in the copied audit folder. It includes the datapath and byte-inverse checks and writes new outputs beside the copied scripts. No third-party Python packages are required. The independently preserved control script has its source paths documented in `control_peer/COMMANDS.md`; its saved results are not silently rerun by this command. Default paths target the original Mac workspace and must be overridden on another machine.

The visible-record export is a scoped field projection with exact-value checks, source line hashes and explicit cutoffs. Encrypted ordinary peer instructions are counted separately from intentional omissions of internal reasoning/platform data, and separately from older generation-log gaps. This audit used Codex and its peer; Qwen calls belong to the coordinating chat's independently retained workflow.
