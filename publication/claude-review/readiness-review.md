# CSAW Partial-Submission Readiness Review

Scope note: I reviewed only the supplied documents. I ran nothing, audited no source or logs, recovered no keys, and I am not a security certificate or a multi-model council. The byte-for-byte/CRC/manifest results you reference prove **packaging integrity only**; current source and full logs were not provided to me and are **not** independently audited here.

---

## 1. Safe verdict

**Partial instructor review — NOT original-assignment completion.**

The documents are internally consistent on this: two mandatory original deliverables are absent, the technical brief does not establish every original requirement, and the proposed defensive scope has no recorded professor approval. This package is suitable only as a clearly labeled partial/instructor-review submission. It does not satisfy the original CSAW qualifier.

---

## 2. Remaining submission gaps

**A. Missing mandatory artifacts (block original completion):**
- **Trojan-modified RTL** — absent/unfinished (placeholder file only). Not substitutable by the recovered baseline or detector results.
- **Exploit demonstration testbench** — absent/unfinished. Ordinary/known-answer benches do not demonstrate the required behavior.
- **Complete recovered-cipher explanation in the technical brief** — not established. *Caution:* the original README requires a *proposed* explanation, while the docs describe a *complete* explanation as unmet — confirm whether at least the required **proposed** explanation is present so you neither over- nor under-state this gap.
- **Comprehensive prompts/responses or chat links** — bounded records exist, but project-wide completeness is **unproven** (encrypted, truncated, unmapped, post-cutoff gaps). The original README warns missing logs risk disqualification; treat completeness as an open mandatory risk, not a satisfied item.

**B. Known evidence / normal-operation issues (disclosed, not failures to hide):**
- Immediate first-BUSY-low read **fails 8/8** known-answer cases per model (retained failure); 24/24 original-host cases pass per model. Two models agreeing does not remove the failure.
- Baseline/bitstream equivalence is **conditional** on stated digital-primitive models and a state relation — not board validation or cipher-algorithm proof.
- Clean-AES reference passed 5 supplied tests but is a **different design**; not equivalence to the CSAW baseline.
- Earlier four-detector CLEAN classifications used heuristic-graph / fallback extraction (after exact extraction failed on missing RAM definitions) — **not proof of Trojan absence**.
- Defensive appendix on 23 labeled designs: combined rule detected **9/14 infected, missed 5, false-flagged 7/9 clean** (64.3% detection, 77.8% false-alarm). Related design families dominate; training overlap unknown, so **not** established as held-out evaluation; labels are directory-derived, not behaviorally proven.

**C. Approval / administrative items:**
- **Professor approval of the alternative defensive scope: pending.** No acceptance may be inferred from silence.
- **Submission not sent/uploaded.** Current course upload destination not verified.
- **Deadline not freshly confirmed.** The **November 13, 2026, 3 PM Eastern** date is a *previously user-recorded* value the orchestrator relays; it is **not** freshly verified instructor confirmation. (~30-hour window relative to today, Nov 11, but treat as unconfirmed.)
- Parent agent is **separately** checking credentials/unrelated private content and publication scope before any upload — must complete first.
- If uploaded while scope is unresolved, include the current partial-label note and **save the submission confirmation separately** (preparation ≠ submission).

**D. Optional items (do not block):**
- Independent key recovery — a **bonus** in the original qualifier; not established, no key claimed.
- Physical-board validation — **not required** by the original simulation-only phase (later course instructions could differ; that is unverified).

---

## 3. Misleading claims / contradictions to correct

The documents are mostly careful and internally arithmetic-consistent (378+1,893 = 2,271 records; detector table rows and the 64.3%/77.8% figures all reconcile). Points to tighten:

- **Do not present Nov 13, 3 PM Eastern as verified.** Keep the docs' "previously recorded / no fresh confirmation" framing everywhere; avoid any wording implying a freshly confirmed deadline or upload destination.
- **Combined-rule framing.** The any-positive-vote combination detects the same 9 infected as HT1 alone while raising false alarms from 5 to 7 — i.e., **no sensitivity gain, worse false-positive rate** on this set. Ensure the brief does not imply the combination improved detection.
- **"Proposed" vs "complete" cipher explanation** (noted in §2A) — align language with the original requirement to avoid an inaccurate gap statement.
- **Integrity-vs-audit wording.** Ensure no reader interprets the copy-receipt/CRC/manifest checks as independent validation of source correctness, test results, or security — they prove only that copied bytes match prior records.
- **Keep the historical unsent professor draft clearly labeled** as historical; route present status only through the current unsent follow-up.

No fabricated approval, logs, tests, keys, or model provenance appear — maintain that.

---

## 4. Private-repository publication boundaries & reproducibility caveats

- **Hold publication/upload until the parent agent's credential and private-content/scope check completes.** I cannot and do not certify absence of credentials or sensitive material.
- Keep **Paper 5 fully separate and excluded** (its own chat/workspace/logs; Nov 16 deadline is unrelated).
- Label any upload **clearly as partial / instructor review**, not completion.
- **Reproducibility is limited by design:** these are portable evidence subsets, not standalone EDA/detector installs. Absolute source paths, shared environments, large solver intermediates, full graphs, detector weights, and toy RTL inputs are not all included; a rerun is not guaranteed without them. No attack artifact should be generated to "fill" the missing RTL/testbench.
- No script auto-runs on open — retain that property; direct reviewers to the per-component reproduction/limitation notes.
- AI exports may contain sensitive content; vet before any wider (non-private) publication.

---

## 5. Plain-language final status

Your package is a solid, honestly-documented **partial submission for instructor review — it is not the finished original assignment.** Two required pieces (the Trojan-modified RTL and its demonstration testbench) are still missing, the write-up doesn't yet cover every required topic, and your AI logs can't be shown to be complete. The defensive detector study is real work but is a *proposed alternative* your professor hasn't approved. The Nov 13, 3 PM deadline is the date you recorded earlier, not a freshly confirmed one, and nothing has been uploaded or accepted. Before any upload: wait for the credential/private-content check, label it clearly as partial, don't present the deadline as verified, and if you do submit, save the confirmation separately. Keep Paper 5 out of this.
