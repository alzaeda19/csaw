# AUDIT_FINDINGS — records and claim verification (revised)

**Original audit:** prepared 2026-11-11 for the `csaw` partial-submission repository. Configured model: Claude Opus 4.8 (serving model may differ; no new inference was run against any design). This attribution is historical and is retained unchanged.

**Revision:** 2026-11-11. This is a new, tool-disabled Claude Code document correction (session model `claude-opus-5-5`). It applies only the supplied verified facts listed in the revision note. This revision did not read, hash, execute or rerun anything. The original `AUDIT_SESSION_RECORD.md` remains the authentic record of the original audit and is not rewritten here.

## Scope and method
This audit covers records and claim verification only. It excludes cipher analysis, design alignment, RTL repair, hardware modification, TrojanGYM, published solutions, archived-script execution, commits, pushes and submission.

The original audit reports that it checked integrity by independent `sha256` re-hashing, without running `tools/verify_evidence.py`. A matching hash is evidence of file integrity only. It is never evidence of functional correctness.

## 1. Artifact inventory (provenance + hashes)

| Design | Path | sha256 | Size | Notes |
|---|---|---|---|---|
| Recovered baseline RTL | `evidence/core_evidence/rtl/baseline_reference/baseline.v` | `180b895d9e3ada5f` (first 16) | 45,711 lines | A byte-identical copy exists at `supplementary_clean_verification/baseline_recovery_2026-11-06/adapters/recovered_iverilog.v` (same hash). |
| Readiness-repaired RTL | `supplementary_clean_verification/result_readiness_repair_2026-11-06/derivative/recovered_readiness_repaired.v` | `bed2bda6d9521812` (first 16) | 45,945 lines | Distinct from baseline (+234 lines). Documented as an intentional normal-operation timing repair, not exact recovery. |
| Regenerated/decoded RTL | `evidence/core_evidence/verification/baseline_equivalence/decode/regenerated_raw.v` | `ec920772bf2fa88a` (first 16) | 48,250 lines | Decoded from the rebuilt bitstream. |
| Repaired mapped netlist (Yosys netlist JSON) | `supplementary_clean_verification/synthesis_fit_timing_2026-11-06/runs/synthesize_repaired_02/mapped_clean.json` | `b9274fdac6870c7b04b67d73ae0206dab97d7f1d9da22793071aef823658e2d7` | 3,963,320 bytes | Listed in the existing `REPOSITORY_MANIFEST.json`. Top-level keys are `creator` and `modules`, and it includes the protocol DUT module. No separate Verilog-format mapped netlist is claimed. The formal-proof result JSONs under `evidence/core_evidence/verification/baseline_equivalence/formal/baseline_mapped/` are separate records, not the netlist. |
| Separate clean AES reference | `evidence/core_evidence/verification/clean_aes_reference/sources/designs/aes_128/` (`aes_128.v`, `round.v`, `table.v`) + `sources/testbenches/tb_aes_128.v` | — | present | A different design from the CSAW baseline. Not analyzed here. |

Notes on the inventory:
- Sizes are in lines for the RTL files and in bytes for the netlist JSON.
- The netlist path, size, hash, manifest listing and JSON structure come from the supplied verified facts. This revision did not recompute them.
- The original audit confirmed that the baseline, repaired and regenerated RTL are distinct by hash. The mapped netlist has a different hash and a different format (Yosys JSON rather than Verilog source).
- Distinctness supports the repository's 'keep these distinct' framing. It establishes nothing about any functional relationship between the artifacts, which was not examined.

## 2. Repository integrity (earlier reviewer-reported result, original scope)
- `REPOSITORY_MANIFEST.json`: 842 entries, each `{path, bytes, sha256}`.
- Independent re-hash of a random 20-file sample, as reported by the original audit: **20/20 match, 0 mismatch, 0 missing.**
- Coverage, as reported by the original audit: every non-`.git` file then on disk was listed except the manifest itself (843 on disk vs 842 listed; `in_manifest_not_on_disk = 0`).
- **Scope correction:** the audit files were added after the original 842-entry manifest and the original 843-file inventory. The sample and coverage results above describe that earlier state only.
- The current, expanded working tree is not claimed to be fully manifested.
- This revision did not rerun the sample or the coverage check.
- Caveat: this is file-integrity evidence only. It does not show the correctness of any design or test.

## 3. Claim-support audit

### Claims with saved machine backing
- **Clean AES reference, 'five supplied tests pass':** backed by `evidence/core_evidence/verification/clean_aes_reference/runs/20261110T123203.879963Z/RESULT.json` (`pass_count=5, fail_count=0, pass=true`), with `commands.json` and `environment.json`.
- **Known-answer 24/24:** `evidence/core_evidence/verification/baseline_equivalence/records/*.json` reference the 24-count results (the value 24 recurs throughout those JSONs).
- **Detector study (best-documented component):** `evidence/defensive_appendix/REPORT.txt` reports:
  - 23/23 designs scored (14 infected, 9 clean) and 92 predictions.
  - Ensemble detected 9/14 infected designs and missed 5.
  - 7/9 clean designs were false-flagged.
  - Supporting files: `dataset-manifest.json` and `frozen-model-manifest.json`.
  - The report is explicitly self-critical: 'not a security guarantee', correlated toy variants, no additional positives beyond HT1.

### Claims whose counts rest on narrative in this package (flagged)
No raw per-check simulation, assertion, solver or synthesis run logs are packaged for the counts below. They are documented in prose and cannot be independently re-derived from this repository. Historical reports are not fresh independent reruns.

- **Readiness repair '1,122/1,122 pass; baseline 14 failures':**
  - Location: `supplementary_clean_verification/result_readiness_repair_2026-11-06/`.
  - Bundle contents: `AI_RECORD.md`, `OUTPUT_HASHES.json`, `REPORT.md` and the derivative RTL.
  - The '1122' token in the `.v` file is a source identifier, not a result.
- **ROM disabled-read '67,584 assertions / 6,144 scenarios':**
  - Location: `supplementary_clean_verification/rom_disabled_read_coverage_2026-11-06/`.
  - Bundle contents: `AI_RECORD.md`, `OUTPUT_HASHES.json`, `REPORT.md`.
- **Synthesis/fit/timing figures (1,443 / 2,920 LCs; Fmax 35.82 / 29.25 MHz; 1 MHz route pass):**
  - Location: `supplementary_clean_verification/synthesis_fit_timing_2026-11-06/REPORT.md`.
  - The bundle also contains the repaired mapped netlist JSON listed in Section 1.
  - Raw synthesis/fit/timing run logs are not packaged.
  - The netlist's presence does not by itself re-derive the reported LC, Fmax or route figures, and no synthesis was rerun.
- **Two-transaction modes 00/01/10/11:**
  - Location: `supplementary_clean_verification/two_transaction_equivalence_2026-11-07/`.
  - It includes four records: `trace_audit.json`, `completion_review.json`, `result_matrix.json` and `final_seal_checks.json`.
  - This makes it better supported than the readiness and ROM bundles.
  - It remains a selected record subset, not the full proof dependencies or raw solver logs.

This matches the supplementary README's own disclaimer that it ships 'selected reports ... not a standalone complete experiment installation.' For submission purposes, these counts currently rest on reports plus a hash manifest, and the underlying raw outputs are not in the package.

### Failures / limits correctly retained (good practice, preserved)
- Immediate first-BUSY-low read: 8/8 known-answer failures retained (documented in `evidence/core_evidence/TECHNICAL_BRIEF.txt` and `.../baseline_equivalence/.../REPORT.txt`).
- Baseline 14 readiness failures retained.
- Detector misses (5) and false positives (7) retained and emphasized.
- Formal: seven unavailable internal monitors untested; the unrestricted longer proof times out.
- Synthesis: board PCF, pins and external timing unverified; explicit 'do not program the auto-pin binary.'
- Detector extraction failed on `SBRAM404K`; classifications are on a coarse fallback graph that omits RAM internals.

## 4. Model-provenance note
- `publication/claude-review/opus55-readiness-review-stdout.json`:
  - `modelUsage` contains `claude-opus-5-5`; `is_error` is false.
  - The 'opus55' label is substantiated.
- `publication/claude-review/readiness-review-stdout.json`:
  - `modelUsage` contains both `claude-opus-4-8` and `claude-haiku-4-5-20251001`; `is_error` is false.
  - This review was not Haiku-only.
- The older archived one-shot CLI review under `core_evidence/verification/...` is a separate record. Per `LATEST_STATUS.md`, it recorded `claude-opus-4-8` and `claude-haiku-4-5`.
- `LATEST_STATUS.md`'s 'Opus 5.5 availability is not verified' refers to that archived review's own actions, not to the opus55 review.
- Recommend the docs disambiguate which review used which models, so the statements are not read as contradictory.

## 5. Submission checklist vs preserved qualifier
Preserved qualifier: `evidence/core_evidence/course_instructions/original_qualifier_README.md`.

| Deliverable | Class | Status |
|---|---|---|
| AI-generated Trojan-modified RTL | Mandatory | ABSENT (baseline/repair are not this artifact) |
| Demonstration/exploit testbench | Mandatory | ABSENT |
| Technical brief | Mandatory | PARTIAL — completed-work sections present; the required proposed explanation of the recovered encryption system and the modification/demonstration sections are absent |
| Comprehensive GenAI transcripts | Mandatory | PARTIAL — bounded exports; documented gaps (encrypted bodies, truncation, compaction boundaries, unmapped chats, post-cutoff packaging) |
| Key recovery | Bonus | Optional; correctly NOT listed as a mandatory missing requirement |
| Physical-board testing | Not required | Preserved qualifier is simulation-only; any later course change needs reconfirmation |
| Defensive detector study as alternative | Pending | Needs explicit professor approval; silence is not approval |
| Course destination + authoritative deadline | Unconfirmed | A GitHub push is not a submission receipt |

The repository's existing `SUBMISSION_GAPS.md` already states all of the above accurately, and this audit confirms it matches the preserved qualifier.

Suggested tightening: have `evidence/REQUIREMENTS_STATUS.csv` name the absent 'proposed cipher explanation' as the specific missing technical-brief sub-item, matching `SUBMISSION_GAPS.md`.

This revision records no new course approval, no submission and no completed original deliverables.

## 6. Recommended documentation corrections
1. For each narrative-only supplementary count (1,122/1,122; 67,584; synthesis figures), either include the raw run logs or add an inline pointer to where the raw evidence lives. State what each packaged bundle actually holds.
2. State that the repaired mapped netlist is packaged as a Yosys netlist JSON at `supplementary_clean_verification/synthesis_fit_timing_2026-11-06/runs/synthesize_repaired_02/mapped_clean.json` and is listed in the manifest. State that no Verilog-format mapped netlist is included, and that the formal-proof JSONs are separate records.
3. Disambiguate the reviews by model:
   - opus55 review: `claude-opus-5-5`.
   - readiness review: `claude-opus-4-8` + `claude-haiku-4-5-20251001`.
   - older archived review: separate record, per `LATEST_STATUS.md`.
4. Add a one-line note that `baseline.v` is duplicated byte-identically in two locations, so it is not mistaken for two designs.
5. Keep the existing 'key recovery = bonus' framing.
6. Describe the two-transaction bundle as a selected four-record subset, not full proof dependencies or raw solver logs.
7. Note that the manifest predates the audit files, or regenerate it through the normal project process. This revision does not do so.

## Closeout

### Original audit closeout (historical, as reported by the original session)
- **Files changed:** 2 added at repo root (`AUDIT_FINDINGS.md`, `AUDIT_SESSION_RECORD.md`). No evidence modified, no scripts executed, no commits, no pushes, no submission.
- **Checks actually run:**
  - Independent sha256 re-hash of 20 manifest entries (20/20).
  - Manifest-vs-disk coverage diff.
  - Artifact hash/line-count inventory.
  - Grep-based claim tracing into saved result files.
  - Model-provenance read of the review stdout JSONs.
  - No simulation, detector inference, formal solving or archived-script execution.

### Corrected results (this revision)
- **Integrity and inventory:** integrity was intact for the earlier 842-entry manifest and 843-file inventory. Designs are distinct by hash.
- **Machine-backed claims:** the AES, detector and 24-count known-answer claims have machine backing.
- **Narrative-only claims:** the readiness, ROM and synthesis count claims rest on reports, without raw run logs.
- **Two-transaction:** the bundle has a selected four-record subset.
- **Mapped netlist:** it is present and manifested as a Yosys netlist JSON. This supersedes the original statement that the mapped-netlist file was absent.
- **Model provenance:** corrected as described in Section 4.

### Unresolved limitations
- Raw logs for the readiness, ROM and synthesis counts are not in the package.
- The two-transaction raw solver logs and full proof dependencies are not in the package.
- Historical reports are not fresh independent reruns.
- The current expanded tree is not shown to be fully manifested.
- GenAI-transcript completeness is not established.
- The course deadline and destination are unconfirmed.

### Still missing under the original assignment (unchanged)
- The two mandatory artifacts: Trojan-modified RTL and the demonstration testbench.
- The technical brief's proposed-cipher-explanation section.
- Comprehensive GenAI transcripts.
- Key recovery remains a bonus, not a mandatory gap.

### Revision closeout
- **Files changed:** this tool-disabled response returns corrected text only. Applying it is left to Claude Code.
- **Checks run:** none. No hashing, execution, simulation, synthesis, formal solving or reruns.
- **Excluded work:** no cipher or design-logic analysis, RTL repair, hardware modification or attack content.
