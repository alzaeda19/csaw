# Qwen-assisted verification of the unchanged CSAW package

November 12, 2026, America/New_York. This update adds measured evidence and a reference-board pin map. It does not identify the complete cipher, establish stealth, or turn the historical development process into fully automated generation. The original design files are unchanged.

## What is now established

| Question | New result | Boundary |
|---|---|---|
| Reference-board wiring | All nine signals map consistently across original host declarations, original FPGA coordinates, the board designer's February 2026 Rev A schematic and Lattice's SG48 pin table. | This documents that reference board; no particular physical unit was inspected or programmed. The older automatically assigned bitstream is not thereby board-correct. |
| Normal-operation preservation | A compositional proof covers arbitrarily many well-formed normal transactions in the synchronous model, with arbitrary allowed payload/mode each time. A separate explicit-edge check covers two consecutive transactions. Controls allowing the disclosed fault case correctly fail. | The induction result is restricted to the specified cyclic host schedule and synchronous abstraction; it is not a proof for arbitrary protocol traces or of the cipher. |
| Hardware overhead | Identical synthesis settings give +36 LUT4 cells, +48 registers and +13 carry cells; memory count is unchanged. | Mapped primitive counts, without placement, routing, timing or power. No criterion makes this automatically negligible. |
| Fixed storage | All four memories implement the same effective 256-entry, 8-bit nonlinear bijection; synthesized write clocks and write-clock enables are zero. Separate WE inputs are high. | Table properties do not identify the cipher, key semantics or a key schedule. |
| Runtime key interface | The recovered interface has six input signals; the supplied host sends a 32-bit message and selects a direction. It has no separately documented runtime key transaction or key port. | This does not prove the absence of embedded key-dependent constants or undocumented semantics. No secret key was recovered. |
| Verification automation | One command reproduces synthesis, table analysis and seven proof/control checks in a new directory. A fresh reproduction passed all twelve steps and matched the structured results. | Validation automation only; it does not alter or prove the historical generation workflow. |

## Reference-board correction

| Signal | RP2040 GPIO | FPGA SG48 pin |
|---|---:|---:|
| SCK | 6 | 36 |
| RST_N | 7 | 34 |
| MOSI | 8 | 32 |
| MISO | 9 | 31 |
| NORM_CS_N | 10 | 28 |
| START | 12 | 27 |
| ENC_DEC | 13 | 25 |
| BUSY | 14 | 23 |
| ICE_LED | — | 38 |

The simulation adapter names the two duplicate outputs oppositely: its logical BUSY is physical LED/pin 38, and its logical LED is physical BUSY/pin 23. The original core assigns those outputs equal logic, so the interchange was invisible in the saved digital simulations. The [pin audit](pin_audit/REPORT.md) gives primary sources, coordinates, board nets, vendor rows and remaining hardware limits. The unchanged adapter is not a validated physical constraint file.

The included board schematic and derived crops are attributed to **Hammond Pearce, UNSW Sydney**, under **CC BY-SA 4.0**. See [source attribution](pin_audit/ATTRIBUTION.md). The full Lattice workbook is not republished; relevant factual rows, its URL and hash are retained. The source audit manifest describes the original full audit, while its publication-copy receipt lists the intentional omission.

## Exact normal-operation claim

The frozen wrapper connects the same six inputs directly to the same recovered core as the baseline adapter. BUSY and LED are forwarded; MISO differs only by an XOR mask. A zero-output abstract core exposes every mask event. Proving that the mask never asserts under the stated schedule, combined with the unchanged input connections and XOR identity, establishes equality of sampled output behavior for coupled core state in that scope. It does **not** establish cryptographic correctness of the abstracted core.

Each of two independent transactions permits every 32-bit word in decryption mode, and every word except the already disclosed demonstration word in encryption mode. Modes remain stable through each transaction. Inputs are reset before the first transaction, then loaded as exactly 32 bits, with one START pulse, the prescribed extra processing/readout clocks, exactly 32 extraction clocks, and the recorded idle interval. No reset is added between the two transactions. Extraction MOSI is unconstrained.

The first model checks 161 synchronous SAT steps after `async2sync`. The stronger follow-up uses `clk2fflogic`, explicitly alternates SCK low/high, and checks 325 global samples. Assertions cover counter cycles 1–159. The negative controls remove only the normal-word exclusions; explicit traces show the existing disclosed encryption case and the expected output-mask event at readout. Thus the success is not obtained by preventing the demonstrated behavior from occurring in the control.

A further cyclic harness resets once, then repeats the same 80-cycle transaction schedule indefinitely with a fresh arbitrary allowed word/mode each time. Yosys proved its base case and temporal-induction step at length 100. This establishes mask-free behavior for arbitrarily many normal transactions in the synchronous/async2sync model. A separate cyclic negative control permits the disclosed fault case and correctly fails. The proof does not cover arbitrary protocol traces, malformed frames, unstable controls, clock glitches, metastability or physical timing. The explicit-edge model remains bounded to two transactions; it is not the unbounded model. Sources, harnesses, commands, solver logs and controls are under `sources/` and `formal/`; [VERIFICATION_RESULTS.json](analysis/VERIFICATION_RESULTS.json) records the checks and limits.

## Measured synthesis overhead

| Mapped resource | Baseline | Modified | Added | Relative change |
|---|---:|---:|---:|---:|
| LUT4 | 1,439 | 1,475 | 36 | 2.5017% |
| Flip-flops | 71 | 119 | 48 | 67.6056% |
| RAM4K | 4 | 4 | 0 | 0% |
| Carry cells | 0 | 13 | 13 | Not defined from zero |

Both use the installed Yosys 0.70+344 build and identical `synth_ice40` defaults on the unchanged sources. These resource categories cannot be added as if they had equal silicon area. Source LUT tags and newly mapped LUT counts are different measures. The results quantify overhead; they do not prove negligible overhead or a stealth score. Full reports and tool receipts are under `synthesis/` and [OVERHEAD.json](analysis/OVERHEAD.json).

## Cipher and key-handling findings

The earlier explanation deliberately did not inspect memory contents. This update examines only the original initialization values and the supplied primitive's read layout. Each physical memory uses eight varying address bits and eight connected outputs, selecting an effective 256-entry table. The four effective tables are identical, bijective and non-affine in that bit order. Raw table values are not emitted as a claimed key or recovered cipher.

A separate comparison implements the public AES substitution definition from [NIST FIPS 197, sections 4 and 5.1.1](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf). None matches the AES S-box or inverse S-box in the extracted effective bit order. This narrow comparison neither rules out differently wired components nor names the surrounding algorithm. No challenge solution or shared implementation was consulted.

The original host's message writes are at `sources/host.py` lines 42 and 110; its messages and direction are identified at lines 14, 33–40 and 107–108. The original core's six input ports are on `sources/baseline.v` line 3. The synthesized memory controls corroborate fixed storage, not a writable key buffer. These facts narrow the documented interface; exact key origin, embedded constants and key-dependent computation remain unresolved.

## Qwen's role and retained errors

The existing local `qwen3-csaw-agent:20261112234518` model supplied three text-only reviews through Ollama. It received no file-writing or execution tools. Exact requests, received streams, responses, runtime metadata and receipts are retained in `ai_logs/` and `records/MODEL_IDENTITY.json`. Codex wrote and ran the verification-only harnesses/scripts, checked Qwen's claims, and organized the evidence; Qwen did not run the proofs or synthesis.

Qwen incorrectly described overhead as negligible and confused synthesis of the full designs with harness overhead. Its refinement still contains a residual attribution error. [QWEN_REVIEW_NOTES.md](QWEN_REVIEW_NOTES.md) records the rejected statements and authoritative corrections. Model agreement is not verification evidence.

The pin audit separately discloses four unreadable peer-task exchanges and three unreadable progress messages in its documentation-review history. These are separate from the twelve previously missing generation-review instructions. No original dialogue is invented. This task's visible Codex snapshot records its cutoff; tool-output outcomes are separately captured in experiment receipts.

## Reproduce these checks

Python 3 and a compatible installed Yosys build are required. The tested build is recorded in the synthesis logs; other tool versions are not certified. From this folder, run:

```sh
python3 reproduce_verification.py --yosys /absolute/path/to/yosys --output /absolute/path/to/new-output-directory
```

The output directory must not already exist. The script copies frozen inputs, runs twelve verification steps, checks the expected positive and negative outcomes, and records commands and results. It makes no network or model calls, modifies no source design, generates no new Trojan, and programs no hardware. The successful fresh-directory replay is recorded in `records/REPRODUCTION_RECEIPT.json` and `records/REPRODUCTION_COMMANDS.json`.

## Still unproved

The exact cipher and key semantics, preservation for arbitrary protocol histories outside the proved cyclic schedule, stealth/detector evasion, negligible physical overhead, physical-board behavior and fully automated historical generation remain unestablished. The disclosed comparison and output-mask logic are visible in the source; no concealment was added and no claim of undetectability is made. The new measurements and conditional proof strengthen the submission's evidence without turning those open questions into claimed successes.
