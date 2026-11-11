# CSAW Partial-Submission Readiness Review

This review covers only the four supplied documents. I did not see the source, full logs, SUBMISSION_NOTE.txt, SUBMISSION_STATUS.json, VALIDATION.json, PREPARATION_RECORD.md, or the unsent follow-up, so I could not check them. This is a single reviewer's document check. It is not a multi-model council, a security certification, or a prediction of whether the instructor will accept the work.

## 1. Safe verdict

- **Ready for:** a clearly labeled partial submission or instructor review, once the parent agent's credential and scope check passes.
- **Not ready for:** a claim that the original CSAW qualifier is complete. Two mandatory artifacts are missing and two more mandatory requirements are only partly met.
- **Packaging integrity:** the reported receipt, CRC and manifest checks support that the files are intact. They do not show that the content is correct, complete or acceptable to the instructor.

## 2. Remaining gaps

**A. Mandatory artifacts that are missing**
1. Trojan-modified RTL: absent. Only a placeholder (`UNFINISHED_REQUIRED_MODIFICATION.txt`) is included.
2. Demonstration testbench: absent. Only a placeholder is included.

**B. Mandatory requirements that are only partly met**
3. **AI prompts/responses.** There are bounded exports of 2,271 and 236 records. They have encrypted, truncated, unmapped and post-cutoff gaps. The current packaging chat is described in an authored record, not exported as a native transcript. Because the original rules say missing logs risk disqualification, this is a direct risk, not a minor gap.
4. **Technical brief.** The brief has no section on the modification or demonstration. The original asks for a *proposed* explanation of the encryption system. The docs only say a "full recovered-cipher explanation" is not established. They do not say whether a clearly labeled proposed explanation exists. The supplied docs also do not show whether the brief covers AI model/framework methodology or model provenance.

**C. Known evidence and normal-operation issues**
- Immediate reads at the first BUSY-low fail 8/8 per model. The cause is not explained.
- The 24/24 known-answer passes and the baseline equivalence both depend on the stated digital models and state relation. Neither is board validation or independent proof of the cipher algorithm.
- The detector "CLEAN" results used heuristic or fallback graph extraction. They are not proof that no Trojan is present.
- Defensive appendix limits:
  - Labels come from directory names, not activated behavior.
  - Training overlap with the test designs is unknown.
  - The dataset is small and dominated by related design families.
  - The combined rule has a 77.8% false-alarm rate.
- I checked the table arithmetic and it is internally consistent: 92 predictions, 9/14 = 64.3%, 7/9 = 77.8%, and the row sums are correct.

**D. Approval and administrative items**
- No professor approval of the alternative scope exists. Silence is not approval.
- The current course submission destination and due time are not verified. A private GitHub repo may not be an accepted submission channel. The original form link is historical only.
- **Deadline conflict:** the student now reports about 30 hours remaining. From today (Nov 11), 30 hours ends around Nov 12 or early Nov 13. The recorded date of Nov 13 at 3 PM ET is later than that. Plan for the earlier time until the instructor confirms.
- The unsent follow-up has not been sent. Given the timeline, sending it soon would be prudent.
- Nothing has been uploaded or sent yet. A submission confirmation must be saved separately once that happens.

**E. Optional items**
- Independent key recovery (a bonus): not established, and correctly not claimed.
- Physical-board testing: not required for the original simulation-only phase.

## 3. Misleading claims or contradictions to correct

1. **Deadline wording.** The README bolds "November 13, 2026, at 3 PM Eastern," which can read as current fact. It should be relabeled as a historical, unconfirmed date, with a note that the student currently reports roughly 30 hours remaining.
2. **"Two mandatory artifacts remain absent."** This is accurate but incomplete. It should also say that the AI-log and brief requirements are only partly met, so readers do not assume only two gaps remain.
3. **"Authentic" AI records** (README and summary). This is the package's own claim; this review did not verify it. Wording such as "exported from native sources, as recorded in the recovery index" would be more accurate.
4. **"No existing ... repository was changed."** This is true for packaging, but uploading to `csaw` will change a repository. The wording should make clear that it describes the preparation step only.
5. **"This combined manifest is authoritative."** It should be limited to "authoritative for the file inventory," not correctness.
6. **741 copied files versus 753 ZIP entries.** The roughly 12 non-copied items (the new top-level documents, and possibly directory entries) are not covered by the byte-for-byte receipts. They should be listed explicitly, since they contain the current status claims.
7. **CSV formatting.** Missing spaces ("fails8/8", "and9 clean; detected9 missed5", "November13,2026,3PM"). This is cosmetic but looks careless in a reviewed document.
8. **Encryption-explanation status.** It is unclear whether a proposed explanation is absent or present but unconfirmed. The status should be stated plainly either way, without adding new technical claims.

## 4. Publication boundaries and reproducibility caveats

**What to publish**
- Keep the repository private. Give access only to named course staff, and only after the parent agent's credential and private-content review passes.
- Exclude Paper 5 entirely, including chats, logs and paths.
- Check whether you are allowed to redistribute third-party material before including it. This covers the professor-supplied clean AES reference, the 23 benchmark designs (including the 14 labeled infected), and any detector components. If unsure, cite them instead of copying them.
- Do not add placeholder or invented modified-design or testbench files, and do not add AI logs that were reconstructed after the fact.
- Do not enable CI or Actions that run included scripts.
- Mark the historical professor draft inside `core_evidence/` clearly so nobody mistakes it for sent correspondence.

**Preserving the evidence**
- Git line-ending normalization or other filters can change file bytes and break the hash receipts. Store the ZIP unchanged (for example as a release asset or binary-tracked file) so the receipts remain checkable, and tag the commit.
- Check GitHub's file-size limits (100 MB per file) for the bitstream and any large files before pushing.

**Reproducibility**
- These are portable evidence subsets, not runnable environments. Some scripts use absolute paths and shared environments.
- Solver intermediates, full graphs, detector weights and some toy RTL inputs are omitted.
- No test, inference or hardware step was rerun for this package, and I ran nothing.

## 5. Plain-language status

> Your CSAW package is organized and its files check out as intact. It is ready to send **only as a clearly labeled partial submission or request for review**. It does **not** complete the original assignment. The Trojan-modified design and its demonstration testbench are missing, the AI chat records are incomplete, and the technical brief is only partly finished. Your professor has not approved the alternative defensive scope. Your remaining time (about 30 hours) is earlier than the Nov 13 date in the documents, so treat the earlier time as the real deadline and confirm with your instructor. Also confirm whether a private GitHub repo is an accepted way to submit. Send the follow-up message soon. After you submit, save the confirmation. Keep Paper 5 completely separate.
