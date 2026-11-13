# Suggested plain-language opening

The original recovered design is consistent with a multi-cycle, table-assisted transform of a 32-bit word. The host shifts the word into a 32-register serial bank, most-significant bit first. A separate 32-register working bank and Boolean logic perform the computation, using four initialized memory blocks. Their write controls are disabled during normal operation, so they supply fixed lookup data. This establishes their storage role, but does not identify what the stored values mean. The direction input changes the datapath behavior; the original specification calls its two settings encryption and decryption.

The result must then be copied back into the serial bank before it can be shifted out. BUSY falling indicates a processing boundary; it does not mean that copy has already occurred. The recovered control logic enables the copy on the following rising clock edge while chip-select remains high. This explains why the recorded immediate-read tests failed while the original host's longer clock schedule passed.

The supplied plaintext/ciphertext pair agrees with the two documented directions. Broader comparisons and conditional proofs show agreement between particular hardware representations under their stated assumptions. They do not identify a standard cipher or prove that both directions are mathematical inverses for every input. Algorithm identity, table meanings, key handling and cryptographic strength remain unestablished. The separate course AES example and unverified model-written AES claims do not resolve those questions.

## Evidence boundary

This is a proposed clearer opening, not a new technical result. Retain the current detailed explanation, source index and limitations after it. Support is already mapped in `submission/addenda/2026-11-12/explanation/EVIDENCE_MAP.json`: E02–E04 (interface/serial movement), E05–E07 (registers, memory and mode), E08–E09 (completion/readout), E10–E12 (oracles, equivalence and limits). The baseline identity is SHA-256 `180b895d9e3ada5f662ee502277db1eedcfd80bd53fbf29d9a612fcc3e1b1765`.

Do not relabel processing clocks as cipher rounds, infer AES from the professor's separate reference, or treat fixed initialization data as an identified key. No source code or design behavior needs to change for this wording improvement.
