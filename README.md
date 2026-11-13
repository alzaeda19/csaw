# CSAW 2026 — simulation submission and evidence

The current simulation package is in [submission/](submission/). Download [submission.zip](submission.zip) for the source/evidence folder, with [SHA-256 receipt](submission.zip.sha256).

**The previously missing modified RTL and demonstration testbench are now present.** Saved simulations pass the stated tests. This does not establish satisfaction of every grading criterion or instructor acceptance. [Current limitations and submission status](SUBMISSION_GAPS.md) remain explicit.

## Review the current package

1. [Plain-English handoff](submission/HANDOFF_SIMPLE.md).
2. [Technical brief and reproduction instructions](submission/README.md).
3. [AI records, mixed authorship and missing-history disclosures](submission/ai/AI_RECORDS_INDEX.md).
4. [Publication review and requirement mapping](submission/PUBLICATION_REVIEW.md).
5. [Current package status](submission/PUBLICATION_STATUS.md) and [publication manifest](submission/PUBLICATION_MANIFEST.json).

The code was developed in the separate workspace coordinated by the Trojan chat. Qwen produced initial drafts; Codex made substantive corrections and wrote the final testbench. Claude Code was the file-tool client for Qwen, not evidence of Claude-model authorship. Failed drafts, timeouts, corrections and available authentic records remain included.

## What the saved evidence supports

| Saved check | Outcome |
|---|---|
| Baseline ordinary operation | 88 transactions, 6,726 checks, zero failures |
| Modified ordinary operation | 88 transactions, 6,726 checks, zero failures |
| Simulation demonstration | 39,718 checks, zero failures |
| Two deliberately broken controls | Correctly fail the recorded tests |

These are finite assertion counts, not thousands of independent cipher vectors. The saved source-relocation run used the same external toolchain. The upload review verified files, hashes, exit records and result summaries against saved logs; it did not rerun or modify the simulation design.

The recovered baseline is preserved. This package is distinct from the earlier readiness-repaired derivative and the separate professor-supplied AES reference. Older proofs and detector results do not certify this modification. No stealth, detector-evasion, wrapper synthesis, board timing, universal-equivalence or key-recovery result is claimed.

## Reproduction and integrity

Extract the ZIP **outside a Git checkout** before following its README: the archived runner deliberately refuses to write inside a Git repository. Python 3 and compatible external Icarus/VVP tools are required; the package records the exact tested development build and how to supply its location. Other platforms/tool versions are unverified.

For repository byte integrity only, run:

```sh
python3 tools/verify_evidence.py
```

That checker does not run archived project code. REPOSITORY_MANIFEST.json covers repository files. The unchanged original package manifest records its 262-file input package; submission/PUBLICATION_MANIFEST.json also covers publication notes and upstream licenses. All original files, including the seven frozen runner/RTL/testbench files, remain byte-identical. The augmented ZIP has its own hash and does not imply a new simulation run.

## Earlier work and provenance

Earlier baseline recovery, bitstream checks, ordinary verification, separate clean AES tests and four-detector studies remain under [evidence/](evidence/) and [supplementary_clean_verification/](supplementary_clean_verification/). Their limitations and failed checks are retained. Earlier Claude reviews concern their stated packets, not an independent review of this new design.

Previous top-level status documents are preserved under [publication/nov12-package-integration/](publication/nov12-package-integration/). Historical statements that modified RTL/testbench were absent or nothing had been uploaded describe those earlier stages. Current artifact presence is described above; no missing historical AI dialogue has been reconstructed.

The user specified GitHub as the submission destination and requested **no collaborator invitations for now**. The user subsequently explicitly authorized **public visibility**, including the retained AI records and local paths. Anyone can view the public repository without a collaborator invitation. Publication is not proof of instructor receipt, grading acceptance or complete rubric compliance. No additional professor email or portal submission was made. Jason's reply directs the original guidelines; the defensive alternative is not treated as approved.

Paper 5 remains separate. No published challenge solutions, board programming, key recovery or generation workflow was used in this publication review. Original projects and their uncommitted changes were preserved. [Third-party notices](THIRD_PARTY_NOTICES.md) and the package's upstream notices retain source attribution.
