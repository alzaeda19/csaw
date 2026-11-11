# Claude review of CSAW submission readiness

November 11, 2026. This is a new document review for preparation of the private `csaw` repository. It is not a security certificate, an instructor acceptance decision, a complete conversation export, or a rerun of the saved experiments.

## Actual model and result

- The requested `claude-opus-5-5` review succeeded using an isolated official Claude Code 2.1.322 binary. The raw result reports `modelUsage` containing `claude-opus-5-5`, `is_error: false`, and exit code 0. The CLI returned a cost of $0.153052.
- An earlier supported-alias review also succeeded using the unchanged global Claude Code 2.1.187. Its metadata reports `claude-opus-4-8` and auxiliary `claude-haiku-4-5-20251001`, with returned cost $0.208463. It was not represented as Opus 5.5.
- Both consultations had tools disabled, no MCP servers, no customizations or session persistence, and explicitly supplied document context only. No project code or tests were executed by Claude. The global CLI was not updated.
- The Opus 5.5 conclusion is **partial submission/instructor review only**. The original assignment is not established complete.

## Exact remaining requirements supported by the records

1. The required AI-generated modified RTL artifact is absent.
2. The required demonstration testbench is absent.
3. Comprehensive AI prompt/response coverage is not established. Existing exports have explicit encrypted, truncated, unmapped and post-cutoff gaps. Overlapping export counts must not be added into a claimed complete total.
4. The technical brief does not satisfy all required topics. A follow-up read of `core_evidence/TECHNICAL_BRIEF.txt` confirms that it discusses recovery, equivalence, tests and detectors, but supplies no proposed explanation of the recovered encryption algorithm. The missing modification/demonstration sections remain missing. Model/framework details should be linked to actual recorded interactions, not invented.
5. Professor approval of the proposed defensive alternative is pending. GitHub publication itself is not confirmation of course submission or acceptance. The current course destination/required format must be verified, and an actual submission receipt retained when submitted.

The user now reports approximately 30 hours remaining. Treat that as the current planning constraint. The old November 13, 3 PM Eastern date in frozen records is historical and not freshly confirmed. This review does not establish an exact revised deadline.

Independent key recovery is a bonus under the preserved original instructions. Physical-board testing is not required by that original simulation-only phase. Neither should be mislabeled a missing mandatory item without later instructor evidence.

## Qualifications to retain

- The 24/24 original-host known-answer checks and 8/8 first-BUSY-low failures describe different retained schedules. Model agreement does not resolve those failures or prove universal correctness.
- Equivalence is conditional on the stated digital primitive models and state relation; it is not an independent cipher or board proof.
- The separate clean AES reference is a different design.
- Earlier clean classifications use heuristic/fallback graphs and do not prove absence of a Trojan.
- On the 23 supplied labeled examples the any-positive combination detects 9 of 14 infected designs and falsely flags 7 of 9 clean controls. This has no detection-count advantage over HT1's 9 of 14 and has more false alarms than HT1's 5 of 9. Labels, related families and unknown training overlap limit interpretation.
- File hashes and CRC checks establish byte integrity, not scientific correctness or requirement completion. Portable evidence subsets are not full runnable environments.

## Reviewer findings adjudicated

Opus 5.5 reviewed four supplied current documents, not the complete archive, source, logs, native chat history or publication candidates. It explicitly disclosed this. The parent is independently inspecting upload contents.

- Its concern that a proposed cipher explanation may be unclear was resolved by reading the actual brief: no such explanation is supplied there. Use **proposed explanation**, matching the rubric, rather than requiring an exhaustive proof.
- Its phrase “No professor approval exists” should mean **no approval is recorded in the available evidence/user report**, not a global search of all correspondence.
- The original README already limits its manifest authority to “what is actually included.” Keep that inventory-only meaning; no correctness inference is needed.
- “No existing repository was changed” in the frozen package is explicitly about its prior preparation step. A new GitHub wrapper should distinguish that historical statement from the newly authorized repository push.
- The difference between 741 unchanged copied evidence files and 753 archive files is not a new test discrepancy. The package's combined manifest inventories the additional authored records. Preserve those provenance distinctions.
- The recommendation to send a professor follow-up is advice only. This review did not send a message or authorize sending one.

## Publication recommendations

Keep `csaw` private, keep Paper 5 separate, and complete the parent's credential/private-content/redistribution review before upload. Include truthful status and provenance; do not insert fabricated logs or placeholder code represented as completed work. Do not enable workflows that automatically execute historical scripts. Preserve byte integrity or document any sanitization and regenerate the repository inventory accordingly. Do not upload the isolated CLI binaries, installed dependencies, or package-manager cache with the project evidence.

## Evidence files

The exact requested-model prompt, command, raw JSON and stderr are retained under `opus55-readiness-review-*`; the readable result is `opus55-readiness-review.md`. Earlier attempts and refinements are listed in `ERRORS_AND_REFINEMENTS.md`. `REVIEW_MANIFEST.json` inventories the small review-evidence files, excluding the isolated installed CLI directory. This authored summary does not replace the raw outputs or claim to be a verbatim native chat export.

The official package identity was checked against Anthropic's [Claude Code README](https://github.com/anthropics/claude-code/blob/main/README.md); the isolated install is pinned to 2.1.322 and its lockfile is retained.
