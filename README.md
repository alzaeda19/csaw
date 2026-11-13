# CSAW 2026 — simulation submission and evidence

The current simulation package is in [submission/](submission/). Download [submission.zip](submission.zip) for the source/evidence folder, with [SHA-256 receipt](submission.zip.sha256).

**The previously missing modified RTL and demonstration testbench are now present.** Saved simulations pass the stated tests. This does not establish satisfaction of every grading criterion or instructor acceptance. [Current limitations and submission status](SUBMISSION_GAPS.md) remain explicit.

**November 13 closeout:** [Required versus optional submission checklist](submission/SUBMISSION_CHECKLIST.md) and [plain-English explanation of stealth evidence](submission/addenda/2026-11-13-submission-closeout/STEALTH_IN_PLAIN_ENGLISH.md). One previously incomplete reviewer tool output is now fully assembled from authentic captures; twelve reviewer inputs and one output gap remain. All four artifact types are present; stealth and complete relevant logs remain unresolved.

## Latest detector repair and evaluation

The [defensive detector repair](submission/addenda/2026-11-13-detector-repair/README.md) fixes broken signal-reference connections in a separate extractor copy. All 11 benign fixture checks and both target coverage gates passed before the unchanged models ran. Hardware sources, flattened inputs, weights, normalization and decision rules remain unchanged.

| Detector | Clean control | Existing modified design |
|---|---|---|
| HT1 | CLEAN | CLEAN |
| HT2 | CLEAN | TROJAN |
| HT3 | CLEAN | CLEAN |
| HT4 | TROJAN | TROJAN |

HT2 detects the modification while passing the control. HT4 detects it but also falsely flags the clean design; HT1 and HT3 miss it. The existing any-positive ensemble flags both. These are results for one pair under a validated data-dependency abstraction, not a general accuracy estimate, complete clock/physical model or stealth certificate. The earlier all-CLEAN results used broken graphs and are retained as historical diagnostic evidence. The repair was frozen before classification and was not adjusted to the scores.

The code, tests, errors, refinements, hashes and visible AI records are included in the repository and ZIP. The attempted Trojan-chat review was blocked before a response; this update makes no new independent-review or Qwen-review claim. **Stealth and complete historical AI records remain unresolved.**

## Earlier frozen-design detection evaluation

The [Qwen/Trojan-chat evaluation](submission/addenda/2026-11-13-detection-evaluation/README.md) is complete. Qwen identified the added output behavior, and an independent scoped formal comparison found a mismatch. Six fresh full-core simulations passed: 270 transactions and 39,960 observed output triples each, with all raw/flattened representation traces matching their respective originals. These tests validate the analysis inputs; they do not establish stealth.

All four supplied detectors ran on both clean and modified designs in two predeclared representations. Raw-source parsing fails and uses an incomplete fallback: HT1 flags the modified design. Flattened graphs receive all-CLEAN labels, but thousands of signal references remain unjoined; the independent review confirms the model actually received those incomplete edges. Both earlier routes fail whole-design coverage; the later repair above addresses the flattened graph's reference-joining defect within its stated abstraction. All sixteen scores, failures, exact prompts, Qwen errors and limitations are retained. **The modification is detectable under source/formal review; stealth remains unestablished.** No design or detector was tuned to obtain a favorable result.

The later [review of the three shared Claude chats](submission/addenda/2026-11-13-shared-chat-review/README.md) supplies no new evidence of stealth. It distinguishes the excluded solution-derived plan, the older package audit and unsupported model descriptions. It also clarifies that the rules require neither universal undetectability nor a particular detector result; source/formal discovery is not an automatic grading verdict. The stealth objective and historical log gaps remain unestablished/disclosed.

## Review the current package

1. [Current submission guide and exact remaining gaps](submission/CURRENT_GUIDE.md).
2. [Plain-English encryption explanation](submission/ENCRYPTION_EXPLANATION.md), with a data-flow sketch and links to the detailed original-source evidence.
3. [Newly integrated Claude/Qwen/chat records](submission/addenda/2026-11-12-recovered-records/README.md), alongside the earlier [generation](submission/addenda/2026-11-12/records/generation_tail/EXPORT_MANIFEST.json) and [reviewer](submission/addenda/2026-11-12/records/reviewer_recovery/README.md) recovery.
4. [Original technical brief and reproduction instructions](submission/README.md), retained unchanged with its original AI-record index.
5. [Current package status](submission/PUBLICATION_STATUS.md), [publication review](submission/PUBLICATION_REVIEW.md), and [publication manifest](submission/PUBLICATION_MANIFEST.json).

The November 12 documentation update adds a source-supported explanation of serial loading, the working datapath, fixed lookup storage, direction selection and result readout. It also recovers 44 records beyond the earlier generation-export cutoff and two previously unexported reviewer final responses. The earlier 155 retained parent records are preserved exactly. Twelve reviewer instruction bodies remain unreadable; their parent and child copies are the same exchanges, not 24 separate gaps. That earlier update supplied an architectural proposal. The later reconstruction below identifies the original operations and key handling; it does not claim complete transcript coverage.

The subsequent record-integration update includes the 101-file local collection in both the repository and ZIP, without changing its original text. Its historical statements that it was not uploaded are superseded by the publication supplement. The new explanation separates the architecture, supporting evidence and remaining unknowns. The added setup records and older chat excerpts do not recover the twelve unreadable reviewer instructions or identify the cipher. Unsupported Qwen drafts remain labeled as errors; solution-derived Claude implementation material is excluded.

The code was developed in the separate workspace coordinated by the Trojan chat. Qwen produced initial drafts; Codex made substantive corrections and wrote the final testbench. Claude Code was the file-tool client for Qwen, not evidence of Claude-model authorship. Failed drafts, timeouts, corrections and available authentic records remain included.

## New verification evidence

The [Qwen-assisted follow-up](submission/addenda/2026-11-12-qwen-verification/README.md) adds fresh synthesis, conditional formal verification and a reference-board pin map without changing the original design. A temporal-induction proof establishes unchanged sampled outputs for arbitrarily many prescribed normal transactions in the synchronous model; a separate explicit-edge check covers two transactions. These are conditional compositional results, not a proof of the cipher or arbitrary protocol/physical behavior.

Measured overhead is +36 LUT4 cells (2.5017%), +48 registers (67.6056%) and +13 carry cells, with no additional RAM. All nine reference-board pins are documented; physical BUSY is pin 23 and LED is pin 38, opposite the interchangeable simulation-adapter labels. The subsequent reconstruction restores the original bit ordering and identifies all four tables as the AES S-box, inside a custom 32-bit four-round cipher with fixed-mask key handling. A fresh twelve-step verification replay passed. Qwen's three advisory replies, including rejected overclaims and corrections, are retained.

## Original cipher now reconstructed

The [new reconstruction report](submission/addenda/2026-11-12-cipher-reconstruction/README.md) establishes four rounds of fixed-mask XOR, AES byte substitution and one-byte word rotation; decryption reverses those operations. The same hardwired 32-bit mask is reused in each round, with no runtime key load or evolving key schedule in the supplied protocol. This is a custom 32-bit cipher, not standard AES.

Independent source checks and the untouched original Verilog agree: 2,564 transactions, 20,512 internal round-state comparisons and 12,820 serial/BUSY checks, zero failures. Qwen reviews, the Trojan chat’s independent audit, actual errors/refinements and reproduction scripts are preserved. This closes the earlier cipher-operation/key-handling explanation gap; the separate submission limitations remain.

## What the saved evidence supports

| Saved check | Outcome |
|---|---|
| Baseline ordinary operation | 88 transactions, 6,726 checks, zero failures |
| Modified ordinary operation | 88 transactions, 6,726 checks, zero failures |
| Simulation demonstration | 39,718 checks, zero failures |
| Two deliberately broken controls | Correctly fail the recorded tests |

These are finite assertion counts, not thousands of independent cipher vectors. The saved source-relocation run used the same external toolchain. The upload review verified files, hashes, exit records and result summaries against saved logs; it did not rerun or modify the simulation design.

The recovered baseline is preserved. This package is distinct from the earlier readiness-repaired derivative and the separate professor-supplied AES reference. Older proofs and detector results do not certify this modification. No stealth, detector-evasion, board timing, arbitrary-protocol universal-equivalence or key-recovery result is claimed. The new synthesis and protocol-scoped formal results are separately documented above.

## Reproduction and integrity

Extract the ZIP **outside a Git checkout** before following its README: the archived runner deliberately refuses to write inside a Git repository. Python 3 and compatible external Icarus/VVP tools are required; the package records the exact tested development build and how to supply its location. Other platforms/tool versions are unverified.

For repository byte integrity only, run:

```sh
python3 tools/verify_evidence.py
```

That checker does not run archived project code. REPOSITORY_MANIFEST.json covers repository files. The unchanged original package manifest records its 262-file input package; submission/PUBLICATION_MANIFEST.json also covers documentation, recovered-record supplements and upstream licenses. All original files, including the seven frozen runner/RTL/testbench files, remain byte-identical. The augmented ZIP has its own hash. The new original-baseline simulation is explicitly recorded in the reconstruction addendum; the historical modified-design suite is unchanged.

## Earlier work and provenance

Earlier baseline recovery, bitstream checks, ordinary verification, separate clean AES tests and four-detector studies remain under [evidence/](evidence/) and [supplementary_clean_verification/](supplementary_clean_verification/). Their limitations and failed checks are retained. Earlier Claude reviews concern their stated packets, not an independent review of this new design.

Previous top-level status documents are preserved under [publication/nov12-package-integration/](publication/nov12-package-integration/). Historical statements that modified RTL/testbench were absent or nothing had been uploaded describe those earlier stages. Current artifact presence is described above; no missing historical AI dialogue has been reconstructed.

The user specified GitHub as the submission destination and requested **no collaborator invitations for now**. The user subsequently explicitly authorized **public visibility**, including the retained AI records and local paths. Anyone can view the public repository without a collaborator invitation. Publication is not proof of instructor receipt, grading acceptance or complete rubric compliance. No additional professor email or portal submission was made. Jason's reply directs the original guidelines; the defensive alternative is not treated as approved.

Paper 5 remains separate. No published challenge solutions, board programming, numeric bonus-key claim or new attack-generation workflow was used in these follow-ups. The source-derived fixed mask is used internally by the mathematical reconstruction. Original projects and their uncommitted changes were preserved. [Third-party notices](THIRD_PARTY_NOTICES.md) and the package's upstream notices retain source attribution.
