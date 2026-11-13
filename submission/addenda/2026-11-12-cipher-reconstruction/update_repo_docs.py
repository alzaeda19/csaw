"""Update current reader-facing documents; preserve the earlier versions."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]/'work/csaw-github/fresh-clone'
LINK='addenda/2026-11-12-cipher-reconstruction'
files=['README.md','SUBMISSION_GAPS.md','submission/CURRENT_GUIDE.md','submission/ENCRYPTION_EXPLANATION.md','submission/PUBLICATION_STATUS.md','submission/PUBLICATION_REVIEW.md']
for name in files:
    dest=ROOT/'previous_docs'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(REPO/name,dest)

explanation='''# How the original cipher works

The original recovered design is a **custom 32-bit cipher with four rounds**, using the AES byte-substitution table. Each encryption round XORs the word with one fixed 32-bit mask, substitutes each of its four bytes, then rotates the word left by one byte. Decryption reverses those operations. The same mask is reused in every round.

This is now an original-source reconstruction, beyond the earlier architectural proposal. It comes from the recovered RTL, original memory contents and documented host interface. It was checked independently against the unchanged original Verilog. No published challenge solution, shared solution chat, excluded Claude implementation or separate professor-supplied AES design supplied the algorithm.

## Exact operations

```text
F(x) = ROL32(SubBytes_AES(x XOR K), 8)
G(x) = InvSubBytes_AES(ROR32(x, 8)) XOR K
Encrypt(x) = F(F(F(F(x))))
Decrypt(x) = G(G(G(G(x))))
```

`SubBytes_AES` applies the AES S-box to each byte independently; `InvSubBytes_AES` applies its inverse. `K` is one 32-bit fixed mask, made of four fixed 8-bit parts. Bytes are numbered least-significant first. Forward output byte `(j+1) mod 4` is `S(input[j] XOR K[j])`; inverse output byte `j` is `S^-1(input[(j+1) mod 4]) XOR K[j]`.

Using an AES component does **not** make this standard AES. Standard AES has 128-bit blocks and its own round structure and key expansion. This design has 32-bit blocks, four rounds, byte rotation, no AES MixColumns and no AES key expansion. The byte table was independently calculated from the mathematics in [NIST FIPS 197, sections 4 and 5.1.1](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf), then compared with all original table entries after tracing the bit wiring.

## Key handling

The fixed XOR operation appears as hardwired inversions on selected data wires. Initial and feedback paths contain the same per-byte inversions, so the effective mask stays constant across all four rounds. The inverse path applies the matching mask after inverse substitution. The four memories have disabled write clocks and write-clock enables.

There is no evolving round-key state, separate runtime key port, or key-loading step in the supplied normal protocol. The initial round depends on the newly loaded message, not a previous normal transaction. These source dependencies establish fixed-mask handling rather than merely relying on the absence of a port named “key.”

This does not establish the original author's variable names, how the constant was selected, its entropy or security. The reproduction script derives the mask internally from the original wires; no numeric bonus-key result or key-exfiltration mechanism is supplied.

## Data path and clocks

```mermaid
flowchart LR
    I[32-bit serial input bank] --> F[Forward path: four ROM byte substitutions]
    I --> D[Inverse path: Boolean logic and 32 working registers]
    F -->|Four rounds| M[Select completed result with ENC_DEC]
    D -->|Four rounds| M
    M --> O[Parallel load into shared serial bank]
    O --> R[32 registered serial output bits]
```

1. Chip-select low shifts in 32 bits, most-significant first.
2. START with chip-select high performs the first round. Three more rising edges complete rounds two through four. The two synchronized counters follow `00 → 01 → 10 → 11 → 00`.
3. Forward and inverse paths compute concurrently. `ENC_DEC=0` selects the forward result; `ENC_DEC=1` selects the inverse. The selection acts at the parallel result load, not as a round-key or counter selector. The normal driver keeps it stable.
4. BUSY falls after round four. A **further rising edge with chip-select still high** copies the selected result into the serial bank. Reading immediately can miss this load and return old input.
5. The host waits seven clocks after START, then shifts out 32 bits. Seven wait clocks are not seven cipher rounds.

## What was verified

| Check | Result |
|---|---|
| Original ROMs against mathematical AES S-box after wiring normalization | All 256 entries in each of four memories match. |
| Exact source-derived byte identities | 4,096 checks confirm initial/feedback equality and both directions of inversion for every byte value in every slot. |
| Original control equations | 9,344 identities over 512 assignments, with documented reset and reachable-state assumptions. |
| Independent mathematical model against original Boolean/ROM interpreter | 2,564 complete transactions across 1,282 distinct words; 20,512 round-state matches and zero mismatches. |
| Untouched original Verilog and primitive simulation | Same 2,564 transactions; 20,512 round-state comparisons and 12,820 serial/BUSY checks; zero failures. |

Inputs include every byte value in each position, walking ones, extremes, the supplied pair and seeded random words. Both encryption and decryption are tested. The original example `59c359c3 → 9cd84392` and its reverse match. The raw table originally failed a direct AES comparison because its address and output bits are reordered; normalization resolves that earlier uncertainty.

Read the [reconstruction report](addenda/2026-11-12-cipher-reconstruction/README.md), [structured results](addenda/2026-11-12-cipher-reconstruction/analysis/RECONSTRUCTION_RESULTS.json), [original simulator log](addenda/2026-11-12-cipher-reconstruction/verification/icarus_run/1.stdout), and [independent Trojan-chat source audit](addenda/2026-11-12-cipher-reconstruction/trojan_review/REPORT.md). Reproduction instructions and all current Qwen prompts, replies and corrections are included there.

## Limits that remain

The operations, round count, bit/byte ordering and effective fixed-mask handling are now established for the recovered digital design under the documented protocol. The author's original algorithm name, design rationale and cryptographic strength are not established. The exact byte checks support local algebraic conclusions; the full simulator run is finite and is not a new whole-system formal proof covering arbitrary malformed frames, asynchronous behavior or hardware timing.

The [reference-board pin audit](addenda/2026-11-12-qwen-verification/pin_audit/REPORT.md) separately establishes the published board's pin map, including the physical BUSY/LED label distinction. No particular board was tested and the earlier automatically pinned bitstream is not newly validated for that board.

This closes the earlier cipher-operation/key-handling explanation gap. It does not close the separate gaps in historical AI logs, stealth, physical overhead, generation automation or instructor acceptance. Original RTL, testbenches and sealed evidence remain unchanged. Earlier addenda and the original brief are preserved as historical records; this document supersedes their statements that the cipher was still unidentified.
'''
(REPO/'submission/ENCRYPTION_EXPLANATION.md').write_text(explanation)

def edit(name,replacements):
    p=REPO/name;s=p.read_text()
    for old,new in replacements:
        assert old in s,(name,old[:100]);s=s.replace(old,new)
    p.write_text(s)

edit('README.md',[
('This is a stronger proposed architectural explanation and a better evidence trail, not identification of the full cipher or a claim of complete transcript coverage.','That earlier update supplied an architectural proposal. The later reconstruction below identifies the original operations and key handling; it does not claim complete transcript coverage.'),
('The four original fixed lookup memories contain identical effective nonlinear 256-entry byte permutations, but the full cipher and embedded key semantics remain unidentified.','The subsequent reconstruction restores the original bit ordering and identifies all four tables as the AES S-box, inside a custom 32-bit four-round cipher with fixed-mask key handling.'),
('## What the saved evidence supports','## Original cipher now reconstructed\n\nThe [new reconstruction report](submission/addenda/2026-11-12-cipher-reconstruction/README.md) establishes four rounds of fixed-mask XOR, AES byte substitution and one-byte word rotation; decryption reverses those operations. The same hardwired 32-bit mask is reused in each round, with no runtime key load or evolving key schedule in the supplied protocol. This is a custom 32-bit cipher, not standard AES.\n\nIndependent source checks and the untouched original Verilog agree: 2,564 transactions, 20,512 internal round-state comparisons and 12,820 serial/BUSY checks, zero failures. Qwen reviews, the Trojan chat’s independent audit, actual errors/refinements and reproduction scripts are preserved. This closes the earlier cipher-operation/key-handling explanation gap; the separate submission limitations remain.\n\n## What the saved evidence supports'),
('The augmented ZIP has its own hash and does not imply a new simulation run.','The augmented ZIP has its own hash. The new original-baseline simulation is explicitly recorded in the reconstruction addendum; the historical modified-design suite is unchanged.'),
('No published challenge solutions, board programming, key recovery or generation workflow was used in this publication review.','No published challenge solutions, board programming, numeric bonus-key claim or new attack-generation workflow was used in these follow-ups. The source-derived fixed mask is used internally by the mathematical reconstruction.')])

edit('SUBMISSION_GAPS.md',[
('fresh synthesis and protocol-scoped formal verification.','fresh synthesis, protocol-scoped formal verification and the original-source cipher reconstruction.'),
('The new explanation describes serial loading, working state, lookup storage, direction selection and the delayed result-load boundary, with original-source references.','The new explanation identifies a custom 32-bit four-round cipher using the AES S-box, fixed-mask XOR and byte rotation, its exact inverse, and the delayed result-load boundary.'),
('Exact algorithm identity, round equations and embedded key semantics remain unestablished. Four identical effective nonlinear byte permutations and the documented absence of a separate host key transaction are now evidenced. The requirement is for a proposed explanation; this is an architectural proposal, not a full mathematical reconstruction.','The round equations, AES-table bit ordering and effective fixed-mask handling are now established from original sources and checked against the original simulator. The same hardwired 32-bit mask is reused in every round, with no evolving schedule or normal runtime key load. Author naming/rationale and cryptographic strength remain unknown; no numeric bonus-key result is claimed. End-to-end simulation is finite, distinct from exact local byte/control checks.'),
('They do not prove the cipher or physical hardware.','Those earlier preservation proofs do not identify the cipher. The new original-baseline reconstruction and simulation address the cipher separately; neither validates physical hardware.'),
('It performs synthesis/formal checks but does not change the original RTL or run the original simulation suite.','The follow-ups perform synthesis/formal checks and a new original-baseline cipher simulation, while leaving the original RTL and archived modified-design simulation suite unchanged.'),
('The three new Qwen request/response streams are retained, including incorrect model assertions and the corrective prompt.','The earlier three Qwen verification streams remain intact. The cipher reconstruction adds two further real Qwen review streams, with their incorrect assertions and corrective prompt explicitly documented. Its current analysis records are separate from the historical generation-log gaps.')])

edit('submission/CURRENT_GUIDE.md',[
('The latest update adds fresh synthesis, protocol-scoped formal checks, a reference-board pin audit and Qwen review records.','The follow-ups add fresh synthesis, protocol-scoped formal checks, a reference-board pin audit, original-source cipher reconstruction and Qwen review records.'),
('Full cipher/key semantics are still unknown, although fixed-table properties and the lack of a separately documented runtime key transaction are now evidenced.','The [new reconstruction](addenda/2026-11-12-cipher-reconstruction/README.md) now establishes the exact round operations and effective key handling: four rounds of fixed-mask XOR, AES byte substitution and one-byte rotation, with the inverse path checked independently.'),
('The recovered design accepts one 32-bit word through a serial input. A separate working register bank processes it through Boolean logic and four initialized memory blocks whose write clocks are disabled. A mode input selects encryption or decryption behavior inside the datapath. The result returns to the serial bank for readout.','The recovered design accepts one 32-bit word. Its forward path performs four rounds of XOR with a hardwired 32-bit mask, AES byte substitution and one-byte rotation. A separate working-register path performs the inverse concurrently. The mode input selects the completed result at the serial-bank load. The mask stays fixed; there is no normal runtime key load or evolving key schedule.'),
('It deliberately does not identify the stored tables, recover a key or import an algorithm from another solution. The separate professor-supplied AES example is not evidence that this design implements AES.','The newer analysis identifies the stored AES S-box after restoring the original bit wiring and verifies the round equations against the untouched original Verilog: 2,564 transactions, 20,512 round-state comparisons and zero failures. The fixed mask is derived internally for reproduction; no numeric bonus-key artifact is emitted. No algorithm was imported from a challenge solution. The separate professor-supplied AES example remains unrelated evidence.'),
('| Internal cipher mathematics | Architecture, fixed-table properties and the documented external key-interface boundary are evidenced. Exact algorithm identity, round equations, embedded key semantics and cryptographic strength remain unestablished. |','| Cipher limits after reconstruction | The exact four-round operations, AES S-box ordering and effective fixed-mask handling are established. Author naming/rationale and cryptographic strength remain unverified. Exact byte/control checks and finite end-to-end simulations are not a whole-system proof for arbitrary protocol or physical behavior. |'),
('The encryption proposal is present but remains architectural.','The encryption explanation now includes exact original-source round equations and verified key handling.'),
('The latest follow-up runs synthesis and formal verification of unchanged files; it does not rerun the archived simulation runner or use published challenge solutions.','The follow-ups run synthesis/formal verification and a new original-baseline reconstruction simulation. They do not rerun the archived modified-design simulation runner or use published challenge solutions.'),
('All three new Qwen calls retain their requests, received streams and replies, including rejected overclaims.','The earlier three Qwen verification calls and two later cipher-review calls retain requests, received streams and replies, including rejected overclaims. Current record cutoffs and any separate documentation-audit gaps are disclosed in each addendum.')])

edit('submission/PUBLICATION_STATUS.md',[
('No new simulations were run and no new simulation results are implied by the new ZIP hash. Static analysis and record-integrity checks are separately labeled.','The initial documentation-only publication ran no simulations. Later verification is separately labeled: the cipher-reconstruction addendum now includes a fresh simulation of the untouched original baseline and its primitive models, with 2,564 passing transactions. The historical modified-design suite remains unchanged.'),
('No physical board was programmed or tested.','No physical board was programmed or tested. The latest [cipher reconstruction](addenda/2026-11-12-cipher-reconstruction/README.md) establishes the custom 32-bit four-round transform and fixed-mask key handling, with independent source checks, original simulation and retained Qwen/Trojan-chat records.')])

edit('submission/PUBLICATION_REVIEW.md',[
('**Later documentation update:**','**Current cipher follow-up:** The [reconstruction report](addenda/2026-11-12-cipher-reconstruction/README.md) now identifies the exact four-round transform and fixed-mask handling from original files. A fresh original-baseline simulation passes 2,564 transactions. Earlier unknown-cipher and no-execution statements below describe their dated review stages, not this new verification. Original files remain unchanged.\n\n**Later documentation update:**'),
('The exact cipher, embedded key semantics, stealth, physical timing and fully automated historical generation remain unestablished.','At that stage, cipher operations and key semantics remained unidentified; the subsequent reconstruction above resolves those specific limits. Stealth, physical timing and fully automated historical generation remain unestablished.')])
print('Updated six reader-facing documents; previous versions retained in the new analysis bundle.')
