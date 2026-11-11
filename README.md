# CSAW 2026 — partial evidence and defensive evaluation

This private repository collects completed baseline recovery, ordinary verification, defensive detector evaluation and available AI records. **The original assignment is not complete.** The proposed defensive alternative still requires the professor's approval. A GitHub push is not a course submission or acceptance.

Paper 5 is separate and is not included. No published challenge solutions were used for this publication work. Existing source projects and the sealed November 11 review package were preserved.

## Start here

- [Exact submission gaps](SUBMISSION_GAPS.md).
- [Technical summary and limitations](evidence/TECHNICAL_SUMMARY.md).
- [Recovered baseline and ordinary verification](evidence/core_evidence/TECHNICAL_BRIEF.txt).
- [Additional clean-repair verification](supplementary_clean_verification/README.md), including records omitted from the earlier package.
- [Four-detector study on existing supplied designs](evidence/defensive_appendix/REPORT.txt).
- [Available AI records and known gaps](evidence/AI_RECORD_INDEX.md).
- [Original qualifier requirements](evidence/core_evidence/course_instructions/original_qualifier_README.md).
- [Publication provenance](publication/SOURCE_COPY_RECEIPT.json) and [upload audit](publication/CSAW_UPLOAD_AUDIT.md).
- [Actual Claude Opus 5.5 readiness review](publication/claude-review/REVIEW_SUMMARY.md), with prompts, raw output, errors and refinements.
- [Chat coordination and snapshot boundaries](publication/CHAT_COORDINATION.md).

## Completed evidence

- Recovered baseline RTL and regenerated bitstream, with conditional digital-model equivalence and recorded build assumptions.
- Original-host known-answer checks: 24/24 pass per model. The archived first-BUSY-low immediate-read checks fail 8/8 per model; those failures are retained.
- Separate professor-supplied clean AES reference: five supplied tests pass. This is a different design from the recovered CSAW baseline.
- Earlier four-detector runs classify both clean references CLEAN with documented heuristic/fallback graph limitations.
- The later study scores 23 existing supplied designs (14 labeled infected, nine clean): 92 individual model predictions. The any-positive combination detects nine infected designs, misses five, and falsely flags seven clean designs. It detects no more infected cases than HT1 and increases false alarms. This is not a security guarantee or an established held-out benchmark.
- Genuine bounded AI exports and command records, including errors and refinements. Project-wide transcript completeness is not established.

## Check this repository

With Python 3.9 or later, run from this directory:

```sh
python3 tools/verify_evidence.py
```

This checks file hashes without running archived code, hardware simulation, detector inference or generation. Success establishes file integrity only.

Historical scripts/logs preserve original paths. This is an evidence archive, not a complete portable EDA/detector installation: some solver artifacts, weights, graphs and dataset inputs are absent. Individual reports document rerun requirements. No automated GitHub workflow is included.

## Publication and deadline notes

The `evidence/` records retain their original contents. Two disposable generated files (compiled AES simulation and Python bytecode) are omitted and listed in the copy receipt. Historical embedded manifests may describe these or a larger experiment; `REPOSITORY_MANIFEST.json` describes this repository's files.

The user's latest instruction reports **30 hours remaining**. This supersedes the older planning estimate for urgency; the exact course deadline/time and upload destination have not been independently reconfirmed. The older November 13 date remains in historical records, not as a newly verified deadline. Paper 5's November 16 deadline does not apply here.

Course materials and upstream sources retain their ownership and notices. No blanket license is granted. See [third-party notices](THIRD_PARTY_NOTICES.md).
