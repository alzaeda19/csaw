# CSAW GitHub intake audit

Reviewed the existing `outputs/CSAW_submission_review_2026-11-11` without executing its code or changing it. This is an upload/content audit, not a new experiment or a claim of assignment completion.

## Evidence integrity and contents

- 753 files, 46,895,383 bytes. All 752 entries in the combined manifest match their recorded sizes and SHA-256 hashes. The manifest excludes itself.
- Retained source is the recovered baseline, normal-operation testbenches, ordinary professor AES reference, evidence-export scripts, and frozen detector evaluation/verification scripts. No required modified-design or trigger/payload testbench is present.
- No input Trojan RTL, detector weights, generator notebook, or attack implementation is included in the compact defensive appendix. Saved classifications alone do not execute a payload.
- No file exceeds GitHub's usual individual-file limit; largest is a disposable compiled AES simulation (15,630,187 bytes).

## Upload recommendations

Include the summaries, current status/requirements, qualified baseline artifacts, normal-operation verification, detector results, genuine bounded logs, and provenance/manifests in a PRIVATE repository. Preserve all claims and known failures. Use a new repository-level README/status wrapper to distinguish a GitHub push from actual course submission and to record the user's newer relative 30-hour deadline; do not silently rewrite historical records.

Before copying third-party source into the new repository, add complete license texts and attribution/provenance, or exclude those sources explicitly. None of LICENSE/NOTICE/COPYING is present in this package. Four professor AES files preserve Apache-2.0 headers: `core_evidence/verification/clean_aes_reference/sources/designs/aes_128/{aes_128,round,table}.v` and `core_evidence/verification/clean_aes_reference/sources/testbenches/tb_aes_128.v`. `core_evidence/verification/baseline_equivalence/simulation/sources/cells_sim.v` is copied from the locally recorded Yosys installation and needs the matching notice/license provenance. Keep original source headers. Do not blanket-license professor challenge materials as student-authored.

Omit these optional generated files from Git history (retain immutable originals locally):
- `core_evidence/verification/clean_aes_reference/runs/20261110T123203.879963Z/clean_aes.vvp`
- `core_evidence/ai/recovered_records/coordinator/__pycache__/export_coordinator_visible.cpython-312.pyc`

If the repository excludes or redacts any file, create a separate repository manifest and explicit inclusion/omission record. The unchanged source-package manifest remains historical provenance, not a claim that every listed file is present in the filtered repository. Do not embed an unfiltered ZIP if doing so would bypass the intended exclusion.

## Credential and privacy triage

Pattern checks across all text-readable files found no GitHub tokens, Anthropic/OpenAI key-shaped credentials, AWS access-key identifiers, private-key blocks, JWTs, quoted credential assignments, or credential-bearing HTTP URLs. The `ANTHROPIC_API_KEY` name appears in saved CLI help, with no value. Email matches are software authors/credits and tool version output. These checks do not prove the absence of every possible secret format.

Absolute local paths, account name, project-chat identifiers and scoped conversations are present throughout provenance and logs. They are appropriate only for the authorized PRIVATE course repository. No public upload or unrelated chat export is recommended. Export boundaries already document the omission of mixed/solution-contaminated earlier history. This audit did not attempt to reconstruct those omissions.

## Exact submission gaps

1. Original mandatory AI-generated Trojan-modified RTL: absent. The included baseline is explicitly not that artifact.
2. Original mandatory demonstration/exploit testbench: absent. Ordinary baseline/AES regressions are explicitly not that artifact.
3. Comprehensive AI interactions: unproven. Bounded authentic logs exist, but encrypted/truncated/unmapped histories, original Claude conversations, and post-cutoff records remain missing or excluded. Do not call them complete.
4. Full original technical brief: incomplete. It documents completed verification but does not establish a complete explanation of the recovered cipher or cover the missing modification/demo requirements.
5. Approval of the defensive alternative: no approval recorded. Detector results do not themselves replace original deliverables.
6. Administrative delivery: current course upload route and actual accepted submission receipt are absent. A GitHub push will satisfy the user's repository request, not prove course submission or instructor acceptance.

Technical qualification: original-host checks are 24/24 passing per model, while the first-BUSY-low timing gives 8/8 failures per model. This archived package does not establish a later repair. Equivalence is conditional and not independent cipher or physical-hardware proof. Baseline/AES detector graph limitations and poor toy-dataset false-positive behavior are correctly disclosed. Physical-board validation is not required by the preserved simulation-only qualifier. Independent key recovery is optional bonus in those instructions, not a mandatory missing artifact.

The compact package also lacks all dependencies, weights, full graph artifacts and toy RTL needed for a fully standalone detector rerun; historical paths are retained. These are reproducibility limitations to state, not reasons to invent results.

## Conclusion

Suitable for a PRIVATE, clearly labeled partial-evidence repository after adding license/provenance material and a current repository wrapper. Not a complete original-assignment submission. No need to remove truthful failure evidence or fabricate missing logs. No archived code was run in this review.
