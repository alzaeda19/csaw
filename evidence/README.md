# CSAW partial submission / instructor review

Prepared November 11, 2026. **Not submitted or sent. Alternative scope approval is pending**, as reported by the student.

This package organizes completed recovery, verification and defensive detector work for review. It does **not** establish completion of the original CSAW assignment.

**Two mandatory artifacts remain absent:** the AI-generated Trojan-modified RTL and its demonstration testbench. Available AI records have documented gaps. The included technical brief covers completed work but does not establish every original brief requirement, including a complete explanation of the recovered cipher or the missing modification/demonstration.

## Reading order

1. [Current submission note](SUBMISSION_NOTE.txt) and [current requirement status](REQUIREMENTS_STATUS.csv).
2. [Current technical summary](TECHNICAL_SUMMARY.md), including known failures and detector limitations.
3. [Original technical brief](core_evidence/TECHNICAL_BRIEF.txt) and [original evidence guide](core_evidence/README_START_HERE.txt).
4. [Completed clean/infected detector study](defensive_appendix/REPORT.txt).
5. [AI record index and remaining gaps](AI_RECORD_INDEX.md).
6. [Unsent professor follow-up](correspondence/UNSENT_PROFESSOR_FOLLOWUP.txt).

## Included work

- Recovered baseline RTL and a regenerated bitstream, with qualified digital-model equivalence evidence.
- Original-host known-answer results and retained immediate-read failures.
- Separate clean AES reference verification: five supplied tests passed.
- Four-detector evaluations of the recovered baseline and clean AES, with heuristic-graph limitations.
- A distinct defensive appendix evaluating all four detectors on 14 package-labeled infected and nine clean designs. The combined rule detected nine infected designs, missed five and falsely flagged seven clean designs.
- Available authentic AI records, command evidence, errors and documented transcript limits.

The original qualifier instructions are preserved under [core_evidence/course_instructions](core_evidence/course_instructions/original_qualifier_README.md). Their required modified-design and exploit-testbench deliverables remain unmet. The appendix is a proposed alternative, not an approved replacement.

## Packaging and provenance

`core_evidence/` is an unchanged copy of the November 10 partial package. `defensive_appendix/` is an unchanged copy of the finalized detector-study bundle. Their own reports, scripts, correspondence, logs and manifests retain their original bytes. The older professor message inside the core package is a historical unsent draft; use the current follow-up above for the present status.

`SOURCE_COPY_RECEIPTS.json` maps every copied file to its source and hash. `MANIFEST.json` describes this combined package. Original embedded manifests may describe larger source experiments; this combined manifest is authoritative for what is actually included.

These are portable evidence subsets, not complete standalone EDA/detector installations. Some historical scripts refer to absolute source paths or shared environments. Large solver intermediates, full graphs, detector weights and the toy RTL inputs are not all included. Read the individual reproduction/limitation notes before attempting a rerun. No script runs automatically when the archive is opened.

Paper 5 is a separate assignment and is not included here. No existing CSAW source, old evidence or repository was changed in preparing this package. No prior test, detector inference, hardware operation or Trojan-generation workflow was rerun.

## Submission-stage status

The local package is prepared for a clearly labeled partial submission or instructor review. It has not been uploaded, emailed, accepted or graded. No reply approving the proposed scope has been recorded.

The orchestrator reports the previously user-recorded CSAW deadline as **November 13, 2026, at 3 PM Eastern**. This packaging task did not obtain a new instructor confirmation or verify the current course upload destination. The original challenge form link is retained only as historical documentation. **Paper 5's November 16 deadline is separate.**

If an upload is made while the scope remains unresolved, include the current note identifying it as partial. Save the resulting submission confirmation separately; package preparation alone is not submission.

