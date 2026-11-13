# Requirement-interpretation review

**No material correction is needed to the current conclusion: stealth is not established.** The two permitted documents contain no verified evidence that overturns the frozen-design evaluation. This is a document interpretation review, not a new experiment or independent revalidation of every reported result.

The reviewed current report is `submission/addenda/2026-11-13-detection-evaluation/README.md`, SHA-256 `c7ac11427ba60c818a0060a3ffc4d056d121fcb267c55f1018019df8f6c66e54`. The preserved original qualifier is `evidence/core_evidence/course_instructions/original_qualifier_README.md`, SHA-256 `72833c7880d7c4ea2af74bdeff9c001716ea087bca609f8d53699546b6ff4e08`. Exact full source paths, byte-identical copies and line excerpts are supplied in this bundle.

## Distinctions to preserve

1. **Stealth is an objective and a graded property, not a requirement of universal undetectability.** Qualifier line 16 requires a stealthy modification with normal behavior preserved and activation under specific hidden circumstances. The Trojan Quality rubric at lines 64–69 grades stealth, trigger specificity, payload quality and overhead. It supplies no mandated detector, numerical stealth threshold, requirement to defeat source review/formal analysis, or requirement that all four supplied checkpoints return CLEAN. Detection under a strong white-box check is test-specific evidence; it is not by itself a rules-defined automatic disqualification or proof about every detection setting. Conversely, the rubric's lack of a threshold is not permission to claim stealth without supporting evidence. The report's wording “not established” is appropriate.

2. **Disclosure to the grader is required.** Qualifier lines 36–39 require the trigger/payload, stealth methods and exploit details. Visible documentation of the trigger does not itself violate the assignment. The required evidence must distinguish ordinary operation from the exceptional behavior, rather than hide the design from the evaluator. This does not alter the measured source/formal detection findings.

3. **Working behavior and the observed model labels address different questions.** The current report's lines 7–19 record useful positive results: a working change, source review, a formal counterexample and finite representation-validation simulations. Its lines 21–30 explain why raw fallback and flat graph-join defects prevent whole-design conclusions from classifier labels. Functional preservation of the tested HDL transformations does not validate the downstream graph. No existing result in this report supports replacing “stealth not established” with “stealth established.” It also does not establish a universal inability to be stealthy.

4. **Framework availability does not satisfy a requirement.** The preserved qualifier asks the brief to describe any supporting AI framework used (line 35); it does not mandate TrojanGYM or a specific detector. This statement is limited to this original qualifier and does not rule out separate instructor requirements outside the permitted review scope. Tool names, agent counts and unsupported descriptive adjectives are not experiments.

5. **Do not add optional work to the mandatory checklist.** The qualifier is entirely simulation-based (line 8). It requires enough written detail for future hardware exploitation (line 39), not an executed board test. Key recovery is explicitly a bonus (lines 94–95). Predictable ciphertext corruption is an allowed payload example (line 22). Negligible overhead, a sophisticated payload and one-click generation-to-simulation automation are higher rubric tiers, not additional separately enumerated artifact categories. The report correctly preserves these distinctions.

6. **Keep provenance limits visible without inventing a grading outcome.** Comprehensive generation prompts/responses are mandatory, with strict missing-log language at line 32. The report discloses the twelve unavailable reviewer instructions and remaining tool-output gap at line 48. New chats cannot replace unavailable originals. The instructor must decide how these particular gaps affect compliance; neither guaranteed acceptance nor automatic disqualification is established by this review.

## Optional precision improvement

Where the report says data/mode are “unconstrained,” the most precise short form is **“arbitrary transaction words and transaction-stable modes under the fixed legal protocol schedule.”** This keeps the existing formal result's scope clear. It changes no experimental finding or overall conclusion. Likewise, avoid converting “detected by these checks” into an assertion that the rules demand resistance to every such check.

## Provenance and scope

Only the current local report and preserved qualifier were read as substantive sources. No shared Claude chat, published challenge solution, excluded implementation, detector source, new experiment or earlier contaminated material was consulted for this assessment. The coordinating chat's descriptions of the shared chats were not independently verified here and are not used as new technical evidence. No design/detector modification, generation, evasion work, agent launch or repository write occurred.

The first attempt used a guessed `REPORT.md` filename that did not exist. A directory listing identified the actual `README.md`; its complete contents were then read. The actual failed read and correction are recorded in `ERRORS.json`. Authentic current visible prompt/reply/tool records are exported separately with a cutoff and explicit exclusions; no missing dialogue is synthesized. Copies and hashes are sealed in `MANIFEST.json`.

The current AI snapshot retains 12 visible records with 79 verified scalar fields, covering native lines 2516–2556 through 2026-11-13 06:24:21.118 UTC. It indexes 29 excluded internal/context/event records. Final sealing and handoff messages follow that snapshot. Both substantive source files and their copies were rechecked unchanged; the qualifier hash matches the previously preserved original identity.
