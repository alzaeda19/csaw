# Original cipher reconstruction — November 12, 2026

The original recovered design implements a **custom 32-bit, four-round substitution and byte-rotation cipher using the AES S-box**. Its effective key handling is a **single hardwired 32-bit XOR mask, reused unchanged in each round**. These findings come from the original Boolean equations, memory initialization and interface, independently checked against the untouched Verilog simulation. They supersede the earlier statement that the cipher and embedded key handling were unidentified.

This is analysis of the original baseline. No modified RTL, Trojan generation, attack optimization, board programming, published challenge solution, shared solution chat or excluded Claude implementation was used. The public AES mathematical standard is the sole algorithm reference, not a challenge solution. Original project files remain unchanged.

## Reconstructed operations

For a 32-bit word `x`, define `SubBytes` as applying the AES byte substitution independently to its four bytes, and `K` as the fixed source-derived 32-bit mask:

```text
F(x) = ROL32(SubBytes(x XOR K), 8)
G(x) = InvSubBytes(ROR32(x, 8)) XOR K
Encryption = F(F(F(F(x))))
Decryption = G(G(G(G(x))))
```

Bytes are numbered least-significant first. One forward round sends `S(x[j] XOR K[j])` to output byte `(j+1) mod 4`. The inverse sends `S^-1(x[(j+1) mod 4]) XOR K[j]` to output byte `j`. `K` is 32 bits total, composed of four fixed 8-bit parts; those parts are not assumed equal. This is not standard AES: it has a 32-bit block, four rounds, byte rotation, no AES MixColumns, and no AES key expansion. Standard AES uses 128-bit blocks; see [NIST FIPS 197](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf), sections 3–5. The S-box was independently calculated using the field inverse and affine equation in sections 4 and 5.1.1.

The mask appears as fixed input-wire inversions before the forward lookup, and the matching fixed inversions after the inverse substitution. Initial and feedback paths use the same per-position mask. The four memories are read-only under the recovered connections. Neither path has a separate runtime key input, a key-loading operation in the supplied normal protocol, or evolving round-key state. Initial data cones take the newly loaded message, not a previous normal transaction. This establishes effective key handling in this recovered design; it does not establish the original author's variable names, how a key was chosen, its entropy, or its security. A numeric bonus-key result is not claimed. The mathematical checker derives the fixed mask internally from the original wires to reproduce the transform; no numeric key artifact is emitted.

## Datapath and timing

The serial bank loads 32 bits, MSB first. On START with chip-select high, two synchronized two-bit counters leave zero. Four datapath updates occur, **including the START edge**, with counter sequence `00 → 01 → 10 → 11 → 00`. The four ROMs implement the forward path. A separate 32-register Boolean path implements the inverse. Both compute concurrently; `ENC_DEC` selects which complete result enters the serial bank (`0` forward, `1` inverse). It does not select round keys or turn the forward ROMs into inverse tables.

BUSY falls after the fourth update. The next rising edge with chip-select high loads the selected result into the serial bank; reading immediately can miss that load. The supplied host waits seven clocks after START, then reads 32 registered output bits. Those seven waiting clocks are not seven cryptographic rounds. The ROM-valid register becomes set after launch; it is distinct from the ROM clock enable.

## Evidence

| Independent check | Result and scope |
|---|---|
| Original source identity | `baseline.v` SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765` |
| S-box normalization | All 256 entries in each of four memories match the mathematically calculated AES S-box after original-wire bit ordering is restored. |
| Static byte cones | 4,096 exact identities: initial/feedback equality and both forward/inverse compositions, four byte positions × 256 values. Source leaf checks establish independent byte cones. |
| Control equations | 9,344 identities over 512 control assignments, plus reachable counter/reset analysis; details in the Trojan chat's audit. |
| Independent Python models | 1,282 distinct words × both modes = 2,564 complete transactions; 20,512 forward/inverse round-state matches, 2,564 serial matches and 2,564 roundtrips, zero mismatches. |
| Untouched original Verilog + original primitive simulator | Same 2,564 transactions; 20,512 round-state comparisons and 12,820 serial/BUSY checks, zero failures. This checks original synchronous ROM semantics as well as output timing. |

The input set includes every byte value in each byte position, walking ones, extremes, the supplied example and 256 seeded random words, deduplicated. The original example `59c359c3 → 9cd84392` and its reverse match. Test counts are labeled explicitly; they are not counts of independent random plaintexts.

The raw physical table hash is `ab40298c12186501c43297c3d81ee4fb8aabbe95246c8cd48bf5c231b07f173f`. After input rotation and output-bit permutation, its hash is `c2d8e5eed6cbebd8625fc18f81486a7733c04f9b0129ffbe974c68b90308b4f2`, identical to the independently calculated AES S-box. The earlier direct-order mismatch was real but inconclusive; bit wiring explains it.

See [structured reconstruction results](analysis/RECONSTRUCTION_RESULTS.json), [original simulator log](verification/icarus_run/1.stdout), [simulator receipt](verification/icarus_run/RUN_RECEIPT.json), [source identities](records/SOURCE_MANIFEST.json), and the [Trojan chat's independent source audit](trojan_review/REPORT.md).

## Reproduce independently

Use Python 3 and the recorded Icarus/VVP toolchain. Choose a new output directory:

```sh
python3 reproduce.py --suite /path/to/oss-cad-suite/bin --output /path/to/new-reconstruction-run
```

This copies the six preserved source inputs and analysis scripts into the new directory, checks the original baseline hash, runs the strict Boolean/ROM interpreter, compares the mathematical cipher at every round, then compiles and simulates the unchanged baseline. It makes no network/model calls and does not run the archived modified-design suite. The suite path is a local dependency, not bundled software. The fresh replay receipt and matching result hashes are retained in `verification/fresh_replay/`.

The interpreter admits only whitelisted one-bit expressions and known original primitive forms. It initializes its private RAM output state to zero; the independent original Verilog simulator starts from the primitive's unknown state and nevertheless matches after the documented reset/launch sequence in all tested transactions. Other tool versions and physical hardware are unverified.

## AI records and remaining limits

The Trojan chat independently traced Boolean cones, fixed inversions, control timing and byte inverses. Codex wrote the mathematical model, independent interpreter and Icarus harness. Two local Qwen reviews supplied advisory feedback; their actual requests, streams, replies and errors/corrections are retained. [Qwen review notes](QWEN_REVIEW_NOTES.md) reject residual incorrect claims about mask size, counter-controlled direction and physical validation. Model agreement is not treated as evidence.

Visible current-chat records have a documented cutoff and exclusions. This update does not recreate missing older generation dialogue. The audit's unavailable peer inputs, if any, are listed separately from historical generation gaps. Tools, outputs and any execution errors are recorded; hidden reasoning and platform instructions are excluded.

The round equations and effective fixed-mask handling are established for the recovered digital design under the documented protocol. The byte identities give exact local algebraic checks; the end-to-end simulator run is finite. This is not a new whole-system formal proof for malformed frames, arbitrary asynchronous timing or physical silicon. It does not establish cryptographic strength, stealth of the modified submission, negligible overhead, complete historical generation automation, or instructor acceptance. Those separate submission gaps remain explicit in the repository's current guide.

The cipher-analysis audit preserves 93 visible records with exact-value checks and discloses three unreadable peer instruction exchanges plus two unreadable progress messages. These are new documentation-analysis gaps, separate from the historical twelve reviewer instructions and the earlier pin-audit gaps. Both current peer final responses are preserved. Current Qwen prompts and received replies are complete; record cutoffs do not pretend to include future publication messages.
