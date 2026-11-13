# Submission requirements wording review

Scope: four snapshot documents; artifact presence and test outcomes are reported, not independently inspected or rerun.

## Mandatory deliverables

The qualifier requires a ZIP containing AI-generated modified RTL, an exploit testbench, comprehensive generation prompts/responses, and a technical brief covering reverse engineering, AI methods/models/frameworks, trigger/payload, stealth methods, exploitation details sufficient for later hardware use, and a **proposed** encryption explanation. Missing generation logs carry a disqualification warning; human-written hardware is prohibited. (`sources/submission/evidence/original_qualifier_README.md:18–40`)

Current documents report RTL, testbench, brief, saved results and archive present. Historical “missing RTL/testbench” or “not uploaded” statements are superseded and remain dated evidence. Saved finite tests support the stated cases, not universal behavior. (`sources/README.md:5,21–30,48`; `sources/submission/CURRENT_GUIDE.md:3,11`)

## Remaining completeness and delivery limits

- **Relevant AI-record completeness remains unresolved:** 12 encrypted reviewer bodies—nine requests and three steering messages—remain unreadable. Parent/child copies represent the same 12 exchanges. Two outputs retain 1,546- and 2,535-token truncations; some older histories are unavailable. Recovered code cannot replace missing prompts. All generation-relevant prompts/responses are required; unrelated histories and hidden reasoning are not. The documents cannot establish complete coverage or that every unavailable item is outside scope. (`sources/submission/CURRENT_GUIDE.md:23–26,32–34,39`; `sources/SUBMISSION_GAPS.md:18`)
- **Publication and acceptance remain distinct:** the original competition README names a Google form, while the user specified GitHub for this course. Follow that course instruction; do not silently introduce a separate contest-form upload or a new approval requirement. Public availability is verifiable, but instructor review/acceptance is not established by publication alone. (`sources/submission/evidence/original_qualifier_README.md:27,42–52`; `sources/README.md:50`)

## Grading strength versus additional mandatory work

The expanded architecture account is a proposed encryption explanation; algorithm identity, table meanings, round equations, key handling and cryptographic strength remain unestablished. The original asks for a proposal, not a full cipher proof. (`sources/submission/CURRENT_GUIDE.md:15–19,35`; `sources/submission/evidence/original_qualifier_README.md:40`)

Perfect normal operation is a stated objective; stealth, resource overhead, automation and simulation quality affect grading. Finite evidence does not establish the strongest outcomes. No mandatory formal/universal proof or synthesis report is specified. Trigger disclosure is required; predictable corruption is allowed. (`sources/submission/evidence/original_qualifier_README.md:16,21–22,37,62–92`; `sources/SUBMISSION_GAPS.md:14`)

The qualifier is simulation-only; later-hardware exploit detail does not require board execution. Key recovery is bonus work. Mandatory board programming, physical timing or key-recovery tasks should not be added. (`sources/submission/evidence/original_qualifier_README.md:8,39,94–95`)

Current readiness language is appropriately qualified. Remaining record-completeness and delivery uncertainties prevent an unqualified “fully compliant/accepted submission” claim.
